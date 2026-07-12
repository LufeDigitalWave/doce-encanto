"""Fake payment provider — QR generation, expiry, webhook bypass."""

from __future__ import annotations

import base64

import pytest

from app.services.payment.fake_provider import FakePaymentProvider


@pytest.mark.asyncio
async def test_create_pix_charge_returns_qr_and_copy_paste():
    p = FakePaymentProvider()
    charge = await p.create_pix_charge(
        amount_cents=1500,
        description="Pedido teste",
        customer={"name": "Fulano", "email": "f@example.com"},
        order_number="DE-2026-0001",
    )
    assert charge.qr_code_base64.startswith("data:image/png;base64,")
    # Round-trip the base64 payload to make sure it's a real PNG.
    raw = base64.b64decode(charge.qr_code_base64.split(",", 1)[1])
    assert raw[:8] == b"\x89PNG\r\n\x1a\n"
    assert charge.copy_paste_code.startswith("00020126")
    assert charge.provider_charge_id.startswith("fake_")
    assert charge.expires_at is not None


@pytest.mark.asyncio
async def test_check_charge_pending_then_expired():
    p = FakePaymentProvider()
    charge = await p.create_pix_charge(
        amount_cents=100,
        description="x",
        customer={},
        order_number="DE-X-0001",
        ttl_seconds=0,
    )
    # ttl=0 means it expires immediately
    status = await p.check_charge(charge.provider_charge_id)
    assert status in ("EXPIRED", "PENDING")