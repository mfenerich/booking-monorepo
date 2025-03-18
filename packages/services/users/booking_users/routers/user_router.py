"""User router for API endpoints."""

from booking_api import SuccessResponse
from booking_db import get_db
from booking_shared_models.schemas import User, UserCreate
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..services import register_user

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
