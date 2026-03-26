# Build Spec — boilerworks-fastapi-micro

## Context

You are building the `boilerworks-fastapi-micro` template from scratch. This is a lightweight FastAPI microservice with API-key auth, no user accounts, no frontend. It is part of the Boilerworks template catalogue.

## Required Reading (before writing ANY code)

Read ALL of these files. They are your source of truth:

1. `../primers/fastapi-micro/PRIMER.md` — architecture spec, stack choices, patterns, build order
2. `../primers/PROCESS.md` — development philosophy, coding standards (Ruff, uv, venv, PEP 8), testing standards (meaningful tests, 80%+ coverage), quality gates
3. `../primers/CATALOGUE.md` — what Boilerworks is, universal patterns, anti-patterns
4. `../primers/PRIMER_TEMPLATE.md` — the structure all primers follow (for context)
5. `../boilerworks-django-nextjs/bootstrap.md` — reference implementation of a bootstrap.md (for style/structure reference when writing this template's bootstrap.md)
6. `../boilerworks-django-nextjs/CLAUDE.md` — reference implementation of a CLAUDE.md agent shim

## Repo Setup (do this FIRST)

This directory is not yet a git repo. Before building:

1. `git init`
2. Create the GitHub repo: `gh repo create ConflictHQ/boilerworks-fastapi-micro --public --source=. --push`
   - If the org/repo already exists, just add the remote: `git remote add origin https://github.com/ConflictHQ/boilerworks-fastapi-micro.git`
3. Create an initial commit with the existing scaffolding files
4. Set up a GitHub Project board for this repo: `gh api orgs/ConflictHQ/projects --method POST -f title="boilerworks-fastapi-micro"`
   - If this fails (permissions, already exists), skip it and move on
5. Push to main

You have `gh` CLI access. Use it for repo creation, issues, and PRs.

**After repo setup, follow the Build Order in the primer exactly. Do not skip phases. Do not reorder.**

## Quality Rules (non-negotiable)

### Code
- Python 3.12+, fully typed (type hints on all function signatures)
- PEP 8 via Ruff. Run `ruff check .` and `ruff format .` after every phase. Zero violations.
- Use `uv` for package management. Create `pyproject.toml` with all dependencies. Generate `uv.lock`.
- Virtual environment: use `uv venv` to create `.venv`
- SQLAlchemy 2.0 async with mapped_column syntax (not legacy Column())
- Pydantic v2 for all request/response models
- Alembic for migrations (not raw SQL, not SQLAlchemy create_all)
- API-key auth: keys hashed with SHA256 before storage. Raw key returned ONCE on creation.
- All endpoints return consistent `ApiResponse` shape: `{"ok": bool, "data": ..., "errors": [...]}`

### Testing
- pytest + httpx AsyncClient
- Tests hit a REAL Postgres database (via Docker or testcontainers). NO MOCKS.
- Every endpoint gets at minimum: happy path test + auth-denied test (missing/invalid API key)
- Assert against database state after mutations, not just response content
- No hardcoded passes, no empty test bodies, no `assert True`
- Target: 80%+ coverage minimum
- Run `pytest` after every phase. All tests must pass before moving on.

### Docker
- `docker-compose.yaml` with: api (FastAPI/uvicorn), postgres (16), redis (7-alpine, optional)
- Health checks on all services
- `docker compose up` must boot cleanly with no errors
- The API must be reachable at `http://localhost:8000` after boot

### Files that MUST exist when done
- `pyproject.toml` (with Ruff config, project metadata, all dependencies)
- `uv.lock`
- `alembic.ini` + `alembic/` (migrations directory with at least one migration)
- `app/` (main application package)
- `app/main.py` (FastAPI app, uvicorn entrypoint)
- `app/config.py` (settings from env vars, validated with Pydantic)
- `app/models/` (SQLAlchemy models)
- `app/api/` (route handlers)
- `app/auth/` (API key middleware and models)
- `app/schemas/` (Pydantic request/response models)
- `tests/` (pytest tests, NOT empty)
- `docker-compose.yaml`
- `Dockerfile`
- `.env.example`
- `README.md` (updated with actual getting started, endpoints, architecture)
- `CLAUDE.md` (updated with actual stack info, not placeholder)
- `bootstrap.md` (updated with actual conventions, not stub)
- `.github/workflows/ci.yml` (lint + test + audit)

### What NOT to do
- Do NOT create stubs or placeholder files with TODO comments
- Do NOT write tests that always pass (no `assert True`, no `pass`)
- Do NOT mock the database
- Do NOT use SQLAlchemy `create_all()` instead of Alembic migrations
- Do NOT use legacy SQLAlchemy Column() syntax — use mapped_column()
- Do NOT skip type hints
- Do NOT add features not in the primer (no user auth, no forms engine, no workflows)
- Do NOT use pip directly — use uv

## Phase Checklist

After completing EACH phase, verify:
1. `ruff check . && ruff format --check .` — zero issues
2. `pytest` — all tests pass
3. `docker compose up -d` — boots cleanly (if Docker is set up)
4. No TODO/FIXME/HACK comments in the code
5. Move to next phase ONLY when the current phase is fully complete

## Completion

When ALL of the following are true:
- All 4 build phases complete
- `ruff check .` passes with zero violations
- `ruff format --check .` passes
- `pytest` passes with 80%+ coverage
- `docker compose up -d` boots and the API responds at localhost:8000
- All files listed above exist with real content (not stubs)
- README.md documents actual endpoints and getting started
- bootstrap.md documents actual conventions (not placeholder text)

Output: <promise>TEMPLATE_COMPLETE</promise>

If you are stuck after 15 iterations:
- Document what's blocking in a file called `BLOCKERS.md`
- List what was attempted
- Suggest what a human should look at
- Output: <promise>TEMPLATE_COMPLETE</promise> (so the loop exits)
