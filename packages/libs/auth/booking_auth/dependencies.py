from booking_api.exceptions import UnauthorizedError
from fastapi import Depends

from .middleware import get_current_user, jwt_scheme
from .token import TokenData
from .user_provider import UserInfoProvider


async def get_authenticated_user_id(
    token_data: TokenData = Depends(get_current_user),
) -> int:
    """
    Simple dependency that returns just the authenticated user ID
    """
    return int(token_data.sub)


async def get_authenticated_user_info(
    token_data: TokenData = Depends(get_current_user), token: str = Depends(jwt_scheme)
) -> dict:
    """Get full authenticated user information"""
    provider = UserInfoProvider.from_settings()
    user_info = await provider.get_user_by_id(token_data.sub, token)

    if not user_info:
        raise UnauthorizedError("User not found or access denied")

    # Add token claims to user info if needed
    user_info.update(token_data.additional_claims or {})

    return user_info
