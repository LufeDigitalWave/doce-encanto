"""Scheduling service tests — capacity, lead time, availability."""

from __future__ import annotations

import asyncio
from datetime import date, datetime, time, timedelta, timezone

import pytest
from sqlalchemy import select

from app.models import (
    FulfillmentType,
    Order,
    OrderStatus,
    SchedulingSlot,
)
from app.services import scheduling
from app.services.scheduling import (
    earliest_booking_date,
    is_lead_time_ok,
    remaining_capacity,
    reserve_slot,
)


@pytest.mark.asyncio
async def test_lead_time_blocks_today(session):
    today = date.today()
    assert not is_lead_time_ok(today)
    assert earliest_booking_date() > today


@pytest.mark.asyncio
async def test_availability_filters_past_lead_time(session):
    slot = SchedulingSlot(
        date=date.today(),
        start_time=time(10, 0),
        end_time=time(12, 0),
        capacity=3,
        fulfillment_type=FulfillmentType.PICKUP,
    )
    session.add(slot)
    await session.commit()

    out = await scheduling.availability_for(
        session, target_date=date.today(), fulfillment=FulfillmentType.PICKUP
    )
    assert out == []


@pytest.mark.asyncio
async def test_capacity_decrements_after_reserve(session):
    far_date = date.today() + timedelta(days=3)
    slot = SchedulingSlot(
        date=far_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        capacity=2,
        fulfillment_type=FulfillmentType.PICKUP,
    )
    session.add(slot)
    await session.commit()

    assert await remaining_capacity(session, slot.id) == 2

    s = await reserve_slot(session, slot.id, far_date)
    assert s.id == slot.id

    # Insert an order occupying this slot to simulate a real reservation.
    order = Order(
        order_number="DE-T-0001",
        customer_name="Test",
        customer_email="t@example.com",
        customer_phone="11999990000",
        fulfillment_type=FulfillmentType.PICKUP,
        address_json=None,
        subtotal_cents=1000,
        shipping_cents=0,
        total_cents=1000,
        status=OrderStatus.PAID,
        payment_method="pix",  # type: ignore[arg-type]
        payment_status="paid",  # type: ignore[arg-type]
        scheduled_date=far_date,
        slot_id=slot.id,
    )
    session.add(order)
    await session.commit()

    assert await remaining_capacity(session, slot.id) == 1


@pytest.mark.asyncio
async def test_slot_full_blocks_new_reservation(session):
    far_date = date.today() + timedelta(days=3)
    slot = SchedulingSlot(
        date=far_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        capacity=1,
        fulfillment_type=FulfillmentType.PICKUP,
    )
    session.add(slot)
    await session.commit()

    # Fill the slot.
    order = Order(
        order_number="DE-T-0001",
        customer_name="T",
        customer_email="t@example.com",
        customer_phone="11999990000",
        fulfillment_type=FulfillmentType.PICKUP,
        address_json=None,
        subtotal_cents=1000,
        shipping_cents=0,
        total_cents=1000,
        status=OrderStatus.PAID,
        payment_method="pix",  # type: ignore[arg-type]
        payment_status="paid",  # type: ignore[arg-type]
        scheduled_date=far_date,
        slot_id=slot.id,
    )
    session.add(order)
    await session.commit()

    with pytest.raises(scheduling.SlotUnavailableError):
        await reserve_slot(session, slot.id, far_date)


@pytest.mark.asyncio
async def test_concurrent_reservation_does_not_overbook(session):
    """Two concurrent reserve_slot() calls on a capacity-1 slot: exactly one wins."""
    far_date = date.today() + timedelta(days=3)
    slot = SchedulingSlot(
        date=far_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        capacity=1,
        fulfillment_type=FulfillmentType.PICKUP,
    )
    session.add(slot)
    await session.commit()

    async def attempt():
        # Each attempt must use its own session bound to the same engine.
        from app.core.db import SessionLocal

        async with SessionLocal() as s:
            try:
                await reserve_slot(s, slot.id, far_date)
                await s.commit()
                return True
            except scheduling.SlotUnavailableError:
                await s.rollback()
                return False

    results = await asyncio.gather(attempt(), attempt())
    assert sum(results) == 1, f"expected 1 success, got {results}"