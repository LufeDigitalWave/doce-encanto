"""Console email provider — DEMO_MODE=true default.

Does NOT actually send. Prints to stdout and returns success. The
notification row in `notifications` is what the admin outbox displays.
"""

from __future__ import annotations

import logging

from app.services.notification.base import NotificationPayload, NotificationProvider


_log = logging.getLogger("notif.console_email")


class ConsoleEmailProvider(NotificationProvider):
    channel = "email"

    async def send(self, payload: NotificationPayload) -> bool:
        _log.info(
            "\n──── CONSOLE EMAIL ────\n"
            "to: %s\n"
            "subject: %s\n"
            "%s\n──────────────────────",
            payload.recipient,
            payload.subject,
            payload.body,
        )
        return True