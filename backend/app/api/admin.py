"""Admin panel API — auth + order management + products CRUD + outbox."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.db import get_session
from app.core.deps import get_email_provider, get_whatsapp_provider
from app.core.security import create_access_token, decode_access_token, verify_password
from app.models import (
    AdminUser,
    Notification,
    Order,
    OrderStatus,
    Product,
)
from app.schemas import (
    AdminLoginIn,
    AdminLoginOut,
    NotificationOut,
    OrderOut,
    OrderStatusUpdate,
    ProductCreate,
    ProductOut,
    ProductUpdate,
)
from app.services import notification_service

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ---- Auth helpers ---------------------------------------------------------

async def _get_admin_user(session: AsyncSession, username: str) -> AdminUser | None:
    return await session.scalar(select(AdminUser).where(AdminUser.username == username))


async def require_admin(
    authorization: str = Header(alias="Authorization"),
) -> str:
    """Dependency that validates the JWT and returns the admin username."""
    settings = get_settings()
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_access_token(token, secret=settings.jwt_secret)
        return payload["sub"]
    except Exception:
        raise HTTPException(401, "invalid or expired token")


# ---- Login ----------------------------------------------------------------

@router.post("/login", response_model=AdminLoginOut)
async def login(body: AdminLoginIn, session: AsyncSession = Depends(get_session)):
    user = await _get_admin_user(session, body.username)
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "invalid credentials")
    settings = get_settings()
    token = create_access_token(
        user.username, secret=settings.jwt_secret, ttl_minutes=settings.jwt_ttl_minutes
    )
    return AdminLoginOut(
        access_token=token, expires_in_minutes=settings.jwt_ttl_minutes
    )


# ---- Dashboard summary ----------------------------------------------------

@router.get("/dashboard")
async def dashboard(
    _admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    from datetime import date, datetime, timezone

    today = date.today()
    total_today = await session.scalar(
        select(func.count(Order.id)).where(Order.scheduled_date == today)
    )
    revenue_today = await session.scalar(
        select(func.coalesce(func.sum(Order.total_cents), 0)).where(
            Order.scheduled_date == today,
            Order.payment_status == "paid",
        )
    )
    return {
        "orders_today": total_today or 0,
        "revenue_today_cents": revenue_today or 0,
    }


# ---- Orders ---------------------------------------------------------------

@router.get("/orders", response_model=list[OrderOut])
async def list_orders(
    status: OrderStatus | None = None,
    _admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    q = select(Order).options(selectinload(Order.items), selectinload(Order.slot))
    if status is not None:
        q = q.where(Order.status == status)
    q = q.order_by(Order.created_at.desc()).limit(100)
    rows = (await session.scalars(q)).all()
    return rows


@router.patch("/orders/{order_id}/status", response_model=OrderOut)
async def update_order_status(
    order_id: int,
    body: OrderStatusUpdate,
    _admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    order = await session.scalar(
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.slot))
        .where(Order.id == order_id)
    )
    if order is None:
        raise HTTPException(404)
    order.status = body.status
    await session.commit()
    await session.refresh(order)

    await notification_service.emit(
        session,
        order=order,
        template_key="order_status_changed",
        email_provider=get_email_provider(),
        whatsapp_provider=get_whatsapp_provider(),
        extra_status_label=body.status.value.replace("_", " ").title(),
    )
    await session.commit()
    return order


# ---- Products CRUD --------------------------------------------------------

@router.get("/products", response_model=list[ProductOut])
async def admin_list_products(
    _admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    rows = (await session.scalars(select(Product).order_by(Product.sort_order))).all()
    return rows


@router.post("/products", response_model=ProductOut, status_code=201)
async def admin_create_product(
    body: ProductCreate,
    _admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    from slugify import slugify

    product = Product(
        name=body.name,
        slug=slugify(body.name),
        description=body.description,
        price_cents=body.price_cents,
        image_url=body.image_url,
        is_active=body.is_active,
        sort_order=body.sort_order,
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


@router.patch("/products/{product_id}", response_model=ProductOut)
async def admin_update_product(
    product_id: int,
    body: ProductUpdate,
    _admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    product = await session.get(Product, product_id)
    if product is None:
        raise HTTPException(404)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    await session.commit()
    await session.refresh(product)
    return product


# ---- Notifications outbox -------------------------------------------------

@router.get("/notifications", response_model=list[NotificationOut])
async def list_notifications(
    _admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    rows = (
        await session.scalars(
            select(Notification).order_by(Notification.created_at.desc()).limit(200)
        )
    ).all()
    return rows
