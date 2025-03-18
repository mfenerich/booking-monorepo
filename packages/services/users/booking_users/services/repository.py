"""User repository module."""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from booking_db import Repository
from booking_shared_models.models import User


class UserRepository(Repository[User]):
    """Repository for User model operations."""
    
    def __init__(self):
        """Initialize with User model."""
        super().__init__(User)
    
    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        """Get a user by email."""
        return await self.get_by(session, email=email)
    
    async def get_by_username(self, session: AsyncSession, username: str) -> Optional[User]:
        """Get a user by username."""
        return await self.get_by(session, username=username)


# Single instance
user_repository = UserRepository()