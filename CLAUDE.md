# CLAUDE.md — conventions for Claude Code on Doce Encanto

This file is loaded at the start of every Claude Code session in this repo.
Follow it strictly; if something here conflicts with a user instruction,
the user wins, but call it out.

## Project at a glance

- **Doce Encanto** is a fictional Brazilian confectionery's online store.
- It is **portfolio / demo** code, public on GitHub under `LufeDigitalWave`.
- **No real customer data.** Brand, products, testimonials, phones, emails,
  addresses, tax IDs — all invented.
- Two modes, chosen by `DEMO_MODE` env var:
  - `true` (default): fake providers, runs offline, no credentials.
  - `false`: real AbacatePay + Resend for live demos in closing calls.

## Language rules

- **Code, comments, docstrings, commit messages, branch names, env var
  keys** → **English**.
- **User-visible strings** (landing copy, checkout, admin UI, README body,
  docs other than ARCHITECTURE.md) → **PT-BR**.
- **Variable / function / class names** → English.
- **Commit messages** → English, Conventional Commits (`feat:`, `fix:`,
  `docs:`, `refactor:`, `test:`, `chore:`). Atomic commits.

## Money

- **Always** integers in **centavos** (`price_cents`, `subtotal_cents`,
  `shipping_cents`, `total_cents`). Never floats for money.
- BRL formatting on the UI is done in `frontend/src/lib/formatters.ts`
  using `Intl.NumberFormat('pt-BR', ...)`. Result: `R$ 1.234,56`.

## DEMO_MODE is a contract

- The choice of payment / notification provider happens in **one place**:
  `backend/app/core/deps.py` (`get_payment_provider`, `get_notification_provider`).
- The rest of the codebase **must not import** `AbacatePayProvider` or
  `ResendEmailProvider` directly. Always depend on the `PaymentProvider` /
  `NotificationProvider` ABCs.
- If `DEMO_MODE=false`, missing required env vars (`ABACATEPAY_API_KEY`,
  `ABACATEPAY_WEBHOOK_SECRET`, `RESEND_API_KEY`, `EMAIL_FROM`) **must
  crash at startup** with a clear message — never silently fall back to
  the fake provider.

## Adding a new PaymentProvider

1. Create `backend/app/services/payment/<your_provider>.py` implementing
   the `PaymentProvider` ABC from `backend/app/services/payment/base.py`.
2. Add a factory branch in `backend/app/core/deps.py`.
3. Add a test in `backend/app/tests/test_payment_<your_provider>.py` that
   mocks the provider's HTTP client. Never hit a real API in tests.
4. Document the integration in `docs/ARCHITECTURE.md`.

Same shape applies for `NotificationProvider`.

## Running things

```bash
# Full stack (one command)
docker compose up --build

# Backend tests
docker compose exec api pytest -v

# Lint
docker compose exec api ruff check .
cd frontend && npm run lint

# New migration
docker compose exec api alembic revision --autogenerate -m "add table foo"
docker compose exec api alembic upgrade head

# Re-seed products + slots (idempotent)
docker compose exec api python -m app.seeds.run

# Wipe and re-init (dev only)
docker compose down -v && docker compose up --build
```

## Useful routes once running

- Web (landing): `http://localhost:5173`
- API docs (Swagger): `http://localhost:8000/docs`
- Admin: `http://localhost:5173/admin` (admin / demo1234)
- Order tracking (after checkout): `/pedido/<public_token>`

## Pitfalls already learned

- **Slot capacity** is enforced both at read time (calendar) and at write
  time (`SELECT ... FOR UPDATE` inside the order creation transaction).
  Do not trust the calendar alone.
- **Webhook idempotency**: `payment_events.external_event_id` is UNIQUE.
  AbacatePay may retry the same event. The handler must be idempotent.
- **Webhook signature**: read raw bytes BEFORE FastAPI parses the body;
  we use `request.body()` inside the route. Otherwise HMAC will not match.
- **Pix charge creation in dev mode**: AbacatePay's `simulate-payment`
  endpoint is dev-only. Never expose it; guard with `DEMO_MODE`.