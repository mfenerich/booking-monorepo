"""Schema validation models package."""

from .hotel import (
    Hotel,
    HotelBase,
    HotelBenefit,
    HotelBenefitBase,
    HotelBenefitCreate,
    HotelBookingEnquiry,
    HotelCreate,
    HotelDetailed,
    HotelImage,
    HotelImageBase,
    HotelImageCreate,
    HotelInList,
    HotelReview,
    HotelReviewBase,
    HotelReviewCreate,
    HotelReviewsResponse,
    ReviewMetadata,
    ReviewPagination,
)
from .user import User, UserBase, UserCreate, UserInDB, UserUpdate

__all__ = [
    # User schemas
    "User",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    # Hotel schemas
    "Hotel",
    "HotelBase",
    "HotelCreate",
    "HotelInList",
    "HotelDetailed",
    "HotelImage",
    "HotelImageBase",
    "HotelImageCreate",
    "HotelBenefit",
    "HotelBenefitBase",
    "HotelBenefitCreate",
    "HotelReview",
    "HotelReviewBase",
    "HotelReviewCreate",
    "HotelBookingEnquiry",
    "HotelReviewsResponse",
    "ReviewMetadata",
    "ReviewPagination",
]
