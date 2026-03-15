# Настройка тестового окружения:
# - SQLite вместо PostgreSQL (быстро и не нужен контейнер)
# - FakeRedis вместо Redis (всё в памяти)
# - SLOW_DB_DELAY=0 чтобы тесты не ждали по 2 секунды

import asyncio
import os
from unittest.mock import AsyncMock, patch

# Override settings before importing app
os.environ["SLOW_DB_DELAY"] = "0"
os.environ["JWT_SECRET"] = "test-secret"

# Clear settings cache to pick up test env vars
from app.core.config import get_settings
get_settings.cache_clear()

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.session import Base, get_async_session
from app.dependencies.deps import get_redis
from app.main import app

# ── In-memory SQLite for tests ──

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"
test_engine = create_async_engine(TEST_DB_URL, echo=False)
test_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)


# ── Fake Redis for tests ──

# ИИ помог написать этот мок — реальный redis.asyncio имеет кучу методов,
# а тут нужны только get/set/delete/scan, и нужно чтобы SCAN работал с glob-паттернами
class FakeRedis:
    """Minimal in-memory Redis mock for testing."""

    def __init__(self):
        self._store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self._store[key] = value

    async def delete(self, *keys: str) -> None:
        for k in keys:
            self._store.pop(k, None)

    async def scan(self, cursor: int = 0, match: str = "*", count: int = 100):
        import fnmatch
        matched = [k for k in self._store if fnmatch.fnmatch(k, match)]
        return 0, matched

    async def close(self):
        self._store.clear()


fake_redis = FakeRedis()


async def override_get_async_session():
    async with test_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def override_get_redis():
    return fake_redis


app.dependency_overrides[get_async_session] = override_get_async_session
app.dependency_overrides[get_redis] = override_get_redis


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    fake_redis._store.clear()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
