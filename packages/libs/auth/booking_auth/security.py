from typing import Optional

from fastapi import Request
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param


class JWTAuth(SecurityBase):
    """
    Custom security scheme that extracts a JWT token from either:
    1. Authorization header (Bearer token)
    2. Cookie (access_token)
    """

    def __init__(self, scheme_name: str = "JWT", cookie_name: str = "access_token"):
        self.scheme_name = scheme_name
        self.cookie_name = cookie_name
        # No tokenUrl means no login form displayed in docs
        self.model = {"type": "http", "scheme": "bearer"}

    async def __call__(self, request: Request) -> Optional[str]:
        # First try to get token from Authorization header
        authorization = request.headers.get("Authorization")
        if authorization:
            scheme, token = get_authorization_scheme_param(authorization)
            if scheme.lower() == "bearer":
                return token

        # If not in header, try to get from cookie
        if self.cookie_name in request.cookies:
            return request.cookies[self.cookie_name]

        return None
