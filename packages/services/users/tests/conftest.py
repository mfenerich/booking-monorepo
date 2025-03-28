import asyncio
from typing import Any, AsyncGenerator, Dict, Generator

import pytest
import pytest_asyncio
from booking_auth import get_password_hash
from booking_db import DatabaseClient, DatabaseSettings, initialize_db
from booking_shared_models.models import Base, User
from booking_shared_models.schemas import UserCreate
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from booking_users.main import create_app

# Use a persistent in-memory SQLite database that can be shared between connections
TEST_DB_URL = "sqlite+aiosqlite:///file:memdb1?mode=memory&cache=shared&uri=true"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_client() -> AsyncGenerator[DatabaseClient, None]:
    """Create a test database client for the whole test session."""
    # Create database settings for in-memory SQLite
    # SQLite doesn't support pool_size and max_overflow
    db_settings = DatabaseSettings(url=TEST_DB_URL)

    # Initialize database client
    client = initialize_db(db_settings)

    # Create tables
    async with client.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Verify tables were created
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        )
        tables = result.fetchall()
        if not tables:
            raise Exception(
                "Users table was not created! Database schema setup failed."
            )

    yield client

    # Clean up
    await client.close()


@pytest_asyncio.fixture
async def db_session(db_client: DatabaseClient) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with db_client.async_session() as session:
        # Start with a clean slate for each test
        for table in reversed(Base.metadata.sorted_tables):
            # Use text() function to wrap SQL strings
            await session.execute(text(f"DELETE FROM {table.name}"))
        await session.commit()

        yield session

        # Rollback at the end of the test
        await session.rollback()


@pytest.fixture
def app(db_client: DatabaseClient) -> FastAPI:
    """Create a FastAPI test application."""
    return create_app()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create a test client for synchronous tests."""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for asynchronous tests."""
    # Use ASGITransport to connect AsyncClient to the FastAPI app
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Sample user data for tests."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Password123!",
    }


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession, test_user_data: Dict[str, Any]) -> User:
    """Create a test user in the database."""
    # Create user
    user = User(
        email=test_user_data["email"],
        username=test_user_data["username"],
        hashed_password=get_password_hash(test_user_data["password"]),
        is_active=True,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
def test_user_create() -> UserCreate:
    """Create a UserCreate model for testing."""
    return UserCreate(
        email="new@example.com", username="newuser", password="NewPassword123!"
    )
