from datetime import datetime, timedelta
from typing import Optional

from fastapi import Response


def set_jwt_cookie(
    response: Response,
    token: str,
    expires_delta: Optional[timedelta] = None,
    secure: bool = True,
    httponly: bool = True,
    samesite: str = "lax",
):
    """Set JWT token as HTTP-only cookie."""
    if not expires_delta:
        expires = datetime.utcnow() + timedelta(minutes=30)
    else:
        expires = datetime.utcnow() + expires_delta

    response.set_cookie(
        key="access_token",
        value=token,
        expires=expires.timestamp(),
        path="/",
        secure=secure,  # Only send over HTTPS
        httponly=httponly,  # Not accessible via JavaScript
        samesite=samesite,  # CSRF protection
    )


def clear_jwt_cookie(response: Response):
    """Clear JWT cookie by setting it to expire immediately."""
    response.delete_cookie(key="access_token", path="/")
