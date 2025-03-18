"""User service module for business logic."""

from booking_api import ConflictError, NotFoundError
from booking_auth import get_password_hash
from booking_db import transaction
from booking_shared_models.schemas import User as UserSchema
from booking_shared_models.schemas import UserCreate, UserUpdate
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
    return UserSchema.model_validate(user)


async def get_user(session: AsyncSession, user_id: int) -> UserSchema:
    """
    Get user by ID.

    Args:
        session: Database session
        user_id: ID of the user to retrieve

    Returns:
        User schema with user data

    Raises:
        NotFoundError: If user with the given ID does not exist
    """
    user = await user_repository.get(session, user_id)
    if not user:
        raise NotFoundError(f"User with ID {user_id} not found")

    return UserSchema.model_validate(user)


async def get_user_by_email(session: AsyncSession, email: str) -> UserSchema:
    """
    Get user by email.

    Args:
        session: Database session
        email: Email of the user to retrieve

    Returns:
        User schema with user data

    Raises:
        NotFoundError: If user with the given email does not exist
    """
    user = await user_repository.get_by_email(session, email)
    if not user:
        raise NotFoundError(f"User with email {email} not found")

    return UserSchema.model_validate(user)


async def get_user_by_username(session: AsyncSession, username: str) -> UserSchema:
    """
    Get user by username.

    Args:
        session: Database session
        username: Username of the user to retrieve

    Returns:
        User schema with user data

    Raises:
        NotFoundError: If user with the given username does not exist
    """
    user_model = await user_repository.get_by_username(session, username)
    if not user_model:
        raise NotFoundError(f"User with username {username} not found")

    # Don't transform to schema yet, we need the hashed_password
    return user_model


async def list_users(
    session: AsyncSession, skip: int = 0, limit: int = 100
) -> tuple[list[UserSchema], int]:
    """
    List users with pagination.

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Tuple of (list of users, total count)
    """
    users = await user_repository.list(session, skip=skip, limit=limit)
    total = await user_repository.count(session)

    return [UserSchema.model_validate(user) for user in users], total


async def update_user(
    session: AsyncSession, user_id: int, user_data: UserUpdate
) -> UserSchema:
    """
    Update user.

    Args:
        session: Database session
        user_id: ID of the user to update
        user_data: User data for update

    Returns:
        Updated user schema

    Raises:
        NotFoundError: If user with the given ID does not exist
        ConflictError: If updating to an email or username that already exists
    """
    # Check if user exists
    existing_user = await user_repository.get(session, user_id)
    if not existing_user:
        raise NotFoundError(f"User with ID {user_id} not found")

    # Prepare update data
    update_data = {}

    # Update email if provided and different from current
    if user_data.email and user_data.email != existing_user.email:
        # Check if email already exists for another user
        email_user = await user_repository.get_by_email(session, user_data.email)
        if email_user and email_user.id != user_id:
            raise ConflictError("User with this email already exists")
        update_data["email"] = user_data.email

    # Update username if provided and different from current
    if user_data.username and user_data.username != existing_user.username:
        # Check if username already exists for another user
        username_user = await user_repository.get_by_username(
            session, user_data.username
        )
        if username_user and username_user.id != user_id:
            raise ConflictError("User with this username already exists")
        update_data["username"] = user_data.username

    # Update password if provided
    if user_data.password:
        update_data["hashed_password"] = get_password_hash(user_data.password)

    # Update active status if provided
    if user_data.is_active is not None:
        update_data["is_active"] = user_data.is_active

    # If no updates, return existing user
    if not update_data:
        return UserSchema.model_validate(existing_user)

    # Update user with transaction
    async with transaction(session):
        updated_user = await user_repository.update(session, user_id, update_data)
        if not updated_user:
            # This should not happen normally since we checked existence
            raise NotFoundError(f"User with ID {user_id} not found")

    return UserSchema.model_validate(updated_user)


async def delete_user(session: AsyncSession, user_id: int) -> bool:
    """
    Delete user.

    Args:
        session: Database session
        user_id: ID of the user to delete

    Returns:
        True if user was deleted, False otherwise

    Raises:
        NotFoundError: If user with the given ID does not exist
    """
    # Check if user exists
    existing_user = await user_repository.get(session, user_id)
    if not existing_user:
        raise NotFoundError(f"User with ID {user_id} not found")

    # Delete user with transaction
    async with transaction(session):
        result = await user_repository.delete(session, user_id)

    return result
