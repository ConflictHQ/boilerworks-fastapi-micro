# Calliope — Boilerworks FastAPI Micro
<!-- Agent shim for https://github.com/calliopeai/calliope-cli -->

Primary conventions doc: [`bootstrap.md`](bootstrap.md)
Context seed: [`memory.md`](memory.md)

Read both before writing any code.

---

## Project-specific notes

- FastAPI (Python 3.12+) — API-only REST, OpenAPI auto-generated at `/docs`. Pydantic v2 validation; slowapi rate limiting; Redis 7 optional.
- SQLAlchemy 2.0 async (`mapped_column()` syntax) + async Alembic; API-key middleware (`X-API-Key` header, SHA256-hashed).
- Auth (`require_api_key`) required on every endpoint; use `require_scope("scope.name")` for permission-gated endpoints.
- Never expose integer PKs — use UUID; all endpoints return `ApiResponse(ok=bool, data=..., errors=[...])`.
- Soft-delete only: set `deleted_at` via `func.now()`, never hard delete business objects.
- Ruff (check + format), max line length 120; tests use real Postgres — never mock the database.
