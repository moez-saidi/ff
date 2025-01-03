import asyncio

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.core.database import Base, get_db_session
from app.main import app


class Settings(BaseSettings):
    POSTGRES_USER: str
    PGPORT: int
    POSTGRES_HOST: str
    POSTGRES_PASSWORD: SecretStr


TEST_POSTGRES_DB = "test_db"

config = Settings()
TEST_DATABASE_URI: PostgresDsn = (
    "postgresql+asyncpg://"
    f"{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD.get_secret_value()}"
    f"@{config.POSTGRES_HOST}:{config.PGPORT}/{TEST_POSTGRES_DB}"
)


test_engine = create_async_engine(TEST_DATABASE_URI)
test_session_local = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Override the default event loop for pytest."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Create the test database schema."""
    sync_url = str(TEST_DATABASE_URI).replace("asyncpg", "psycopg")
    if not database_exists(sync_url):
        create_database(sync_url)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    drop_database(sync_url)
    await test_engine.dispose()


@pytest.fixture(scope="session")
async def db_session():
    """Provide a clean database session for each test."""
    async with test_session_local() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def async_test_client(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides = {}
