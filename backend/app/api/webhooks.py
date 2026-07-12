"""Webhook receiver for AbacatePay.

Signature validation + idempotency (UNIQUE external_event_id). Processing
follows the exact same path as `simulate-payment` — update status, fire
notifications.

Only active when DEMO_MODE=false.
"""

from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.core.deps import get_email_provider, get_payment_provider, get_whatsapp_provider
from app.models import (
    Order,
    OrderStatus,
    PaymentEvent,
    PaymentStatus,
)
from app.services import notification_service

_log = logging.getLogger("webhooks.abacatepay")

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/abacatepay")
async def abacatepay_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    settings = get_settings()

    # Read raw body BEFORE any JSON parsing — otherwise HMAC won't match.
    raw_body = await request.body()
    signature = request.headers.get("x-webhook-signature", "")

    provider = get_payment_provider()

    if not provider.verify_webhook_signature(raw_body=raw_body, signature_header=signature):
        _log.warning("Invalid webhook signature")
        raise HTTPException(401, "invalid signature")

    parsed = provider.parse_webhook(raw_body)
    event_id = parsed["event_id"]
    charge_id = parsed["charge_id"]
    status = parsed["status"]  # PAID, EXPIRED, etc.
    event_type = parsed["event_type"]

    # Idempotency — if we already processed this event_id, return 200.
    pe = PaymentEvent(
        order_id=None,
        provider=provider.name,
        event_type=event_type,
        external_event_id=event_id,
        raw_payload_json=parsed.get("_raw", {}),
    )
    session.add(pe)
    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        _log.info("Duplicate event %s — skipping", event_id)
        return {"status": "duplicate"}

    # Find the order by provider_charge_id.
    order = await session.scalar(
        select(Order).where(Order.provider_charge_id == charge_id)
    )
    if order is None:
        _log.warning("No order found for charge %s", charge_id)
        await session.commit()
        return {"status": "no_order"}

    pe.order_id = order.id

    if status == "PAID":
        order.payment_status = PaymentStatus.PAID
        order.status = OrderStatus.PAID
        template_key = "payment_approved"
    elif status in ("EXPIRED", "CANCELED"):
        order.payment_status = PaymentStatus.FAILED
        template_key = "payment_failed"
    elif status == "REFUNDED":
        order.payment_status = PaymentStatus.REFUNDED
        order.status = OrderStatus.CANCELED
        template_key = "payment_failed"
    else:
        await session.commit()
        return {"status": "unhandled", "event_status": status}

    await session.commit()
    await session.refresh(order, attribute_names=["items", "slot"])

    await notification_service.emit(
        session,
        order=order,
        template_key=template_key,
        email_provider=get_email_provider(),
        whatsapp_provider=get_whatsapp_provider(),
    )
    await session.commit()

    return {"status": "processed", "order_id": order.id}
