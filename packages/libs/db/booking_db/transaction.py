"""Database transaction utilities."""

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def transaction(session: AsyncSession):
    """
    Transaction context manager.

    This context manager ensures that a transaction is committed on success
    and rolled back on failure.

    Example:
        ```
        async with transaction(session):
            # Perform database operations
            session.add(some_object)
        ```
    """
    try:
        yield
        await session.commit()
    except Exception:
        await session.rollback()
        raise
