"""Payment API — create PIX charge and check status.

The frontend only knows two endpoints:
  POST /api/orders/{id}/pay  -> {qr_code_base64, copy_paste_code, expires_at}
  GET  /api/orders/{id}/payment-status -> {status}
  POST /api/orders/{id}/simulate-payment (DEMO_MODE only)

It doesn't know which provider backs them.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.core.deps import get_email_provider, get_payment_provider, get_whatsapp_provider
from app.models import OrderStatus, PaymentStatus
from app.schemas import PaymentChargeOut, PaymentStatusOut
from app.services import notification_service, order_service
from app.services.payment.base import PaymentProvider
from app.services.payment.fake_provider import FakePaymentProvider

router = APIRouter(prefix="/api/orders", tags=["payments"])


@router.post("/{order_id}/pay", response_model=PaymentChargeOut)
async def create_pix_charge(
    order_id: int,
    session: AsyncSession = Depends(get_session),
):
    order = await order_service.get_order_by_id(session, order_id)
    if order is None:
        raise HTTPException(404, "order not found")
    if order.payment_status != PaymentStatus.PENDING:
        raise HTTPException(409, f"order already {order.payment_status.value}")

    provider: PaymentProvider = get_payment_provider()
    charge = await provider.create_pix_charge(
        amount_cents=order.total_cents,
        description=f"Doce Encanto #{order.order_number}",
        customer={
            "name": order.customer_name,
            "email": order.customer_email,
            "cellphone": order.customer_phone,
            "taxId": order.customer_cpf or "",
        },
        order_number=order.order_number,
    )
    order.provider_charge_id = charge.provider_charge_id
    order.payment_provider = provider.name
    await session.commit()

    # In real mode, copy_paste_code contains the checkout URL
    checkout_url = None
    if not get_settings().demo_mode and charge.copy_paste_code.startswith("http"):
        checkout_url = charge.copy_paste_code

    return PaymentChargeOut(
        qr_code_base64=charge.qr_code_base64,
        copy_paste_code=charge.copy_paste_code,
        checkout_url=checkout_url,
        expires_at=charge.expires_at,
        demo_mode=get_settings().demo_mode,
    )


@router.get("/{order_id}/payment-status", response_model=PaymentStatusOut)
async def check_payment_status(
    order_id: int,
    session: AsyncSession = Depends(get_session),
):
    order = await order_service.get_order_by_id(session, order_id)
    if order is None:
        raise HTTPException(404)
    return PaymentStatusOut(
        status=order.payment_status,
        order_status=order.status,
        provider=order.payment_provider,
    )


@router.post("/{order_id}/simulate-payment")
async def simulate_payment(
    order_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Only responds in DEMO_MODE=true. Simulates a payment approval so the
    demo flow can proceed without real money."""
    settings = get_settings()
    if not settings.demo_mode:
        raise HTTPException(404)  # endpoint doesn't exist in production mode

    order = await order_service.get_order_by_id(session, order_id)
    if order is None:
        raise HTTPException(404)
    if order.payment_status != PaymentStatus.PENDING:
        raise HTTPException(409, f"already {order.payment_status.value}")

    provider = get_payment_provider()
    if isinstance(provider, FakePaymentProvider):
        provider.simulate_payment(order.provider_charge_id or "")

    # Mark as paid (same path as the webhook flow)
    order.payment_status = PaymentStatus.PAID
    order.status = OrderStatus.PAID
    await session.commit()
    await session.refresh(order, attribute_names=["items", "slot"])

    await notification_service.emit(
        session,
        order=order,
        template_key="payment_approved",
        email_provider=get_email_provider(),
        whatsapp_provider=get_whatsapp_provider(),
    )
    await session.commit()

    return {"status": "paid", "order_number": order.order_number}
