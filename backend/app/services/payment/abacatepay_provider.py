"""AbacatePay real payment provider.

Wraps the official SDK (available at https://github.com/AbacatePay/abacatepay-python-sdk)
but we implement the HTTP calls directly for full control over signature verification and
error handling. Base URL, endpoints, and authentication follow the official SDK contracts.

Docs: https://www.abacatepay.com/llms.txt
SDK: https://github.com/AbacatePay/abacatepay-python-sdk
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.services.payment.base import PaymentProvider, PixCharge

_log = logging.getLogger("payment.abacatepay")

BASE_URL = "https://api.abacatepay.com/v2"
HEADERS = {
    "User-Agent": "DoceEncanto/0.1",
    "Content-Type": "application/json",
}


class AbacatePayProvider(PaymentProvider):
    """Production payment provider using AbacatePay's Pix infrastructure."""

    name = "abacatepay"

    def __init__(self, *, api_key: str, webhook_secret: str) -> None:
        self.api_key = api_key
        self.webhook_secret = webhook_secret

    async def create_pix_charge(
        self,
        *,
        amount_cents: int,
        description: str,
        customer: dict,
        order_number: str,
        ttl_seconds: int = 900,
    ) -> PixCharge:
        """Create a Pix charge via POST /pixQrCode/create.

        Args:
            amount_cents: total in centavos (e.g., 1500 = R$ 15,00)
            description: invoice description
            customer: dict with name, email, cellphone
            order_number: unique identifier for this order (used as txid)
            ttl_seconds: how long the QR is valid (default 15 min)

        Returns:
            PixCharge with qr_code_base64, copy_paste_code, etc.
        """
        payload = {
            "data": {
                "amount": amount_cents,
                "expiresIn": ttl_seconds,
                "description": description,
                "customer": customer if customer else None,
            }
        }
        # Remove None values from data
        payload["data"] = {k: v for k, v in payload["data"].items() if v is not None}

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{BASE_URL}/transparents/create",
                json=payload,
                headers={**HEADERS, "Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            if not resp.is_success:
                _log.error("AbacatePay %s: %s", resp.status_code, resp.text)
            resp.raise_for_status()
            data = resp.json()

        # Response shape from SDK: {data: {id, brCode, brCodeBase64, status, devMode, ...}}
        result = data.get("data", {})
        charge_id = result.get("id")

        if not charge_id:
            raise RuntimeError(
                f"AbacatePay response missing 'id': {json.dumps(result)}"
            )

        expires_at = (
            datetime.fromisoformat(result["expiresAt"].replace("Z", "+00:00"))
            if "expiresAt" in result
            else datetime.now(tz=timezone.utc) + timedelta(seconds=ttl_seconds)
        )

        return PixCharge(
            qr_code_base64=result.get("brCodeBase64", ""),
            copy_paste_code=result.get("brCode", ""),
            provider_charge_id=charge_id,
            expires_at=expires_at,
            raw_response=result,
        )

    async def check_charge(self, provider_charge_id: str) -> str:
        """Check charge status via GET /pixQrCode/check?id=<id>.

        Returns one of: PENDING, PAID, EXPIRED, CANCELED, REFUNDED, FAILED.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{BASE_URL}/transparents/check",
                params={"id": provider_charge_id},
                headers={**HEADERS, "Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

        result = data.get("data", {})
        status = result.get("status", "PENDING")
        return status

    def verify_webhook_signature(
        self, *, raw_body: bytes, signature_header: str
    ) -> bool:
        """Verify HMAC-SHA256 signature from AbacatePay webhook.

        Header: x-webhook-signature (base64-encoded HMAC)
        Algorithm: HMAC-SHA256(secret, raw_body)
        """
        if not signature_header:
            return False
        try:
            expected = base64.b64encode(
                hmac.new(
                    self.webhook_secret.encode("utf-8"),
                    raw_body,
                    hashlib.sha256,
                ).digest()
            ).decode("utf-8")
            return hmac.compare_digest(expected, signature_header)
        except Exception as e:
            _log.error("Signature verification failed: %s", e)
            return False

    def parse_webhook(self, raw_body: bytes) -> dict:
        """Parse and normalize a webhook payload.

        AbacatePay sends events like:
        {
          "id": "evt_...",
          "event": "transparent.completed" | "transparent.paid" | ...,
          "data": {
            "id": "pix_qr_...",
            "status": "PAID" | "PENDING" | ...,
            ...
          }
        }

        Returns a dict: {event_id, event_type, charge_id, status, _raw}
        """
        payload = json.loads(raw_body or b"{}")
        event_id = payload.get("id", "")
        event_type = payload.get("event", "")
        data = payload.get("data", {})
        charge_id = data.get("id", "")
        status = data.get("status", "PENDING")

        return {
            "event_id": event_id,
            "event_type": event_type,
            "charge_id": charge_id,
            "status": status,
            "_raw": payload,
        }
