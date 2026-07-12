"""Scheduling API — calendar availability per day."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.models import FulfillmentType
from app.schemas import AvailabilityOut, SlotOut
from app.services import scheduling

router = APIRouter(prefix="/api/scheduling", tags=["scheduling"])


@router.get("/availability", response_model=AvailabilityOut)
async def get_availability(
    date_: date = Query(alias="date"),
    fulfillment: FulfillmentType = Query(),
    session: AsyncSession = Depends(get_session),
):
    slots = await scheduling.availability_for(
        session, target_date=date_, fulfillment=fulfillment
    )
    return AvailabilityOut(
        date=date_,
        fulfillment=fulfillment,
        slots=[
            SlotOut(
                id=s.id,
                date=s.date,
                start_time=s.start_time.strftime("%H:%M"),
                end_time=s.end_time.strftime("%H:%M"),
                capacity=s.capacity,
                remaining=s.remaining,
                available=s.available,
            )
            for s in slots
        ],
    )
