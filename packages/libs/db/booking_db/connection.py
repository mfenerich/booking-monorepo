"""Database connection utilities."""

from typing import AsyncGenerator, Optional, Dict, Any

from booking_shared_models.models import Base
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


class DatabaseSettings(BaseModel):
    """Database connection settings."""

    url: str
    echo: bool = False
    pool_size: Optional[int] = None
    max_overflow: Optional[int] = None


class DatabaseClient:
    """
    Database client for managing connections and sessions.

    This class provides a convenient way to create and manage database
    connections and sessions using SQLAlchemy's async support.
    """

    def __init__(self, settings: DatabaseSettings):
        """Initialize the database client with settings."""
        self.settings = settings
        
        # Create engine options based on database type
        engine_options: Dict[str, Any] = {"echo": settings.echo, "future": True}
        
        # Only add pooling options for non-SQLite databases or if explicitly specified
        if not settings.url.startswith("sqlite") or "?poolclass=" in settings.url:
            if settings.pool_size is not None:
                engine_options["pool_size"] = settings.pool_size
            if settings.max_overflow is not None:
                engine_options["max_overflow"] = settings.max_overflow
        
        self.engine = create_async_engine(
            settings.url,
            **engine_options
        )
        
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session."""
        async with self.async_session() as session:
            try:
                yield session
            finally:
                await session.close()

    async def create_tables(self):
        """Create all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        """Close all connections."""
        await self.engine.dispose()


# Global instance
_db_client: Optional[DatabaseClient] = None


def get_db_client() -> DatabaseClient:
    """Get the global database client instance."""
    if _db_client is None:
        raise RuntimeError("Database client not initialized")
    return _db_client


def initialize_db(settings: DatabaseSettings) -> DatabaseClient:
    """Initialize the global database client."""
    global _db_client
    _db_client = DatabaseClient(settings)
    return _db_client


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session.

    This is a FastAPI dependency that provides a database session.
    """
    client = get_db_client()
    async for session in client.get_session():
        yield session
