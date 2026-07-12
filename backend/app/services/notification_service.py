"""Notification service — template rendering + persistence + dispatch.

Every event creates a `notifications` row BEFORE the provider is called,
so the admin outbox shows the rendered payload regardless of whether the
provider succeeded. This is the critical guarantee that makes the demo
useful even when DEMO_MODE=true.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Notification,
    NotificationChannel,
    NotificationStatus,
    Order,
)
from app.services.notification.base import NotificationPayload, NotificationProvider


# Templates are intentionally simple string.Template-style — no Jinja in the
# hot path. Keep them short, friendly, and editable.
TEMPLATES: dict[str, dict[str, str]] = {
    "order_created": {
        "subject": "Recebemos seu pedido! 🧁",
        "email_body": (
            "Oi {first_name}!\n\n"
            "Recebemos seu pedido {order_number}. Estamos aguardando a confirmação "
            "do pagamento Pix para começar a preparar tudo com carinho.\n\n"
            "Total: {total_brl}\n"
            "Agendado para: {scheduled_date} ({slot_label}).\n\n"
            "Qualquer dúvida é só responder este e-mail.\n\n"
            "Beijo doce,\nEquipe Doce Encanto"
        ),
        "whatsapp_body": (
            "Oi {first_name}! 👋\n"
            "Recebemos seu pedido *{order_number}* na Doce Encanto 🧁\n"
            "Total: *{total_brl}*\n"
            "Retirada/entrega: *{scheduled_date}* às *{slot_label}*.\n"
            "Vamos te chamar aqui assim que o pagamento confirmar 💛"
        ),
    },
    "payment_approved": {
        "subject": "Pagamento confirmado! ✅",
        "email_body": (
            "Oi {first_name}!\n\n"
            "O pagamento do pedido {order_number} foi confirmado. "
            "Já começamos a separar tudo para {scheduled_date} ({slot_label}).\n\n"
            "Qualquer novidade avisaremos por aqui.\n\n"
            "Até logo!\nEquipe Doce Encanto"
        ),
        "whatsapp_body": (
            "{first_name}, pagamento confirmado! ✅\n"
            "Pedido *{order_number}* já está com a gente.\n"
            "Pode deixar que cuidamos de tudo para *{scheduled_date}* ({slot_label}). 🧁"
        ),
    },
    "payment_failed": {
        "subject": "Não recebemos o pagamento do seu pedido",
        "email_body": (
            "Oi {first_name},\n\n"
            "Tivemos um problema com o pagamento do pedido {order_number}. "
            "Tente gerar o QR Code novamente — se persistir, responde este e-mail.\n\n"
            "Equipe Doce Encanto"
        ),
        "whatsapp_body": (
            "{first_name}, o pagamento do pedido *{order_number}* não caiu. "
            "Gera o Pix de novo pelo nosso site, por favor 🙏"
        ),
    },
    "order_status_changed": {
        "subject": "Atualização do seu pedido 📦",
        "email_body": (
            "Oi {first_name}!\n\n"
            "Seu pedido {order_number} agora está: {status_label}.\n"
            "Agendado para {scheduled_date} ({slot_label}).\n\n"
            "Beijo,\nEquipe Doce Encanto"
        ),
        "whatsapp_body": (
            "📦 Pedido *{order_number}*: agora está *{status_label}*.\n"
            "Te vemos em *{scheduled_date}* ({slot_label})! 🧁"
        ),
    },
    "scheduling_reminder": {
        "subject": "Lembrete: seu pedido é amanhã! 🧁",
        "email_body": (
            "Oi {first_name}!\n\n"
            "Passando para lembrar que seu pedido {order_number} está agendado "
            "para amanhã, {scheduled_date} ({slot_label}).\n\n"
            "Vai dar tudo certo!\nEquipe Doce Encanto"
        ),
        "whatsapp_body": (
            "Oi {first_name}! 👋 Lembrete: amanhã, *{scheduled_date}* ({slot_label}), "
            "é dia do seu pedido *{order_number}*. 🧁 Nos vemos!"
        ),
    },
}


@dataclass(slots=True)
class RenderContext:
    order: Order
    customer_first_name: str
    total_brl: str
    scheduled_date: str
    slot_label: str
    status_label: str = ""


def _format_brl(cents: int) -> str:
    reais = cents / 100
    return f"R$ {reais:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _slot_label(start: time, end: time) -> str:
    return f"{start.strftime('%H:%M')}–{end.strftime('%H:%M')}"


def build_context(order: Order) -> RenderContext:
    return RenderContext(
        order=order,
        customer_first_name=order.customer_name.split()[0],
        total_brl=_format_brl(order.total_cents),
        scheduled_date=order.scheduled_date.strftime("%d/%m/%Y"),
        slot_label=_slot_label(order.slot.start_time, order.slot.end_time),
    )


def render(template_key: str, ctx: RenderContext, channel: NotificationChannel) -> tuple[str, str]:
    """Returns (subject, body). For whatsapp, subject is empty."""
    if template_key not in TEMPLATES:
        raise KeyError(f"unknown template {template_key!r}")
    tpl = TEMPLATES[template_key]
    body_kind = "whatsapp_body" if channel is NotificationChannel.WHATSAPP else "email_body"
    body = tpl[body_kind].format(
        first_name=ctx.customer_first_name,
        order_number=ctx.order.order_number,
        total_brl=ctx.total_brl,
        scheduled_date=ctx.scheduled_date,
        slot_label=ctx.slot_label,
        status_label=ctx.status_label,
    )
    subject = tpl["subject"] if channel is NotificationChannel.EMAIL else ""
    return subject, body


async def emit(
    session: AsyncSession,
    *,
    order: Order,
    template_key: str,
    email_provider: NotificationProvider | None = None,
    whatsapp_provider: NotificationProvider | None = None,
    extra_status_label: str = "",
) -> list[Notification]:
    """Render + persist + dispatch a notification event.

    Always creates the rows, then attempts delivery via whichever providers
    are wired in. The outbox (admin UI) sees the rendered body regardless.
    """
    ctx = build_context(order)
    if extra_status_label:
        ctx.status_label = extra_status_label
    rows: list[Notification] = []

    if email_provider is not None:
        subject, body = render(template_key, ctx, NotificationChannel.EMAIL)
        n = Notification(
            order_id=order.id,
            channel=NotificationChannel.EMAIL,
            recipient=order.customer_email,
            template_key=template_key,
            rendered_body=f"Assunto: {subject}\n\n{body}",
            status=NotificationStatus.QUEUED,
        )
        session.add(n)
        await session.flush()
        try:
            ok = await email_provider.send(
                NotificationPayload(recipient=order.customer_email, subject=subject, body=body)
            )
            n.status = NotificationStatus.SENT if ok else NotificationStatus.FAILED
        except Exception:  # noqa: BLE001 — provider failure must not crash order flow
            n.status = NotificationStatus.FAILED
        rows.append(n)

    if whatsapp_provider is not None:
        _, body = render(template_key, ctx, NotificationChannel.WHATSAPP)
        n = Notification(
            order_id=order.id,
            channel=NotificationChannel.WHATSAPP,
            recipient=order.customer_phone,
            template_key=template_key,
            rendered_body=body,
            status=NotificationStatus.QUEUED,
        )
        session.add(n)
        await session.flush()
        try:
            ok = await whatsapp_provider.send(
                NotificationPayload(recipient=order.customer_phone, subject="", body=body)
            )
            n.status = NotificationStatus.SENT if ok else NotificationStatus.FAILED
        except Exception:  # noqa: BLE001
            n.status = NotificationStatus.FAILED
        rows.append(n)

    return rows