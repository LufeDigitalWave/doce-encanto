"""Notification provider interface — abstract over email and WhatsApp."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class NotificationPayload:
    recipient: str         # email address or phone number
    subject: str
    body: str              # rendered template (already substituted)


class NotificationProvider(ABC):
    """One implementation per channel. Multiple providers may run concurrently."""

    channel: str = "abstract"

    @abstractmethod
    async def send(self, payload: NotificationPayload) -> bool:
        """Returns True if delivery succeeded (or was simulated)."""


class NotificationError(Exception):
    """Raised when a provider refuses to deliver (e.g. invalid email)."""