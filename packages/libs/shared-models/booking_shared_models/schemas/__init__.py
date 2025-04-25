"""Schema validation models package."""

from .user import User, UserBase, UserCreate, UserInDB, UserUpdate
from .hotel import (
    Hotel,
    HotelBase,
    HotelCreate,
    HotelInList,
    HotelDetailed,
    HotelImage,
    HotelImageBase,
    HotelImageCreate,
    HotelBenefit,
    HotelBenefitBase,
    HotelBenefitCreate,
    HotelReview,
    HotelReviewBase,
    HotelReviewCreate,
    HotelBookingEnquiry,
    HotelReviewsResponse,
    ReviewMetadata,
    ReviewPagination,
)

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
