import asyncio

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import DATABASE_URI, Base
from app.core.hashing import get_password_hash
from app.main import app
from app.models.users import User


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(DATABASE_URI)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine):
    async_session_maker = sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_maker() as session:
        await session.begin()
        yield session
        await session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(text(f"TRUNCATE {table.name} CASCADE;"))
            await session.commit()


@pytest.fixture(scope="function")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test/api") as ac:
        yield ac


@pytest.fixture(scope="function")
def sync_client():
    return TestClient(app)


@pytest.fixture(scope="function")
async def create_test_users(db_session: AsyncSession):
    async def _create_test_users(num_users: int = 3):
        users = []
        for i in range(num_users):
            user = User(
                username=f"testuser{i}",
                email=f"testuser{i}@example.com",
                hashed_password=get_password_hash(f"password{i}"),
                is_active=True,
            )
            db_session.add(user)
            users.append(user)

        await db_session.commit()

        return users

    yield _create_test_users
