from booking_api import NotFoundError, UnauthorizedError
from booking_auth import TokenSettings, create_access_token, verify_password
from booking_auth.middleware import get_token_settings
from booking_db import get_db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..services import get_user_by_username


# Define login request model
class LoginRequest(BaseModel):
    username: str
    password: str


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_db),
    token_settings: TokenSettings = Depends(get_token_settings),
):
    """
    Simple login endpoint that accepts username and password and returns JWT
    """
    # Authenticate user - get the USER MODEL, not schema
    try:
        user = await get_user_by_username(session, credentials.username)
    except NotFoundError:  # Catch specific exception instead of bare except
        raise UnauthorizedError("Invalid username or password")

    # Verify password - the user is now a model with hashed_password field
    if not verify_password(credentials.password, user.hashed_password):
        raise UnauthorizedError("Invalid username or password")

    # Check if user is active
    if not user.is_active:
        raise UnauthorizedError("Account is disabled")

    # Create token with user information
    access_token = create_access_token(
        subject=str(user.id),
        settings=token_settings,
        additional_claims={"username": user.username, "email": user.email},
    )

    return {"access_token": access_token, "token_type": "bearer"}
