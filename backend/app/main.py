"""FastAPI application entry point.

Imported from the Docker CMD / uvicorn; also by the test conftest ASGI
transport. Routing is split across `app.api` routers.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Validate settings on startup (fail-fast when DEMO_MODE=false and keys missing)
    get_settings()
    yield


app = FastAPI(
    title="Doce Encanto API",
    version="0.1.0",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For portfolio demo; restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
# Imported here to register routes. Actual handlers live in app.api.*
from app.api.products import router as products_router  # noqa: E402
from app.api.scheduling import router as scheduling_router  # noqa: E402
from app.api.orders import router as orders_router  # noqa: E402
from app.api.payments import router as payments_router  # noqa: E402
from app.api.webhooks import router as webhooks_router  # noqa: E402
from app.api.admin import router as admin_router  # noqa: E402
from app.api.tracking import router as tracking_router  # noqa: E402

app.include_router(products_router)
app.include_router(scheduling_router)
app.include_router(orders_router)
app.include_router(payments_router)
app.include_router(webhooks_router)
app.include_router(admin_router)
app.include_router(tracking_router)


@app.get("/health")
async def health():
    return {"status": "ok", "demo_mode": get_settings().demo_mode}
