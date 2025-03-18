"""Repository base class for database operations."""

from typing import TypeVar, Generic, Type, List, Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.sql import Select

from booking_shared_models.models import Base

T = TypeVar('T', bound=Base)


class Repository(Generic[T]):
    """
    Base repository class for database operations.
    
    This class provides basic CRUD operations for a model.
    """
    
    def __init__(self, model: Type[T]):
        """Initialize with model class."""
        self.model = model
    
    async def create(self, session: AsyncSession, data: Dict[str, Any]) -> T:
        """Create a new record."""
        db_obj = self.model(**data)
        session.add(db_obj)
        await session.flush()
        return db_obj
    
    async def get(self, session: AsyncSession, id: Any) -> Optional[T]:
        """Get a record by ID."""
        stmt = select(self.model).where(self.model.id == id)
        result = await session.execute(stmt)
        return result.scalars().first()
    
    async def get_by(self, session: AsyncSession, **kwargs) -> Optional[T]:
        """Get a record by arbitrary field values."""
        stmt = select(self.model)
        for field, value in kwargs.items():
            stmt = stmt.where(getattr(self.model, field) == value)
        result = await session.execute(stmt)
        return result.scalars().first()
    
    async def list(
        self, 
        session: AsyncSession, 
        stmt: Optional[Select] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[T]:
        """List records, optionally filtering and paginating."""
        if stmt is None:
            stmt = select(self.model)
        
        stmt = stmt.offset(skip).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())
    
    async def count(
        self, 
        session: AsyncSession, 
        stmt: Optional[Select] = None
    ) -> int:
        """Count records, optionally filtering."""
        if stmt is None:
            stmt = select(self.model)
        
        # Convert select to count query
        from sqlalchemy import func
        count_stmt = select(func.count()).select_from(stmt.subquery())
        result = await session.execute(count_stmt)
        return result.scalar_one()
    
    async def update(
        self, 
        session: AsyncSession, 
        id: Any, 
        data: Dict[str, Any]
    ) -> Optional[T]:
        """Update a record by ID."""
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**data)
            .returning(self.model)
        )
        result = await session.execute(stmt)
        return result.scalars().first()
    
    async def delete(self, session: AsyncSession, id: Any) -> bool:
        """Delete a record by ID."""
        stmt = delete(self.model).where(self.model.id == id)
        result = await session.execute(stmt)
        return result.rowcount > 0