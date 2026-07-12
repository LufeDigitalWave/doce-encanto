"""Fake WhatsApp provider — DEMO_MODE=true default.

Prints to stdout. Meta Cloud API is a documented extension; implementing
it only requires subclassing `NotificationProvider` and registering it
in `app.core.deps`.
"""

from __future__ import annotations

import logging

from app.services.notification.base import NotificationPayload, NotificationProvider


_log = logging.getLogger("notif.fake_whatsapp")


class FakeWhatsAppProvider(NotificationProvider):
    channel = "whatsapp"

    async def send(self, payload: NotificationPayload) -> bool:
        _log.info(
            "\n──── FAKE WHATSAPP ────\n"
            "to: %s\n"
            "%s\n──────────────────────",
            payload.recipient,
            payload.body,
        )
        return True