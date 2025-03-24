import logging

from booking_api import UnauthorizedError
from booking_auth import TokenSettings, create_access_token, verify_password
from booking_auth.dependencies import get_authenticated_user_id
from booking_auth.middleware import get_token_settings
from booking_db import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from booking_users.schemas import AuthStatusResponse, LoginRequest, LoginResponse
from booking_users.services.user_service import get_user, get_user_by_email

# Set up logging
logger = logging.getLogger(__name__)


router = APIRouter(prefix="/users", tags=["auth"])


@router.get(
    "/auth-user",
    response_model=AuthStatusResponse,
    summary="Check Authentication Status",
    description="Return the current authentication status and user details if authenticated.",
)
async def check_auth_status(
    user_id: int = Depends(get_authenticated_user_id),
    session: AsyncSession = Depends(get_db),
) -> AuthStatusResponse:
    """
    Check the current authentication status and return user details if authenticated.

    Args:
        user_id (int): The ID of the authenticated user (injected via dependency).
        session (AsyncSession): Database session dependency.

    Returns:
        AuthStatusResponse: A response containing the authentication status and user details.
    """
    try:
        user = await get_user(session, user_id)
        logger.info("Authentication check successful for user ID: %d", user_id)
        return AuthStatusResponse(isAuthenticated=True, userDetails=user)
    except Exception:
        logger.error("Error retrieving user details for user ID: %d", user_id)
        return AuthStatusResponse(isAuthenticated=False, userDetails=None)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User Login",
    description="Authenticate a user with email and password and return a JWT token.",
)
async def login(
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_db),
    token_settings: TokenSettings = Depends(get_token_settings),
) -> LoginResponse:
    """
    Authenticate a user using their email and password and return an access token.

    Args:
        credentials (LoginRequest): The login credentials containing email and password.
        session (AsyncSession): Database session dependency.
        token_settings (TokenSettings): Token generation settings dependency.

    Raises:
        UnauthorizedError: If the user is not found, the password is invalid, or the account is disabled.

    Returns:
        LoginResponse: A response model containing the JWT token and token type.
    """
    try:
        user = await get_user_by_email(session, credentials.email)
    except Exception:
        logger.warning(
            "Login failed: User with email '%s' not found.", credentials.email
        )
        raise UnauthorizedError("Invalid email or password")

    if not verify_password(credentials.password, user.hashed_password):
        logger.warning(
            "Login failed: Incorrect password for email '%s'.", credentials.email
        )
        raise UnauthorizedError("Invalid email or password")

    if not user.is_active:
        logger.warning(
            "Login failed: Account disabled for email '%s'.", credentials.email
        )
        raise UnauthorizedError("Account is disabled")

    access_token = create_access_token(
        subject=str(user.id),
        settings=token_settings,
        additional_claims={"email": user.email, "username": user.username},
    )
    logger.info("User logged in successfully: %s", credentials.email)
    return LoginResponse(token=access_token)
