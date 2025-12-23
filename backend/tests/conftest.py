import os
import pytest
from typing import AsyncGenerator
from unittest.mock import AsyncMock

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Set test environment variables BEFORE importing app
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"
os.environ["DEBUG"] = "true"
os.environ["RATE_LIMIT_ENABLED"] = "false"  # Disable rate limiting in tests
os.environ["REQUIRE_AUTH"] = "false"  # Disable auth requirement in tests
os.environ["REQUIRE_PAYMENT"] = "false"  # Disable payment requirement in tests
os.environ["WEB_ONLY"] = "true"  # Use FastAPI background tasks instead of Celery
os.environ["ALLOWED_HOSTS"] = '["test", "localhost", "127.0.0.1"]'  # Allow test host

from app.main import app
from app.database import Base, get_db

# Import models to register them with Base metadata (required for create_all)
from app.models import db_models  # noqa: F401


@pytest.fixture(scope="session")
def event_loop_policy():
    import asyncio

    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture
async def test_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///file:test.db?mode=memory&cache=shared&uri=true",
        echo=False,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    async with session_factory() as session:
        yield session


@pytest.fixture
async def client(test_session) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis():
    mock = AsyncMock()
    mock.ping = AsyncMock(return_value=True)
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.close = AsyncMock()
    return mock
