"""Public order tracking by public_token."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.schemas import OrderOut
from app.services import order_service

router = APIRouter(prefix="/api/tracking", tags=["tracking"])


@router.get("/{public_token}", response_model=OrderOut)
async def track_order(
    public_token: str,
    session: AsyncSession = Depends(get_session),
):
    order = await order_service.get_order_by_token(session, public_token)
    if order is None:
        raise HTTPException(404, "order not found")
    return order
