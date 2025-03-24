from typing import Optional

from booking_shared_models.schemas.user import User
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"


class AuthStatusResponse(BaseModel):
    isAuthenticated: bool
    userDetails: Optional[User] = None
