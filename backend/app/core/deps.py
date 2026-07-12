"""Dependency injection — wires the right provider based on DEMO_MODE.

This is the **single point** where the choice of payment / notification
provider is made. The rest of the app is agnostic. To add a new provider:
1. Implement the ABC (e.g., PaymentProvider or NotificationProvider).
2. Add a branch here based on config.
3. Register it in the get_*_provider functions below.
4. No other files change.
"""

from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.services.notification.base import NotificationProvider
from app.services.notification.console_email import ConsoleEmailProvider
from app.services.notification.fake_whatsapp import FakeWhatsAppProvider
from app.services.payment.base import PaymentProvider
from app.services.payment.fake_provider import FakePaymentProvider


@lru_cache(maxsize=1)
def get_payment_provider() -> PaymentProvider:
    settings = get_settings()
    if settings.demo_mode:
        return FakePaymentProvider()
    # Fail-fast is already enforced by Settings._enforce_real_mode_credentials
    # — if we reach here, ABACATEPAY_API_KEY and ABACATEPAY_WEBHOOK_SECRET are set.
    from app.services.payment.abacatepay_provider import AbacatePayProvider
    return AbacatePayProvider(
        api_key=settings.abacatepay_api_key,
        webhook_secret=settings.abacatepay_webhook_secret,
    )


@lru_cache(maxsize=1)
def get_email_provider() -> NotificationProvider | None:
    settings = get_settings()
    if settings.demo_mode:
        return ConsoleEmailProvider()
    from app.services.notification.resend_email import ResendEmailProvider
    return ResendEmailProvider(api_key=settings.resend_api_key, from_address=settings.email_from)


@lru_cache(maxsize=1)
def get_whatsapp_provider() -> NotificationProvider:
    # Always fake for now; Meta Cloud API is a documented extension
    return FakeWhatsAppProvider()
