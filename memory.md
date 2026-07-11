# Boilerworks Memory

This file is the **AI context seed** for the Boilerworks FastAPI Micro template. It captures decisions, constraints, and non-obvious facts that are not derivable from reading the code.

For conventions and patterns, see [`bootstrap.md`](bootstrap.md).

---

## Template purpose

Headless microservice template: API-only FastAPI service (no frontend) for callers that authenticate with an `X-API-Key` header — other services, cron jobs, webhook senders.

---

## Key architectural decisions

| Decision | Why |
|---|---|
| API-key auth (SHA256-hashed), not sessions/JWT | Callers are machines, not browsers; keys carry `scopes` for permission gating via `require_scope()` |
| SQLAlchemy 2.0 async + Alembic (async) | Single async stack end to end; migrations live in `alembic/versions/` |
| UUID as external identifier | Integer PKs are never exposed in API responses |
| Soft deletes (`deleted_at` via `func.now()`) | Never hard-delete business objects |
| `ApiResponse(ok, data, errors)` envelope | Every endpoint returns the same shape |
| slowapi rate limiting | Default limit from `RATE_LIMIT_DEFAULT` (100/minute) |
| Redis is optional | Cache only; the service runs without it |
| uv for dependency management | `uv sync`, `uv run ...`; lockfile is `uv.lock` |

---

## Things that bite newcomers

- **`require_api_key` is mandatory on every endpoint** except `/health` — auth is a dependency, not middleware, so forgetting it silently ships an open endpoint.
- **Raw API keys are shown once** at creation; only the SHA256 hash is stored. Revoke via `DELETE /api-keys/{id}` (sets `is_active=False`).
- **`DEBUG=false` disables `/docs` and `/redoc`** and hides exception details in 500 responses.
- **Tests use real Postgres** — never mock the database.
- **Max line length is 120** — `uv run ruff check . && uv run ruff format .` before committing.

---

## Local topology

```
docker-compose.yaml:
  api (FastAPI/uvicorn :8000) --> postgres:16 (:5432)
                              --> redis:7-alpine (:6379)
```

`./run.sh up` starts everything and runs migrations; `./run.sh test` / `./run.sh lint` run on the host via uv.
