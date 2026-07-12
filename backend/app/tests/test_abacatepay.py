"""AbacatePay provider tests — mocked HTTP, no real API calls.

Uses `respx` to intercept httpx requests.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json

import pytest
import respx
from httpx import Response

from app.services.payment.abacatepay_provider import AbacatePayProvider, BASE_URL


API_KEY = "test_key_123"
WEBHOOK_SECRET = "my-webhook-secret"


@pytest.fixture
def provider():
    return AbacatePayProvider(api_key=API_KEY, webhook_secret=WEBHOOK_SECRET)


@respx.mock
@pytest.mark.asyncio
async def test_create_pix_charge(provider):
    mock_response = {
        "data": {
            "id": "pix_char_abc123",
            "amount": 1500,
            "status": "PENDING",
            "devMode": True,
            "brCode": "00020101021226950014br.gov.bcb.pix",
            "brCodeBase64": "data:image/png;base64,iVBORw0KGgoAAA",
            "platformFee": 80,
            "createdAt": "2026-07-12T10:00:00.000Z",
            "updatedAt": "2026-07-12T10:00:00.000Z",
            "expiresAt": "2026-07-12T10:15:00.000Z",
        }
    }
    respx.post(f"{BASE_URL}/pixQrCode/create").mock(
        return_value=Response(200, json=mock_response)
    )

    charge = await provider.create_pix_charge(
        amount_cents=1500,
        description="Teste",
        customer={"name": "Maria", "email": "m@example.com"},
        order_number="DE-2026-0001",
    )

    assert charge.provider_charge_id == "pix_char_abc123"
    assert charge.copy_paste_code == "00020101021226950014br.gov.bcb.pix"
    assert charge.qr_code_base64.startswith("data:image/png;base64,")
    assert charge.expires_at is not None


@respx.mock
@pytest.mark.asyncio
async def test_check_charge(provider):
    mock_response = {"data": {"status": "PAID", "expiresAt": None}}
    respx.get(f"{BASE_URL}/pixQrCode/check").mock(
        return_value=Response(200, json=mock_response)
    )

    status = await provider.check_charge("pix_char_abc123")
    assert status == "PAID"


def test_verify_valid_signature(provider):
    raw = b'{"id":"evt_123","event":"transparent.completed","data":{}}'
    sig = base64.b64encode(
        hmac.new(WEBHOOK_SECRET.encode(), raw, hashlib.sha256).digest()
    ).decode()
    assert provider.verify_webhook_signature(raw_body=raw, signature_header=sig) is True


def test_verify_invalid_signature(provider):
    raw = b'{"id":"evt_123","event":"transparent.completed","data":{}}'
    assert (
        provider.verify_webhook_signature(raw_body=raw, signature_header="bad-sig")
        is False
    )


def test_verify_empty_signature(provider):
    raw = b'{"id":"evt_123"}'
    assert provider.verify_webhook_signature(raw_body=raw, signature_header="") is False


def test_parse_webhook(provider):
    payload = {
        "id": "evt_abc",
        "event": "transparent.completed",
        "apiVersion": 2,
        "devMode": False,
        "data": {
            "id": "pix_char_xyz",
            "status": "PAID",
            "amount": 1500,
        },
    }
    raw = json.dumps(payload).encode()
    parsed = provider.parse_webhook(raw)
    assert parsed["event_id"] == "evt_abc"
    assert parsed["event_type"] == "transparent.completed"
    assert parsed["charge_id"] == "pix_char_xyz"
    assert parsed["status"] == "PAID"
    assert parsed["_raw"] == payload


def test_webhook_idempotency_key_comes_from_event_id(provider):
    """The event_id parsed from the payload is what becomes the DB UNIQUE column."""
    p1 = json.dumps({"id": "evt_same", "event": "x", "data": {"id": "c1", "status": "PAID"}}).encode()
    p2 = json.dumps({"id": "evt_same", "event": "x", "data": {"id": "c1", "status": "PAID"}}).encode()
    r1 = provider.parse_webhook(p1)
    r2 = provider.parse_webhook(p2)
    assert r1["event_id"] == r2["event_id"], "Deterministic for idempotency"
