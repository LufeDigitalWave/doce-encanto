"""Pydantic v2 schemas for API I/O."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import (
    FulfillmentType,
    NotificationChannel,
    NotificationStatus,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
)


# ----- Products ----------------------------------------------------------


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str
    price_cents: int
    image_url: str | None
    is_active: bool


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = ""
    price_cents: int = Field(ge=0)
    image_url: str | None = None
    is_active: bool = True
    sort_order: int = 0


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price_cents: int | None = Field(default=None, ge=0)
    image_url: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None


# ----- Scheduling --------------------------------------------------------


class SlotOut(BaseModel):
    id: int
    date: date
    start_time: str
    end_time: str
    capacity: int
    remaining: int
    available: bool


class AvailabilityOut(BaseModel):
    date: date
    fulfillment: FulfillmentType
    slots: list[SlotOut]


# ----- Cart / Order input -----------------------------------------------


class CartItemIn(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=99)


class CustomerIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=8, max_length=32)
    cpf: str | None = Field(default=None, min_length=11, max_length=14)

    @field_validator("phone")
    @classmethod
    def _strip_phone(cls, v: str) -> str:
        return "".join(ch for ch in v if ch.isdigit() or ch == "+")


class AddressIn(BaseModel):
    cep: str
    street: str
    number: str
    complement: str | None = ""
    neighborhood: str
    city: str = "São Paulo"
    state: str = "SP"


class OrderCreate(BaseModel):
    items: list[CartItemIn] = Field(min_length=1)
    customer: CustomerIn
    fulfillment_type: FulfillmentType
    address: AddressIn | None = None
    scheduled_date: date
    slot_id: int
    payment_method: Literal[PaymentMethod.PIX] = PaymentMethod.PIX


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name_snapshot: str
    unit_price_cents: int
    quantity: int


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    public_token: str
    customer_name: str
    customer_email: str
    customer_phone: str
    fulfillment_type: FulfillmentType
    address_json: dict[str, Any] | None
    subtotal_cents: int
    shipping_cents: int
    total_cents: int
    status: OrderStatus
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    scheduled_date: date
    slot_id: int
    created_at: datetime
    items: list[OrderItemOut]


# ----- Payment -----------------------------------------------------------


class PaymentChargeOut(BaseModel):
    qr_code_base64: str
    copy_paste_code: str
    expires_at: datetime | None = None
    demo_mode: bool


class PaymentStatusOut(BaseModel):
    status: PaymentStatus
    order_status: OrderStatus
    provider: str | None
    paid_at: datetime | None = None


# ----- Admin -------------------------------------------------------------


class AdminLoginIn(BaseModel):
    username: str
    password: str


class AdminLoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


# ----- Notifications -----------------------------------------------------


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    channel: NotificationChannel
    recipient: str
    template_key: str
    rendered_body: str
    status: NotificationStatus
    created_at: datetime
