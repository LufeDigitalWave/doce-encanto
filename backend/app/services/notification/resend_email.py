"""Resend email provider — real email via Resend API.

When DEMO_MODE=false and RESEND_API_KEY is set, notifications are sent
via Resend's API (https://resend.com).

Resend handles delivery to inboxes; we only fire-and-forget here.
"""

from __future__ import annotations

import logging

import httpx

from app.services.notification.base import NotificationPayload, NotificationProvider

_log = logging.getLogger("notif.resend")


class ResendEmailProvider(NotificationProvider):
    channel = "email"

    def __init__(self, *, api_key: str, from_address: str) -> None:
        self.api_key = api_key
        self.from_address = from_address

    async def send(self, payload: NotificationPayload) -> bool:
        """POST to Resend API to queue an email.

        Returns True if Resend accepted the request; False if delivery failed.
        """
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "from": self.from_address,
            "to": payload.recipient,
            "subject": payload.subject,
            "html": f"<pre>{payload.body}</pre>",
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=body, headers=headers, timeout=10)
                if resp.status_code >= 400:
                    _log.error(
                        "Resend error %s: %s", resp.status_code, resp.text
                    )
                    return False
                return True
        except Exception as e:
            _log.error("Resend exception: %s", e)
            return False
