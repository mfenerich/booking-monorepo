"""User router for API endpoints."""

import logging

from booking_api import PaginatedResponse, SuccessResponse
from booking_auth.dependencies import get_authenticated_user_id
from booking_db import get_db
from booking_shared_models.schemas import User as UserSchema
from booking_shared_models.schemas import UserCreate, UserUpdate
from fastapi import APIRouter, Depends, Query, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from ..services import (
    delete_user,
    get_user,
    get_user_by_email,
    get_user_by_username,
    list_users,
    register_user,
    update_user,
)

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register",
    response_model=SuccessResponse[UserSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Register a New User",
    description="Register a new user with email, username, and password.",
)
async def register(
    user_data: UserCreate, session: AsyncSession = Depends(get_db)
) -> SuccessResponse[UserSchema]:
    """
    Register a new user in the system.

    Args:
        user_data (UserCreate): The registration details for the new user.
        session (AsyncSession): Database session dependency.

    Returns:
        SuccessResponse[User]: A response containing the registered user data.
    """
    user = UserSchema.model_validate(await register_user(session, user_data))
    logger.info("User registered successfully: %s", user.email)
    return SuccessResponse(message="User registered successfully", data=user)


@router.get(
    "/{user_id}",
    response_model=SuccessResponse[UserSchema],
    summary="Get User by ID",
    description="Retrieve a user by their ID.",
)
async def get_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_db),
    _: int = Depends(get_authenticated_user_id),
) -> SuccessResponse[UserSchema]:
    """
    Retrieve a user by their unique ID.

    Args:
        user_id (int): The unique identifier of the user.
        session (AsyncSession): Database session dependency.
        _ (int): Dependency for authentication (not used directly).

    Returns:
        SuccessResponse[User]: A response containing the user data.
    """
    user = UserSchema.model_validate(await get_user(session, user_id))
    logger.info("User retrieved successfully: ID %d", user_id)
    return SuccessResponse(message="User retrieved successfully", data=user)


@router.get(
    "/by-email/{email}",
    response_model=SuccessResponse[UserSchema],
    summary="Get User by Email",
    description="Retrieve a user by their email address.",
)
async def get_by_email(
    email: EmailStr,
    session: AsyncSession = Depends(get_db),
    _: int = Depends(get_authenticated_user_id),
) -> SuccessResponse[UserSchema]:
    """
    Retrieve a user by their email address.

    Args:
        email (EmailStr): The email address of the user.
        session (AsyncSession): Database session dependency.
        _ (int): Dependency for authentication (not used directly).

    Returns:
        SuccessResponse[User]: A response containing the user data.
    """
    user = UserSchema.model_validate(await get_user_by_email(session, email))
    logger.info("User retrieved by email successfully: %s", email)
    return SuccessResponse(message="User retrieved successfully", data=user)


@router.get(
    "/by-username/{username}",
    response_model=SuccessResponse[UserSchema],
    summary="Get User by Username",
    description="Retrieve a user by their username.",
)
async def get_by_username(
    username: str,
    session: AsyncSession = Depends(get_db),
    _: int = Depends(get_authenticated_user_id),
) -> SuccessResponse[UserSchema]:
    """
    Retrieve a user by their username.

    Args:
        username (str): The username of the user.
        session (AsyncSession): Database session dependency.
        _ (int): Dependency for authentication (not used directly).

    Returns:
        SuccessResponse[User]: A response containing the user data.
    """
    user = UserSchema.model_validate(await get_user_by_username(session, username))
    logger.info("User retrieved by username successfully: %s", username)
    return SuccessResponse(message="User retrieved successfully", data=user)


@router.get(
    "/",
    response_model=PaginatedResponse[UserSchema],
    summary="List Users",
    description="Retrieve a paginated list of users.",
)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip."),
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of records to return."
    ),
    session: AsyncSession = Depends(get_db),
    _: int = Depends(get_authenticated_user_id),
) -> PaginatedResponse[UserSchema]:
    """
    Retrieve a paginated list of users.

    Args:
        skip (int): The number of records to skip.
        limit (int): The maximum number of records to return.
        session (AsyncSession): Database session dependency.
        _ (int): Dependency for authentication (not used directly).

    Returns:
        PaginatedResponse[User]: A response containing a list of users along with pagination details.
    """
    users, total = await list_users(session, skip=skip, limit=limit)
    users = [UserSchema.model_validate(user) for user in users]
    page = skip // limit + 1 if limit > 0 else 1
    logger.info("Users listed: page %d, page size %d", page, limit)
    return PaginatedResponse(
        message="Users retrieved successfully",
        items=users,
        page=page,
        page_size=limit,
        total=total,
    )


@router.put(
    "/{user_id}",
    response_model=SuccessResponse[UserSchema],
    summary="Update User",
    description="Update a user's information by their ID.",
)
async def update_user_by_id(
    user_id: int,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_db),
    _: int = Depends(get_authenticated_user_id),
) -> SuccessResponse[UserSchema]:
    """
    Update a user's information.

    Args:
        user_id (int): The unique identifier of the user to update.
        user_data (UserUpdate): The updated user information.
        session (AsyncSession): Database session dependency.
        _ (int): Dependency for authentication (not used directly).

    Returns:
        SuccessResponse[User]: A response containing the updated user data.
    """
    user = UserSchema.model_validate(await update_user(session, user_id, user_data))
    logger.info("User updated successfully: ID %d", user_id)
    return SuccessResponse(message="User updated successfully", data=user)


@router.delete(
    "/{user_id}",
    response_model=SuccessResponse,
    summary="Delete User",
    description="Delete a user by their ID.",
)
async def delete_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_db),
    _: int = Depends(get_authenticated_user_id),
) -> SuccessResponse:
    """
    Delete a user from the system.

    Args:
        user_id (int): The unique identifier of the user to delete.
        session (AsyncSession): Database session dependency.
        _ (int): Dependency for authentication (not used directly).

    Returns:
        SuccessResponse: A response confirming the successful deletion of the user.
    """
    await delete_user(session, user_id)
    logger.info("User deleted successfully: ID %d", user_id)
    return SuccessResponse(message="User deleted successfully")
