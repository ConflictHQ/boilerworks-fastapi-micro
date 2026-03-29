# Boilerworks FastAPI Micro -- Bootstrap

This is the primary conventions document for the Boilerworks FastAPI Micro template. All agent shims (`CLAUDE.md`, `AGENTS.md`) point here.

An agent given this document and a business requirement should be able to generate correct, idiomatic code without exploring the codebase.

---

## What's Already Built

| Layer | What's there |
|---|---|
| Auth | API-key middleware (`X-API-Key` header), SHA256-hashed keys, per-key scopes |
| Data | Postgres 16, `AuditBase` (UUID PK, created_at, updated_at), `SoftDeleteMixin` |
| API | REST (FastAPI native), OpenAPI docs at `/docs`, Pydantic v2 validation |
| ORM | SQLAlchemy 2.0 async with `mapped_column()` syntax |
| Migrations | Alembic (async) |
| Rate limiting | slowapi (per-IP) |
| Cache | Redis 7 (optional) |
| Infra | Docker Compose: api, postgres, redis |
| CI | GitHub Actions: lint (Ruff) + test (pytest/Postgres) + audit (pip-audit) |

---

## App Structure

| Module | Purpose |
|---|---|
| `app/main.py` | FastAPI app, rate limiter, exception handler, uvicorn entrypoint |
| `app/config.py` | Pydantic settings from env vars |
| `app/database.py` | Async SQLAlchemy engine, session factory, `get_db` dependency |
| `app/models/` | SQLAlchemy models (`Base`, `AuditBase`, `SoftDeleteMixin`, `ApiKey`, `WebhookEvent`) |
| `app/schemas/` | Pydantic request/response models (`ApiResponse`, `ApiKeyCreate`, `WebhookPayload`, etc.) |
| `app/api/` | Route handlers (`health`, `api_keys`, `webhooks`) |
| `app/auth/` | `require_api_key` dependency, `require_scope` for permission checks |
| `tests/` | pytest + httpx AsyncClient, real Postgres |

---

## Conventions

### Models

All business models inherit from `AuditBase`:

```python
from app.models.base import AuditBase, SoftDeleteMixin

class MyModel(AuditBase, SoftDeleteMixin):
    __tablename__ = "my_models"

    name: Mapped[str] = mapped_column(String(255))
```

`AuditBase` provides: `id` (UUID PK), `created_at`, `updated_at`.
`SoftDeleteMixin` provides: `deleted_at`.

**Rules:**
- Use `mapped_column()` syntax (not legacy `Column()`)
- UUID primary keys only -- never expose integer PKs
- Soft deletes only -- set `deleted_at`, never hard delete business objects
- All timestamps use server-side `func.now()` for consistency

### API Endpoints

Every endpoint returns `ApiResponse`:

```python
from app.schemas.common import ApiResponse

@router.post("/things", response_model=ApiResponse)
async def create_thing(
    body: ThingCreate,
    _caller: ApiKey = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    # ... create the thing ...
    return ApiResponse(ok=True, data=ThingOut.model_validate(thing).model_dump(mode="json"))
```

**Rules:**
- Auth check on every endpoint (`Depends(require_api_key)`)
- Use `require_scope("scope.name")` for permission-gated endpoints
- Pydantic models for all request bodies and response shapes
- Return `ApiResponse(ok=True, data=...)` or `ApiResponse(ok=False, errors=[...])`

### Auth

API key in `X-API-Key` header. Keys are SHA256 hashed before storage.

```python
# Creating a new key
raw_key = secrets.token_urlsafe(32)
key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
api_key = ApiKey(name="my-key", key_hash=key_hash, scopes=["*"])
```

**Scopes:** Each key has a `scopes` array. `"*"` means full access. Use `require_scope("scope.name")` to gate endpoints.

### Testing

pytest + httpx `AsyncClient` against real Postgres.

```python
async def test_my_endpoint(client: AsyncClient, api_key_header: dict[str, str], db: AsyncSession) -> None:
    response = await client.post("/things", json={"name": "test"}, headers=api_key_header)
    assert response.status_code == 200
    assert response.json()["ok"] is True

    # Assert against database state
    result = await db.execute(select(Thing).where(Thing.name == "test"))
    thing = result.scalar_one()
    assert thing.name == "test"
```

**Rules:**
- Real database -- never mock
- Assert against database state after mutations
- Test both happy path and auth-denied cases
- Use `api_key_header` fixture for authenticated requests
- Use `limited_api_key_header` fixture for scope-limited requests

### Adding a New Module

1. Create model in `app/models/` inheriting from `AuditBase`
2. Import model in `app/models/__init__.py`
3. Create Pydantic schemas in `app/schemas/`
4. Create route handler in `app/api/`
5. Register router in `app/main.py`
6. Generate migration: `uv run alembic revision --autogenerate -m "description"`
7. Apply migration: `uv run alembic upgrade head`
8. Write tests in `tests/`
9. Run `uv run ruff check . && uv run ruff format . && uv run pytest`

---

## Code Style

| Concern | Tool |
|---|---|
| Formatter | Ruff (format) |
| Linter | Ruff (check) |
| Line length | 120 characters |
| Import sorting | Ruff (isort) |

Run: `uv run ruff check . && uv run ruff format --check .`

---

## Common Commands

```bash
uv sync --all-extras                    # Install dependencies
uv run ruff check .                     # Lint
uv run ruff format .                    # Format
uv run pytest -v --cov=app              # Run tests
uv run alembic revision --autogenerate -m "msg"  # Generate migration
uv run alembic upgrade head             # Apply migrations
docker compose up -d                    # Start all services
docker compose up -d postgres redis     # Start infra only
```

---

## Local URLs

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| OpenAPI docs | http://localhost:8000/docs |
| Postgres | localhost:5432 |
| Redis | localhost:6379 |
