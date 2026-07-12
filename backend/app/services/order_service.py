"""Order service — encapsulates the create-order transaction.

Everything that needs to happen atomically when an order is placed lives
here: pricing, slot reservation (with row lock), persistence of items,
snapshotting product names/prices (so later product edits don't mutate
historical orders), and triggering the order_created notification.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import date
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    FulfillmentType,
    Order,
    OrderItem,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
    Product,
)
from app.schemas import CartItemIn, CustomerIn, OrderCreate
from app.services import notification_service, scheduling
from app.services.pricing import compute_pricing
from app.services.notification.base import NotificationProvider


class OrderValidationError(Exception):
    """Raised when the request payload is inconsistent (caller error)."""


def _generate_order_number(seq: int, today: date) -> str:
    return f"DE-{today.year}-{seq:04d}"


async def _next_order_number(session: AsyncSession) -> str:
    """Reads max id and synthesizes DE-YYYY-NNNN. Safe under low write volume;
    on heavy traffic this would move to a Postgres sequence."""
    from sqlalchemy import func

    last_id = (await session.scalar(select(func.coalesce(func.max(Order.id), 0))) ) or 0
    return _generate_order_number(last_id + 1, date.today())


@dataclass(slots=True)
class CreatedOrder:
    order: Order


async def create_order(
    session: AsyncSession,
    payload: OrderCreate,
    *,
    email_provider: NotificationProvider | None = None,
    whatsapp_provider: NotificationProvider | None = None,
) -> Order:
    """Validates payload, reserves the slot, persists the order, fires notifications.

    The function commits the transaction at the end. The caller is responsible
    for any preceding rollback if necessary.
    """
    if payload.fulfillment_type is FulfillmentType.DELIVERY and payload.address is None:
        raise OrderValidationError("address is required for delivery orders")

    products: dict[int, Product] = {}
    product_ids = {it.product_id for it in payload.items}
    rows = await session.scalars(select(Product).where(Product.id.in_(product_ids)))
    for p in rows:
        if not p.is_active:
            raise OrderValidationError(f"product {p.slug} is not available")
        products[p.id] = p

    for it in payload.items:
        if it.product_id not in products:
            raise OrderValidationError(f"product_id {it.product_id} does not exist")

    subtotal = sum(products[it.product_id].price_cents * it.quantity for it in payload.items)
    pricing = compute_pricing(
        subtotal_cents=subtotal, fulfillment_type=payload.fulfillment_type
    )

    # Slot reservation under row lock — concurrent requests cannot overbook.
    slot = await scheduling.reserve_slot(
        session, slot_id=payload.slot_id, target_date=payload.scheduled_date
    )

    order_number = await _next_order_number(session)

    order = Order(
        order_number=order_number,
        customer_name=payload.customer.name.strip(),
        customer_email=str(payload.customer.email).strip().lower(),
        customer_phone=payload.customer.phone,
        customer_cpf=payload.customer.cpf,
        fulfillment_type=payload.fulfillment_type,
        address_json=payload.address.model_dump() if payload.address else None,
        subtotal_cents=pricing.subtotal_cents,
        shipping_cents=pricing.shipping_cents,
        total_cents=pricing.total_cents,
        status=OrderStatus.PENDING_PAYMENT,
        payment_method=PaymentMethod.PIX,
        payment_status=PaymentStatus.PENDING,
        scheduled_date=payload.scheduled_date,
        slot_id=slot.id,
    )
    session.add(order)
    await session.flush()

    for it in payload.items:
        prod = products[it.product_id]
        session.add(
            OrderItem(
                order_id=order.id,
                product_id=prod.id,
                product_name_snapshot=prod.name,
                unit_price_cents=prod.price_cents,
                quantity=it.quantity,
            )
        )

    await session.flush()

    # Notifications are dispatched AFTER the order is persisted and committed,
    # so a partial failure doesn't leave a pending notification with no order.
    await session.commit()
    await session.refresh(order, attribute_names=["items", "slot"])

    await notification_service.emit(
        session,
        order=order,
        template_key="order_created",
        email_provider=email_provider,
        whatsapp_provider=whatsapp_provider,
    )
    await session.commit()
    return order


async def get_order_by_token(session: AsyncSession, token: str) -> Order | None:
    return await session.scalar(
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.slot))
        .where(Order.public_token == token)
    )


async def get_order_by_id(session: AsyncSession, order_id: int) -> Order | None:
    return await session.scalar(
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.slot))
        .where(Order.id == order_id)
    )