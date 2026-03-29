# Boilerworks FastAPI Micro

Lightweight FastAPI microservice template with API-key auth. No user accounts, no sessions, no frontend. Part of the [Boilerworks](https://github.com/ConflictHQ) template catalogue.

## Quick Start

```bash
# Clone and enter the project
git clone https://github.com/ConflictHQ/boilerworks-fastapi-micro.git
cd boilerworks-fastapi-micro

# Copy environment config
cp .env.example .env

# Start infrastructure
docker compose up -d

# Or run locally with uv
uv sync --all-extras
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

The API is available at http://localhost:8000. OpenAPI docs at http://localhost:8000/docs (debug mode only).

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.12+) |
| ORM | SQLAlchemy 2.0 async |
| Database | Postgres 16 |
| Cache | Redis 7 (optional) |
| Auth | API-key middleware (SHA256 hashed) |
| Validation | Pydantic v2 |
| Migrations | Alembic |
| Rate limiting | slowapi |
| Linter/Formatter | Ruff |
| Package manager | uv |

## Endpoints

### Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Health check (DB connectivity) |

### API Keys

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api-keys` | Yes | Create a new API key (returns raw key once) |
| GET | `/api-keys` | Yes | List all active API keys |
| DELETE | `/api-keys/{id}` | Yes | Revoke an API key |

### Webhooks

| Method | Path | Auth | Scope | Description |
|--------|------|------|-------|-------------|
| POST | `/webhooks` | Yes | -- | Receive a webhook event |
| GET | `/webhooks` | Yes | -- | List recent webhook events |
| GET | `/webhooks/{id}` | Yes | -- | Get a specific webhook event |
| DELETE | `/webhooks/{id}` | Yes | `webhooks.delete` | Soft-delete a webhook event |

### Authentication

All endpoints (except `/health`) require an API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-key-here" http://localhost:8000/webhooks
```

### Response Format

All endpoints return a consistent shape:

```json
{
  "ok": true,
  "data": { ... },
  "errors": null
}
```

## Development

```bash
# Install dependencies
uv sync --all-extras

# Run linter and formatter
uv run ruff check .
uv run ruff format .

# Run tests (requires Postgres)
docker compose up -d postgres
TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/boilerworks_test" uv run pytest -v --cov=app

# Generate a new migration
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/boilerworks" uv run alembic revision --autogenerate -m "description"

# Apply migrations
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/boilerworks" uv run alembic upgrade head
```

## Docker

```bash
# Start everything
docker compose up -d

# Start infrastructure only
docker compose up -d postgres redis

# View logs
docker compose logs -f api
```

Services:
- **api**: FastAPI + uvicorn on port 8000
- **postgres**: PostgreSQL 16 on port 5433
- **redis**: Redis 7 on port 6379

## Architecture

```
Caller (service, cron, webhook sender)
  |
  v (HTTP + X-API-Key header)
  |
FastAPI (async Python, Pydantic validation, slowapi rate limiting)
  |-- SQLAlchemy 2.0 async (Postgres)
  +-- Redis 7 (cache, optional)
```

## License

MIT

---

Boilerworks is a [Conflict](https://weareconflict.com) brand. CONFLICT is a registered trademark of Conflict LLC.
