# FuelPanda — Fleet Tracking Platform

A layered FastAPI backend for managing a fuel-delivery fleet: locations, products,
inventory, drivers, vehicles, vehicle allocation (blocking), shifts, deliveries
(orders), GPS tracking, and a performance-optimized fleet-status read model.

 Schema rationale: [`docs/DATABASE.md`](docs/DATABASE.md).
Trade-offs & assumptions: [`docs/DECISIONS.md`](docs/DECISIONS.md).

## Stack

Python 3.12 · FastAPI · Pydantic v2 · SQLAlchemy 2.0 · Alembic · PostgreSQL 16 · Redis 7 · pytest.

## Architecture

Strict one-directional layering:

```
HTTP → Router → Handler → Repository → DB
                   └────→ Service → Redis
```

- **Router** — HTTP surface only (paths, status codes, schema binding, DI wiring).
- **Handler** — all business logic; owns the transaction (unit of work).
- **Service** — cross-cutting / Redis (cache, distributed lock, fleet read model).
- **Repository** — pure persistence (CRUD + locked reads); never commits.

## Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8000
- Interactive docs (Swagger): http://localhost:8000/docs
- Health: http://localhost:8000/health

The `api` container runs `alembic upgrade head` before starting uvicorn.

## Run locally (without Docker)

```bash
pip install -e ".[dev]"
# point DATABASE_URL / REDIS_URL at a local Postgres + Redis, then:
alembic upgrade head
uvicorn app.main:app --reload
```

## Tests

```bash
pip install -e ".[dev]"
pytest -q                 # unit tests run anywhere (mocked repos + fakeredis + sqlite)
pytest -q tests/integration   # integration tests (need Docker for Postgres + Redis)
```

- `tests/unit` — handler logic with mocked repositories/services, schema validation,
  cache/lock services with fakeredis. Fast, no external services.
- `tests/integration` — full HTTP→DB→Redis flows via testcontainers (Postgres + Redis).

## Auth

Stubbed per the brief: `get_current_admin` / `get_current_driver` inject a fake
identity. Admin routes and driver routes are wired behind those dependencies so
swapping in real auth is a one-line change.


1. **Vehicle blocking** — a partial unique index `(vehicle_id, allocation_date) WHERE status='ACTIVE'`
   is the authoritative guard; a Redis lock is defense-in-depth only.
2. **Inventory consistency** — delivery completion bumps destination inventory inside
   one transaction with row locks; idempotent against double-submit.
3. **Shift lifecycle** — start requires an active allocation; end auto-fails open
   deliveries and frees the vehicle.
4. **GPS** — accepted only during an `ACTIVE` shift; write-through to a Redis read model.
5. **Fleet status** — O(active vehicles) read from Redis, with a DB-column fallback.
