"""User router for API endpoints."""

from booking_api import PaginatedResponse, SuccessResponse
from booking_auth.dependencies import get_authenticated_user_id
from booking_db import get_db
from booking_shared_models.schemas import User, UserCreate, UserUpdate
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

# Create router
router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register",
    response_model=SuccessResponse[User],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user with email, username, and password",
)
async def register(
    user_data: UserCreate, session: AsyncSession = Depends(get_db)
) -> SuccessResponse[User]:
    """Register a new user endpoint."""
    user = await register_user(session, user_data)
    return SuccessResponse(message="User registered successfully", data=user)


@router.get(
    "/{user_id}",
    response_model=SuccessResponse[User],
    summary="Get user by ID",
    description="Retrieve a user by their ID",
)
async def get_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_db),
    _: int = Depends(get_authenticated_user_id),
) -> SuccessResponse[User]:
    """Get user by ID endpoint."""
    user = await get_user(session, user_id)
    return SuccessResponse(message="User retrieved successfully", data=user)


@router.get(
    "/by-email/{email}",
    response_model=SuccessResponse[User],
    summary="Get user by email",
    description="Retrieve a user by their email address",
)
async def get_by_email(
    email: EmailStr,
    session: AsyncSession = Depends(get_db),
    _: int = Depends(get_authenticated_user_id),
) -> SuccessResponse[User]:
    """Get user by email endpoint."""
    user = await get_user_by_email(session, email)
    return SuccessResponse(message="User retrieved successfully", data=user)


@router.get(
    "/by-username/{username}",
    response_model=SuccessResponse[User],
    summary="Get user by username",
    description="Retrieve a user by their username",
)
async def get_by_username(
    username: str,
    session: AsyncSession = Depends(get_db),
    _: int = Depends(get_authenticated_user_id),
) -> SuccessResponse[User]:
    """Get user by username endpoint."""
    user = await get_user_by_username(session, username)
    return SuccessResponse(message="User retrieved successfully", data=user)


@router.get(
    "/",
    response_model=PaginatedResponse[User],
    summary="List users",
    description="Retrieve a paginated list of users",
)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of records to return"
    ),
    session: AsyncSession = Depends(get_db),
    _: int = Depends(get_authenticated_user_id),
) -> PaginatedResponse[User]:
    """List users endpoint."""
    users, total = await list_users(session, skip=skip, limit=limit)
    return PaginatedResponse(
        message="Users retrieved successfully",
        items=users,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        total=total,
    )


@router.put(
    "/{user_id}",
    response_model=SuccessResponse[User],
    summary="Update user",
    description="Update a user's information by their ID",
)
async def update_user_by_id(
    user_id: int,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_db),
    _: int = Depends(get_authenticated_user_id),
) -> SuccessResponse[User]:
    """Update user endpoint."""
    user = await update_user(session, user_id, user_data)
    return SuccessResponse(message="User updated successfully", data=user)


@router.delete(
    "/{user_id}",
    response_model=SuccessResponse,
    summary="Delete user",
    description="Delete a user by their ID",
)
async def delete_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_db),
    _: int = Depends(get_authenticated_user_id),
) -> SuccessResponse:
    """Delete user endpoint."""
    await delete_user(session, user_id)
    return SuccessResponse(message="User deleted successfully")
