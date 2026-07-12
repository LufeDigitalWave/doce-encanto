"""Public products API — read-only for the landing page vitrine."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.models import Product
from app.schemas import ProductOut

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
async def list_products(session: AsyncSession = Depends(get_session)):
    rows = await session.scalars(
        select(Product)
        .where(Product.is_active.is_(True))
        .order_by(Product.sort_order)
    )
    return rows.all()


@router.get("/{slug}", response_model=ProductOut)
async def get_product(slug: str, session: AsyncSession = Depends(get_session)):
    from fastapi import HTTPException

    product = await session.scalar(select(Product).where(Product.slug == slug))
    if product is None:
        raise HTTPException(404, "product not found")
    return product
