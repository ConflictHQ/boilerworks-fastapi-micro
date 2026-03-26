import hashlib
import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db
from app.main import app
from app.models.api_key import ApiKey
from app.models.base import Base

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/boilerworks_test",
)

engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_database() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS webhook_events CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS api_keys CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS webhook_events CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS api_keys CASCADE"))


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def api_key_header(db: AsyncSession) -> dict[str, str]:
    raw_key = "test-key-abc123"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    api_key = ApiKey(name="test-key", key_hash=key_hash, scopes=["*"])
    db.add(api_key)
    await db.commit()
    return {"X-API-Key": raw_key}


@pytest.fixture
async def limited_api_key_header(db: AsyncSession) -> dict[str, str]:
    raw_key = "test-key-limited-456"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    api_key = ApiKey(name="limited-key", key_hash=key_hash, scopes=["webhooks.read"])
    db.add(api_key)
    await db.commit()
    return {"X-API-Key": raw_key}
