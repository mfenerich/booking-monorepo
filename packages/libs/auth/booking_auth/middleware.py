from typing import Optional

from booking_api.exceptions import UnauthorizedError
from fastapi import Depends

from .security import JWTAuth
from .token import TokenData, TokenSettings, decode_access_token

# Create instance of custom security scheme
jwt_scheme = JWTAuth()


def get_token_settings() -> TokenSettings:
    """Get token settings from the auth config."""
    from .config import JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY

    return TokenSettings(
        secret_key=JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
        access_token_expire_minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    )


async def get_current_user(
    token: Optional[str] = Depends(jwt_scheme),
    settings: TokenSettings = Depends(get_token_settings),
) -> TokenData:
    """
    Verify JWT token and extract user information.
    """
    if not token:
        raise UnauthorizedError("Authentication required")

    try:
        token_data = decode_access_token(token, settings)
        return token_data
    except Exception:
        raise UnauthorizedError("Invalid or expired token")
