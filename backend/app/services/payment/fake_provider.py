"""Fake payment provider for DEMO_MODE=true.

Generates a local QR code image and a copy-paste string that won't work at
any real bank, plus a `simulate-payment` admin endpoint that flips the order
to PAID. The contract mirrors `PaymentProvider` 1:1 so business code is
identical between modes.
"""

from __future__ import annotations

import base64
import io
import json
import secrets
from datetime import datetime, timedelta, timezone

import qrcode

from app.services.payment.base import PaymentProvider, PixCharge


class FakePaymentProvider(PaymentProvider):
    name = "fake"

    def __init__(self) -> None:
        # Idempotency: charge_id -> expiry. Persisted only in memory; restarting
        # the API resets the fake state, which is fine for demo.
        self._charges: dict[str, datetime] = {}

    async def create_pix_charge(
        self,
        *,
        amount_cents: int,
        description: str,
        customer: dict,
        order_number: str,
        ttl_seconds: int = 900,
    ) -> PixCharge:
        charge_id = f"fake_{secrets.token_hex(8)}"
        expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=ttl_seconds)
        self._charges[charge_id] = expires_at

        copy_paste = self._build_copy_paste(
            amount_cents=amount_cents,
            txid=charge_id,
            merchant="DOCE ENCANTO",
            city="SAO PAULO",
        )
        img = qrcode.make(copy_paste)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        qr_b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

        return PixCharge(
            qr_code_base64=qr_b64,
            copy_paste_code=copy_paste,
            provider_charge_id=charge_id,
            expires_at=expires_at,
            raw_response={
                "demo": True,
                "amount_cents": amount_cents,
                "description": description,
                "customer": customer,
                "order_number": order_number,
                "txid": charge_id,
                "expires_at": expires_at.isoformat(),
            },
        )

    async def check_charge(self, provider_charge_id: str) -> str:
        expires = self._charges.get(provider_charge_id)
        if expires is None:
            return "PENDING"
        if datetime.now(tz=timezone.utc) >= expires:
            return "EXPIRED"
        return "PENDING"

    def simulate_payment(self, provider_charge_id: str) -> None:
        """Admin-triggered flip to PAID — used by Roteiro A demo button."""
        if provider_charge_id in self._charges:
            del self._charges[provider_charge_id]

    # Webhooks are not used in fake mode — the simulate endpoint replaces them.
    def verify_webhook_signature(self, *, raw_body: bytes, signature_header: str) -> bool:
        return True

    def parse_webhook(self, raw_body: bytes) -> dict:
        return {
            "event_id": f"fake_{secrets.token_hex(8)}",
            "event_type": "transparent.completed",
            "charge_id": "",
            "status": "PAID",
            "_raw": json.loads(raw_body or b"{}"),
        }

    # ---- helpers ----------------------------------------------------------

    @staticmethod
    def _build_copy_paste(*, amount_cents: int, txid: str, merchant: str, city: str) -> str:
        """A fake BR Code that looks plausible in a Pix reader but is NOT payable.

        Real EMV/BR Code construction is out of scope; this is intentionally
        invalid so no one accidentally scans it for real money.
        """
        return (
            "00020126580014br.gov.bcb.pix0114+5511999990000"
            f"520400005303986540{amount_cents / 100:.2f}"
            f"5802BR5913{merchant}6009{city}62"
            f"05{len(txid):02d}{txid}6304ABCD"
        )