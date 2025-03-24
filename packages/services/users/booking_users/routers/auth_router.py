import logging

from booking_api import NotFoundError, UnauthorizedError
from booking_auth import TokenSettings, create_access_token, verify_password
from booking_auth.middleware import get_token_settings
from booking_db import get_db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from booking_users.schemas import LoginResponse

from ..services import get_user_by_username

# Set up logging
logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    username: str
    password: str


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User Login",
    description="Authenticate a user and return a JWT token.",
)
async def login(
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_db),
    token_settings: TokenSettings = Depends(get_token_settings),
) -> LoginResponse:
    """
    Authenticate a user using their username and password, and return an access token if successful.

    Parameters:
        credentials (LoginRequest): The login credentials containing the username and password.
        session (AsyncSession): The database session dependency.
        token_settings (TokenSettings): Configuration settings for token generation.

    Raises:
        UnauthorizedError: If the user is not found, the password is invalid, or the account is disabled.

    Returns:
        LoginResponse: A response model containing the JWT token and token type.
    """
    # Attempt to retrieve the user by username
    try:
        user = await get_user_by_username(session, credentials.username)
    except NotFoundError:
        logger.warning(
            "Failed login attempt: User not found for username: %s",
            credentials.username,
        )
        raise UnauthorizedError("Invalid username or password")

    # Validate the password
    if not verify_password(credentials.password, user.hashed_password):
        logger.warning(
            "Failed login attempt: Incorrect password for username: %s",
            credentials.username,
        )
        raise UnauthorizedError("Invalid username or password")

    # Ensure the account is active
    if not user.is_active:
        logger.warning(
            "Failed login attempt: Account disabled for username: %s",
            credentials.username,
        )
        raise UnauthorizedError("Account is disabled")

    # Create a JWT token with additional claims
    access_token = create_access_token(
        subject=str(user.id),
        settings=token_settings,
        additional_claims={"username": user.username, "email": user.email},
    )

    return LoginResponse(token=access_token)
