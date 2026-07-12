"""Pricing rules — covers delivery / pickup / free shipping threshold."""

from __future__ import annotations

import pytest

from app.models import FulfillmentType
from app.services.pricing import (
    FLAT_SHIPPING_CENTS,
    FREE_SHIPPING_THRESHOLD_CENTS,
    compute_pricing,
)


def test_pickup_is_always_free():
    res = compute_pricing(subtotal_cents=100, fulfillment_type=FulfillmentType.PICKUP)
    assert res.shipping_cents == 0
    assert res.total_cents == 100


def test_delivery_flat_fee_below_threshold():
    res = compute_pricing(
        subtotal_cents=FREE_SHIPPING_THRESHOLD_CENTS - 1,
        fulfillment_type=FulfillmentType.DELIVERY,
    )
    assert res.shipping_cents == FLAT_SHIPPING_CENTS
    assert res.total_cents == FREE_SHIPPING_THRESHOLD_CENTS - 1 + FLAT_SHIPPING_CENTS


def test_delivery_free_at_threshold():
    res = compute_pricing(
        subtotal_cents=FREE_SHIPPING_THRESHOLD_CENTS,
        fulfillment_type=FulfillmentType.DELIVERY,
    )
    assert res.shipping_cents == 0
    assert res.total_cents == FREE_SHIPPING_THRESHOLD_CENTS


def test_delivery_free_above_threshold():
    res = compute_pricing(
        subtotal_cents=FREE_SHIPPING_THRESHOLD_CENTS + 5000,
        fulfillment_type=FulfillmentType.DELIVERY,
    )
    assert res.shipping_cents == 0


def test_negative_subtotal_rejected():
    with pytest.raises(ValueError):
        compute_pricing(subtotal_cents=-1, fulfillment_type=FulfillmentType.PICKUP)