"""Payment provider interface — ABC for both fake and real implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class PixCharge:
    qr_code_base64: str          # data:image/png;base64,...
    copy_paste_code: str         # BR Code (Pix copia-e-cola)
    provider_charge_id: str      # used to check status / cancel
    expires_at: datetime | None
    raw_response: dict           # opaque provider payload for debugging


class PaymentProvider(ABC):
    """Implementations: `FakePaymentProvider`, `AbacatePayProvider`.

    A new gateway is added by writing a subclass and registering it in
    `app.core.deps.get_payment_provider`.
    """

    name: str = "abstract"

    @abstractmethod
    async def create_pix_charge(
        self,
        *,
        amount_cents: int,
        description: str,
        customer: dict,
        order_number: str,
        ttl_seconds: int = 900,
    ) -> PixCharge: ...

    @abstractmethod
    async def check_charge(self, provider_charge_id: str) -> str:
        """Return one of: PENDING, PAID, EXPIRED, CANCELED, REFUNDED, FAILED."""
        ...

    @abstractmethod
    def verify_webhook_signature(self, *, raw_body: bytes, signature_header: str) -> bool: ...

    @abstractmethod
    def parse_webhook(self, raw_body: bytes) -> dict:
        """Returns a normalized dict: {event_id, event_type, charge_id, status}."""
        ...