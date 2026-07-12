"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-12

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Products ----------------------------------------------------------
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("slug", sa.String(140), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Admin users -------------------------------------------------------
    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(60), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Scheduling slots --------------------------------------------------
    op.create_table(
        "scheduling_slots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column(
            "fulfillment_type",
            sa.Enum("pickup", "delivery", name="fulfillment_type"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "date", "start_time", "fulfillment_type", name="uq_slot"
        ),
    )
    op.create_index("ix_slots_date", "scheduling_slots", ["date"])

    # Orders ------------------------------------------------------------
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_number", sa.String(40), nullable=False, unique=True),
        sa.Column("public_token", sa.String(64), nullable=False, unique=True),
        sa.Column("customer_name", sa.String(120), nullable=False),
        sa.Column("customer_email", sa.String(180), nullable=False),
        sa.Column("customer_phone", sa.String(32), nullable=False),
        sa.Column("customer_cpf", sa.String(14), nullable=True),
        sa.Column(
            "fulfillment_type",
            sa.Enum("pickup", "delivery", name="order_fulfillment_type"),
            nullable=False,
        ),
        sa.Column("address_json", postgresql.JSONB, nullable=True),
        sa.Column("subtotal_cents", sa.Integer(), nullable=False),
        sa.Column("shipping_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_cents", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending_payment",
                "paid",
                "preparing",
                "ready",
                "delivered",
                "canceled",
                name="order_status",
            ),
            nullable=False,
            server_default="pending_payment",
        ),
        sa.Column(
            "payment_method",
            sa.Enum("pix", "card", name="payment_method"),
            nullable=False,
        ),
        sa.Column(
            "payment_status",
            sa.Enum(
                "pending",
                "paid",
                "failed",
                "refunded",
                name="payment_status",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("payment_provider", sa.String(40), nullable=True),
        sa.Column("provider_charge_id", sa.String(120), nullable=True),
        sa.Column("scheduled_date", sa.Date(), nullable=False),
        sa.Column("slot_id", sa.Integer(), sa.ForeignKey("scheduling_slots.id"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_scheduled_date", "orders", ["scheduled_date"])

    # Order items -------------------------------------------------------
    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("product_name_snapshot", sa.String(120), nullable=False),
        sa.Column("unit_price_cents", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
    )

    # Payment events ----------------------------------------------------
    op.create_table(
        "payment_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "order_id",
            sa.Integer(),
            sa.ForeignKey("orders.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("event_type", sa.String(60), nullable=False),
        sa.Column("external_event_id", sa.String(120), nullable=False, unique=True),
        sa.Column("raw_payload_json", postgresql.JSONB, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Notifications -----------------------------------------------------
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "order_id",
            sa.Integer(),
            sa.ForeignKey("orders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "channel",
            sa.Enum("email", "whatsapp", name="notification_channel"),
            nullable=False,
        ),
        sa.Column("recipient", sa.String(180), nullable=False),
        sa.Column("template_key", sa.String(80), nullable=False),
        sa.Column("rendered_body", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("queued", "sent", "failed", name="notification_status"),
            nullable=False,
            server_default="queued",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("payment_events")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("scheduling_slots")
    op.drop_table("admin_users")
    op.drop_table("products")