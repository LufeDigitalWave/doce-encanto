"""Orders API — create orders and query by ID/token."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import get_email_provider, get_whatsapp_provider
from app.schemas import OrderCreate, OrderOut
from app.services import order_service
from app.services.order_service import OrderValidationError
from app.services.scheduling import SlotUnavailableError

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=201)
async def create_order(
    payload: OrderCreate,
    session: AsyncSession = Depends(get_session),
):
    try:
        order = await order_service.create_order(
            session,
            payload,
            email_provider=get_email_provider(),
            whatsapp_provider=get_whatsapp_provider(),
        )
    except OrderValidationError as e:
        raise HTTPException(422, str(e))
    except SlotUnavailableError as e:
        raise HTTPException(409, str(e))
    return order


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, session: AsyncSession = Depends(get_session)):
    order = await order_service.get_order_by_id(session, order_id)
    if order is None:
        raise HTTPException(404, "order not found")
    return order
