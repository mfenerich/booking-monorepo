"""Standard API response models."""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Standard error response model."""

    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response model."""

    success: bool = True
    message: str
    data: Optional[T] = None


class PaginatedResponse(SuccessResponse, Generic[T]):
    """Standard paginated response model."""

    page: int
    page_size: int
    total: int
    items: List[T]
