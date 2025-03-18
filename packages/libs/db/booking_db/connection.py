"""Database connection utilities."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, Optional
from pydantic import BaseModel

from booking_shared_models.models import Base


class DatabaseSettings(BaseModel):
    """Database connection settings."""
    url: str
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


class DatabaseClient:
    """
    Database client for managing connections and sessions.
    
    This class provides a convenient way to create and manage database
    connections and sessions using SQLAlchemy's async support.
    """
    
    def __init__(self, settings: DatabaseSettings):
        """Initialize the database client with settings."""
        self.settings = settings
        self.engine = create_async_engine(
            settings.url,
            echo=settings.echo,
            pool_size=settings.pool_size,
            max_overflow=settings.max_overflow,
            future=True
        )
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
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
