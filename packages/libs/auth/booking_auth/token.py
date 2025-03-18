"""JWT token handling utilities."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import jwt
from pydantic import BaseModel


class TokenSettings(BaseModel):
    """Settings for JWT token generation and validation."""

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


class TokenData(BaseModel):
    """Model for token payload data."""

    sub: str  # User ID
    exp: datetime
    additional_claims: Optional[Dict[str, Any]] = None


def create_access_token(
    subject: str,
    settings: TokenSettings,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        subject: Subject of the token (usually user_id)
        settings: Token settings including secret key and algorithm
        expires_delta: Optional expiration time delta
        additional_claims: Optional additional claims to include in the token

    Returns:
        JWT token as string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode = {"sub": subject, "exp": expire}

    if additional_claims:
        to_encode.update(additional_claims)

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str, settings: TokenSettings) -> TokenData:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token to decode
        settings: Token settings including secret key and algorithm

    Returns:
        TokenData object with the decoded data

    Raises:
        JWTError: If token is invalid or expired
    """
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

    additional_claims = {k: v for k, v in payload.items() if k not in ["sub", "exp"]}

    return TokenData(
        sub=payload["sub"],
        exp=datetime.fromtimestamp(payload["exp"]),
        additional_claims=additional_claims or None,
    )
