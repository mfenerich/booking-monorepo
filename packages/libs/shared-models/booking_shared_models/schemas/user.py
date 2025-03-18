from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    """Base User schema with common attributes."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    """User creation schema."""
    email: EmailStr
    username: str
    password: str

class UserUpdate(UserBase):
    """User update schema."""
    password: Optional[str] = None

class UserInDB(UserBase):
    """User schema as stored in the database."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    hashed_password: str

    class Config:
        from_attributes = True

class User(UserBase):
    """User schema for API responses (excludes sensitive data)."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True