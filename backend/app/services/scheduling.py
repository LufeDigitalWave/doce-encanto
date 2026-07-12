"""Scheduling service — calendar of pickup/delivery slots with capacity control.

The calendar UI hits `availability_for(date, fulfillment)` to render the
time grid. The booking flow calls `reserve_slot(slot_id)` inside the order
creation transaction; capacity is enforced with a row-level lock
(`SELECT ... FOR UPDATE`) so concurrent requests cannot overbook.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import FulfillmentType, OrderStatus, SchedulingSlot


class SlotUnavailableError(Exception):
    """Raised when the requested slot is full or past the lead time."""


@dataclass(slots=True)
class SlotView:
    id: int
    date: date
    start_time: time
    end_time: time
    capacity: int
    remaining: int

    @property
    def available(self) -> bool:
        return self.remaining > 0

    @property
    def label(self) -> str:
        return f"{self.start_time.strftime('%H:%M')}–{self.end_time.strftime('%H:%M')}"


def earliest_booking_date(now: datetime | None = None) -> date:
    """Min allowed `scheduled_date` based on MIN_LEAD_TIME_HOURS."""
    settings = get_settings()
    now = now or datetime.now(tz=timezone.utc)
    return (now + timedelta(hours=settings.min_lead_time_hours)).date()


def is_lead_time_ok(target: date, now: datetime | None = None) -> bool:
    return target >= earliest_booking_date(now)


def _booked_count_query(slot_id: int):
    return select(OrderStatus).where(OrderStatus != OrderStatus.CANCELED)


async def remaining_capacity(session: AsyncSession, slot_id: int) -> int:
    """How many orders have already reserved this slot (excluding canceled)."""
    from app.models import Order  # local to avoid cycle

    slot = await session.get(SchedulingSlot, slot_id)
    if slot is None:
        raise SlotUnavailableError(f"slot {slot_id} does not exist")
    booked = await session.scalar(
        select(Order.id).where(
            Order.slot_id == slot_id, Order.status != OrderStatus.CANCELED
        )
    )
    # NB: above returns one id, but we need count — replace with a count() below.
    from sqlalchemy import func

    count = await session.scalar(
        select(func.count(Order.id)).where(
            Order.slot_id == slot_id, Order.status != OrderStatus.CANCELED
        )
    )
    return max(slot.capacity - (count or 0), 0)


async def availability_for(
    session: AsyncSession,
    *,
    target_date: date,
    fulfillment: FulfillmentType,
) -> list[SlotView]:
    if not is_lead_time_ok(target_date):
        return []

    slots: Iterable[SchedulingSlot] = (
        await session.scalars(
            select(SchedulingSlot)
            .where(
                SchedulingSlot.date == target_date,
                SchedulingSlot.fulfillment_type == fulfillment,
            )
            .order_by(SchedulingSlot.start_time)
        )
    ).all()

    out: list[SlotView] = []
    for s in slots:
        remaining = await remaining_capacity(session, s.id)
        out.append(
            SlotView(
                id=s.id,
                date=s.date,
                start_time=s.start_time,
                end_time=s.end_time,
                capacity=s.capacity,
                remaining=remaining,
            )
        )
    return out


async def reserve_slot(session: AsyncSession, slot_id: int, target_date: date) -> SchedulingSlot:
    """Lock the slot row, re-check capacity inside the transaction.

    MUST be called within the same transaction as the Order insert; otherwise
    capacity guarantees are lost.
    """
    if not is_lead_time_ok(target_date):
        raise SlotUnavailableError(
            f"scheduled_date {target_date} violates MIN_LEAD_TIME_HOURS"
        )
    slot = (
        await session.scalar(
            select(SchedulingSlot)
            .where(SchedulingSlot.id == slot_id)
            .with_for_update()
        )
    )
    if slot is None:
        raise SlotUnavailableError(f"slot {slot_id} does not exist")
    if slot.date != target_date or slot.fulfillment_type not in (
        FulfillmentType.PICKUP,
        FulfillmentType.DELIVERY,
    ):
        raise SlotUnavailableError("slot does not match requested date/fulfillment")

    remaining = await remaining_capacity(session, slot.id)
    if remaining <= 0:
        raise SlotUnavailableError(f"slot {slot_id} is full")
    return slot