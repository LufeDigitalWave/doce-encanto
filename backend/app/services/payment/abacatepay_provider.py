"""AbacatePay real payment provider — V2 Checkout API.

Uses the hosted checkout flow:
1. Backend creates a product (if not cached) + checkout
2. Frontend redirects customer to AbacatePay's hosted page
3. Customer pays Pix there
4. AbacatePay sends webhook → backend updates order

Docs: https://docs.abacatepay.com/pages/payment/create
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
    """Production payment provider using AbacatePay's hosted checkout."""

    name = "abacatepay"

    def __init__(self, *, api_key: str, webhook_secret: str) -> None:
        self.api_key = api_key
        self.webhook_secret = webhook_secret
        self._product_cache: dict[str, str] = {}  # external_id -> product_id

    async def _ensure_product(self, *, name: str, price_cents: int, external_id: str) -> str:
        """Create or retrieve a product on AbacatePay. Returns product ID."""
        if external_id in self._product_cache:
            return self._product_cache[external_id]

        async with httpx.AsyncClient() as client:
            # Try to find existing product
            resp = await client.get(
                f"{BASE_URL}/products/list",
                headers={**HEADERS, "Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            if resp.is_success:
                products = resp.json().get("data", [])
                for p in products:
                    if p.get("externalId") == external_id:
                        self._product_cache[external_id] = p["id"]
                        return p["id"]

            # Create new product
            resp = await client.post(
                f"{BASE_URL}/products/create",
                json={
                    "externalId": external_id,
                    "name": name,
                    "price": price_cents,
                    "currency": "BRL",
                    "description": name,
                },
                headers={**HEADERS, "Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            if not resp.is_success:
                _log.error("Failed to create product: %s %s", resp.status_code, resp.text)
                resp.raise_for_status()

            product_id = resp.json()["data"]["id"]
            self._product_cache[external_id] = product_id
            return product_id

    async def _ensure_customer(self, customer: dict) -> str | None:
        """Create or find a customer on AbacatePay. Returns customer ID or None."""
        if not customer or not customer.get("email"):
            return None
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{BASE_URL}/customers/create",
                    json={
                        "email": customer.get("email", ""),
                        "name": customer.get("name", ""),
                        "cellphone": customer.get("cellphone", ""),
                        "taxId": customer.get("taxId", customer.get("cpf", "")),
                    },
                    headers={**HEADERS, "Authorization": f"Bearer {self.api_key}"},
                    timeout=10,
                )
                if resp.is_success:
                    return resp.json().get("data", {}).get("id")
                _log.warning("Customer create failed: %s", resp.text)
                return None
        except Exception as e:
            _log.warning("Customer create exception: %s", e)
            return None

    async def create_pix_charge(
        self,
        *,
        amount_cents: int,
        description: str,
        customer: dict,
        order_number: str,
        ttl_seconds: int = 900,
    ) -> PixCharge:
        """Create a hosted checkout on AbacatePay.

        Returns a PixCharge where:
        - qr_code_base64 = "" (QR is on AbacatePay's hosted page)
        - copy_paste_code = the checkout URL (customer is redirected here)
        - provider_charge_id = bill_... ID
        """
        from app.core.config import get_settings
        settings = get_settings()

        # Ensure product exists
        product_id = await self._ensure_product(
            name=description,
            price_cents=amount_cents,
            external_id=order_number,
        )

        # Create or find customer so AbacatePay pre-fills the form
        customer_id = await self._ensure_customer(customer)

        # Create checkout
        payload = {
            "items": [{"id": product_id, "quantity": 1}],
            "methods": ["PIX"],
            "externalId": order_number,
            "completionUrl": f"{settings.public_base_url}/pedido/done",
            "returnUrl": f"{settings.public_base_url}/checkout",
        }
        if customer_id:
            payload["customerId"] = customer_id

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{BASE_URL}/checkouts/create",
                json=payload,
                headers={**HEADERS, "Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            if not resp.is_success:
                _log.error("AbacatePay checkout error %s: %s", resp.status_code, resp.text)
            resp.raise_for_status()
            data = resp.json()

        result = data.get("data", {})
        charge_id = result.get("id", "")
        checkout_url = result.get("url", "")

        if not charge_id:
            raise RuntimeError(
                f"AbacatePay response missing 'id': {json.dumps(result)}"
            )

        return PixCharge(
            qr_code_base64="",  # QR is on AbacatePay's hosted page
            copy_paste_code=checkout_url,  # This IS the checkout URL
            provider_charge_id=charge_id,
            expires_at=datetime.now(tz=timezone.utc) + timedelta(seconds=ttl_seconds),
            raw_response=result,
        )

    async def check_charge(self, provider_charge_id: str) -> str:
        """Check checkout status. Returns PENDING, PAID, EXPIRED, etc."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{BASE_URL}/checkouts/list",
                headers={**HEADERS, "Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            if not resp.is_success:
                return "PENDING"
            data = resp.json()

        for checkout in data.get("data", []):
            if checkout.get("id") == provider_charge_id:
                status = checkout.get("status", "PENDING")
                # Map AbacatePay statuses to our internal ones
                if status == "COMPLETED":
                    return "PAID"
                return status
        return "PENDING"

    def verify_webhook_signature(
        self, *, raw_body: bytes, signature_header: str
    ) -> bool:
        """Verify HMAC-SHA256 signature from AbacatePay webhook.

        Header: X-Webhook-Signature (base64-encoded HMAC)
        Algorithm: HMAC-SHA256(webhook_secret, raw_body)
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
        """Parse AbacatePay V2 webhook payload.

        Format:
        {
          "id": "log_abc123",
          "event": "checkout.completed",
          "apiVersion": 2,
          "devMode": true,
          "data": {
            "id": "bill_...",
            "status": "COMPLETED",
            ...
          }
        }
        """
        payload = json.loads(raw_body or b"{}")
        event_id = payload.get("id", "")
        event_type = payload.get("event", "")
        data = payload.get("data", {})
        charge_id = data.get("id", "")
        status = data.get("status", "PENDING")

        # Map AbacatePay status to our internal
        if status == "COMPLETED" or event_type == "checkout.completed":
            status = "PAID"

        return {
            "event_id": event_id,
            "event_type": event_type,
            "charge_id": charge_id,
            "status": status,
            "_raw": payload,
        }
