# Claude -- Boilerworks FastAPI Micro

Primary conventions doc: [`bootstrap.md`](bootstrap.md)

Read it before writing any code.

## Stack

- **Backend**: FastAPI (Python 3.12+)
- **Frontend**: None (API-only)
- **API**: REST (OpenAPI auto-generated at `/docs`)
- **ORM**: SQLAlchemy 2.0 async (`mapped_column()` syntax)
- **Migrations**: Alembic (async)
- **Auth**: API-key middleware (`X-API-Key` header, SHA256 hashed)
- **Validation**: Pydantic v2
- **Rate limiting**: slowapi
- **Cache**: Redis 7 (optional)

## Claude-specific notes

- Prefer `Edit` over rewriting whole files.
- Run `uv run ruff check . && uv run ruff format .` before committing.
- Max line length is 120.
- Never expose integer PKs in API responses -- use UUID.
- Auth check (`require_api_key`) is required on every endpoint.
- Use `require_scope("scope.name")` for permission-gated endpoints.
- Soft-delete only: set `deleted_at` via `func.now()`, never hard delete business objects.
- All endpoints return `ApiResponse(ok=bool, data=..., errors=[...])`.
- Tests use real Postgres -- never mock the database.
