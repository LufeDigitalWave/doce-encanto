"""Pricing rules — kept in one place so tests are obvious.

Constants:
  - free shipping threshold: subtotal >= 15000 cents (R$ 150,00)
  - flat delivery fee: 1200 cents (R$ 12,00) when subtotal < threshold
  - pickup: shipping is always 0
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models import FulfillmentType


FREE_SHIPPING_THRESHOLD_CENTS = 15_000  # R$ 150,00
FLAT_SHIPPING_CENTS = 1_200  # R$ 12,00


@dataclass(slots=True, frozen=True)
class PricingResult:
    subtotal_cents: int
    shipping_cents: int
    total_cents: int


def compute_pricing(
    *,
    subtotal_cents: int,
    fulfillment_type: FulfillmentType,
) -> PricingResult:
    if subtotal_cents < 0:
        raise ValueError("subtotal cannot be negative")
    if fulfillment_type is FulfillmentType.PICKUP:
        shipping = 0
    else:  # DELIVERY
        shipping = 0 if subtotal_cents >= FREE_SHIPPING_THRESHOLD_CENTS else FLAT_SHIPPING_CENTS
    return PricingResult(
        subtotal_cents=subtotal_cents,
        shipping_cents=shipping,
        total_cents=subtotal_cents + shipping,
    )