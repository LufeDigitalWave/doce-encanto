"""Seed products, admin user and 14 days of scheduling slots.

Idempotent: running it twice is a no-op. The script is invoked from the
docker-compose `command` so fresh DBs come up ready to demo.
"""

from __future__ import annotations

import asyncio
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import SessionLocal, engine
from app.core.security import hash_password
from app.models import AdminUser, FulfillmentType, Product, SchedulingSlot


PRODUCTS: list[dict] = [
    {
        "name": "Brigadeiro Gourmet (cx 12)",
        "slug": "brigadeiro-gourmet-cx-12",
        "description": "Caixa com 12 brigadeiros gourmet no sabor tradicional, com granulado belga.",
        "price_cents": 3800,
        "image_url": "/products/brigadeiro-gourmet.jpg",
        "sort_order": 10,
    },
    {
        "name": "Bolo de Pote Ninho c/ Nutella",
        "slug": "bolo-pote-ninho-nutella",
        "description": "Bolo de pote com camadas de creme de Ninho e Nutella. 350ml.",
        "price_cents": 2200,
        "image_url": "/products/bolo-pote-ninho.jpg",
        "sort_order": 20,
    },
    {
        "name": "Torta Red Velvet",
        "slug": "torta-red-velvet",
        "description": "Torta Red Velvet 1.2kg com cream cheese frosting. Serve 10–12 fatias.",
        "price_cents": 18900,
        "image_url": "/products/torta-red-velvet.jpg",
        "sort_order": 30,
    },
    {
        "name": "Cento de Brigadeiro",
        "slug": "cento-brigadeiro",
        "description": "100 brigadeiros gourmet sortidos. Pronto pra sua festa.",
        "price_cents": 24900,
        "image_url": "/products/cento-brigadeiro.jpg",
        "sort_order": 40,
    },
    {
        "name": "Ovo de Colher 350g",
        "slug": "ovo-colher-350g",
        "description": "Ovo de colher 350g com recheio de Ninho c/ Nutella.",
        "price_cents": 7900,
        "image_url": "/products/ovo-colher.jpg",
        "sort_order": 50,
    },
    {
        "name": "Palha Italiana",
        "slug": "palha-italiana",
        "description": "Palha Italiana clássica, corte 3x3cm, 500g.",
        "price_cents": 4500,
        "image_url": "/products/palha-italiana.jpg",
        "sort_order": 60,
    },
    {
        "name": "Bolo Vulcão",
        "slug": "bolo-vulcao",
        "description": "Bolo vulcão de chocolate com recheio cremoso que escorre. 1.5kg.",
        "price_cents": 16500,
        "image_url": "/products/bolo-vulcao.jpg",
        "sort_order": 70,
    },
    {
        "name": "Kit Festa 50 doces",
        "slug": "kit-festa-50-doces",
        "description": "50 doces sortidos (brigadeiro, beijinho, cajuzinho, olho de sogra).",
        "price_cents": 18900,
        "image_url": "/products/kit-festa.jpg",
        "sort_order": 80,
    },
    {
        "name": "Bem Casadinho (un)",
        "slug": "bem-casadinho-un",
        "description": "Bem casadinho tradicional, unidade de 30g.",
        "price_cents": 350,
        "image_url": "/products/bem-casadinho.jpg",
        "sort_order": 90,
    },
    {
        "name": "Trufa de Chocolate (un)",
        "slug": "trufa-chocolate-un",
        "description": "Trufa artesanal de chocolate meio amargo. Unidade.",
        "price_cents": 450,
        "image_url": "/products/trufa-chocolate.jpg",
        "sort_order": 100,
    },
]

# 5 slots per day, both fulfillment types, closed on Sundays.
SLOT_HOURS: list[tuple[time, time]] = [
    (time(9, 0), time(11, 0)),
    (time(11, 0), time(13, 0)),
    (time(13, 0), time(15, 0)),
    (time(15, 0), time(17, 0)),
    (time(17, 0), time(19, 0)),
]


async def seed_admin(session: AsyncSession) -> None:
    settings = get_settings()
    existing = await session.scalar(select(AdminUser).where(AdminUser.username == settings.admin_username))
    if existing:
        return
    session.add(
        AdminUser(
            username=settings.admin_username,
            password_hash=hash_password(settings.admin_password),
        )
    )
    await session.commit()


async def seed_products(session: AsyncSession) -> None:
    existing = (await session.scalars(select(Product.slug))).all()
    existing_slugs = set(existing)
    added = False
    for p in PRODUCTS:
        if p["slug"] in existing_slugs:
            continue
        session.add(Product(**p))
        added = True
    if added:
        await session.commit()


async def seed_slots(session: AsyncSession) -> None:
    settings = get_settings()
    today = date.today()
    horizon = today + timedelta(days=settings.days_ahead)
    existing_dates = set(
        (
            await session.scalars(
                select(SchedulingSlot.date).where(SchedulingSlot.date >= today)
            )
        ).all()
    )
    for i in range(settings.days_ahead):
        d = today + timedelta(days=i)
        if d.weekday() == 6:  # Sunday closed
            continue
        if d in existing_dates:
            continue
        for start, end in SLOT_HOURS:
            for ft in FulfillmentType:
                session.add(
                    SchedulingSlot(
                        date=d,
                        start_time=start,
                        end_time=end,
                        capacity=settings.slot_capacity,
                        fulfillment_type=ft,
                    )
                )
    await session.commit()


async def main() -> None:
    # Drop and recreate isn't the seed's job — Alembic owns schema.
    async with SessionLocal() as session:
        await seed_admin(session)
        await seed_products(session)
        await seed_slots(session)
    await engine.dispose()
    print(
        f"[seed] complete @ {datetime.now(tz=timezone.utc).isoformat()} — "
        f"products={len(PRODUCTS)}, "
        f"horizon={settings.days_ahead}d, "
        f"slot_capacity={settings.slot_capacity}"
    )


if __name__ == "__main__":
    settings = get_settings()
    asyncio.run(main())