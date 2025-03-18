"""User service module for business logic."""

from booking_api import ConflictError
from booking_auth import get_password_hash
from booking_db import transaction
from booking_shared_models.schemas import User as UserSchema
from booking_shared_models.schemas import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession

from .repository import user_repository


async def register_user(session: AsyncSession, user_data: UserCreate) -> UserSchema:
    """
    Register a new user.

    Args:
        session: Database session
        user_data: User data for registration

    Returns:
        User schema with created user data

    Raises:
        ConflictError: If user with the same email or username already exists
    """
    # Check if email already exists
    existing_email = await user_repository.get_by_email(session, user_data.email)
    if existing_email:
        raise ConflictError("User with this email already exists")

    # Check if username already exists
    existing_username = await user_repository.get_by_username(
        session, user_data.username
    )
    if existing_username:
        raise ConflictError("User with this username already exists")

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create user with transaction
    async with transaction(session):
        user = await user_repository.create(
            session,
            {
                "email": user_data.email,
                "username": user_data.username,
                "hashed_password": hashed_password,
                "is_active": True,
            },
        )

    # Convert to schema and return
    return UserSchema.from_orm(user)
