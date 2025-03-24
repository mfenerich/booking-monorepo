import logging

from booking_api import UnauthorizedError
from booking_api.responses import SuccessResponse
from booking_auth import TokenSettings, create_access_token, verify_password
from booking_auth.dependencies import get_authenticated_user_id
from booking_auth.middleware import get_token_settings
from booking_auth.token import set_access_token_cookie
from booking_db import get_db
from booking_shared_models.schemas import User as UserSchema
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from booking_users.schemas import AuthStatusResponse, LoginRequest, LoginResponse
from booking_users.services.user_service import get_user, get_user_by_email

# Set up logging
logger = logging.getLogger(__name__)


router = APIRouter(prefix="/users", tags=["auth"])


@router.get(
    "/auth-user",
    response_model=SuccessResponse[AuthStatusResponse],
    summary="Check Authentication Status",
    description="Return the current authentication status and user details if authenticated.",
)
async def check_auth_status(
    user_id: int = Depends(get_authenticated_user_id),
    session: AsyncSession = Depends(get_db),
) -> SuccessResponse[AuthStatusResponse]:
    try:
        user = UserSchema.model_validate(await get_user(session, user_id))
        logger.info("Authentication check successful for user ID: %d", user_id)
        auth_status = AuthStatusResponse(isAuthenticated=True, userDetails=user)
        return SuccessResponse(message="User authenticated", data=auth_status)
    except Exception:
        logger.error("Error retrieving user details for user ID: %d", user_id)
        auth_status = AuthStatusResponse(isAuthenticated=False, userDetails=None)
        return SuccessResponse(message="Authentication failed", data=auth_status)


@router.post(
    "/login",
    response_model=SuccessResponse[LoginResponse],
    summary="User Login",
    description="Authenticate a user with email and password and return a JWT token.",
)
async def login(
    credentials: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_db),
    token_settings: TokenSettings = Depends(get_token_settings),
) -> SuccessResponse[LoginResponse]:
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

    # Set JWT cookie
    set_access_token_cookie(
        response=response,
        token=access_token,
        settings=token_settings,
    )
    logger.info("User logged in successfully: %s", credentials.email)
    return SuccessResponse(message="Logged in.", data=LoginResponse(token=access_token))


@router.post(
    "/logout",
    response_model=SuccessResponse[str],
    summary="User Logout",
    description="Clears the JWT token cookie to log out the user.",
)
async def logout(response: Response) -> SuccessResponse[str]:
    """
    Logout endpoint that clears the JWT token cookie.
    """
    # Replace "access_token" with the actual cookie key if it differs
    response.delete_cookie(key="access_token")
    logger.info("User logged out successfully")
    return SuccessResponse(message="Logged out.", data="User logged out.")
