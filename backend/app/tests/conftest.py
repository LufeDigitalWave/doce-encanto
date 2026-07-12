"""Pytest fixtures — async DB session and isolated test schema.

Tests use a real Postgres connection (the docker-compose db) but with a
dedicated database `doce_encanto_test` that's truncated between tests.
The `DATABASE_URL` env var is overridden for the test session.
"""

from __future__ import annotations

import asyncio
import os
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Point to a separate test DB BEFORE app modules are imported.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/doce_encanto_test",
)
os.environ.setdefault("DEMO_MODE", "true")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("ADMIN_PASSWORD", "demo1234")

# Force app modules to read the test DB.
from app.core.config import reset_settings_cache  # noqa: E402
from app.core.db import Base  # noqa: E402
from app import models  # noqa: F401,E402 — register models


@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(os.environ["DATABASE_URL"], future=True)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncSession:
    async with engine.begin() as conn:
        # Truncate everything we own.
        await conn.execute(
            text(
                "TRUNCATE TABLE notifications, payment_events, order_items, "
                "orders, scheduling_slots, products, admin_users RESTART IDENTITY CASCADE"
            )
        )
    maker = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
    async with maker() as s:
        yield s
        await s.rollback()


@pytest_asyncio.fixture
async def client():
    """In-process FastAPI test client (TestClient doesn't support async well,
    so we hit the app via httpx ASGI transport)."""
    import httpx
    from app.main import app  # imported here so settings cache is already primed

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c