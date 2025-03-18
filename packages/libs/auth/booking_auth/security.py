from typing import Optional

from fastapi import Request
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param


class JWTAuth(SecurityBase):
    """
    Custom security scheme that extracts a JWT Bearer token from the
    Authorization header without requiring client credentials.
    """

    def __init__(self, scheme_name: str = "JWT"):
        self.scheme_name = scheme_name
        # No tokenUrl means no login form displayed in docs
        self.model = {"type": "http", "scheme": "bearer"}

    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None

        scheme, token = get_authorization_scheme_param(authorization)
        if scheme.lower() != "bearer":
            return None

        return token
