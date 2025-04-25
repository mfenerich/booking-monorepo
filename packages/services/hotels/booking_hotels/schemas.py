"""Schema definitions for the hotels service."""

from typing import Dict, List, Optional

from pydantic import BaseModel


class HotelImageResponse(BaseModel):
    """Schema for hotel image in API responses."""

    imageUrl: str
    accessibleText: Optional[str] = None


class HotelListItem(BaseModel):
    """Schema for hotel in list responses."""

    hotelCode: int
    title: str
    subtitle: Optional[str] = None
    price: str  # Price as string (e.g., "18900")
    ratings: str  # Ratings as string (e.g., "5")
    city: str
    images: List[HotelImageResponse]
    benefits: List[str]


class HotelDetailedResponse(HotelListItem):
    """Schema for detailed hotel response."""

    description: List[str]
    reviews: Optional[Dict] = None


class HotelBookingDetailsResponse(BaseModel):
    """Schema for hotel booking enquiry response."""

    name: str
    cancellationPolicy: str = "Free cancellation 1 day prior to stay"
    checkInTime: str = "12:00 PM"
    checkOutTime: str = "10:00 AM"
    currentNightRate: float
    maxGuestsAllowed: int = 5
    maxRoomsAllowedPerGuest: int = 3


class AddReviewRequest(BaseModel):
    """Schema for adding a review."""

    hotelId: int
    reviewerName: str
    rating: float
    review: str
    date: str


class HotelReviewResponse(BaseModel):
    """Schema for hotel review in API responses."""

    reviewerName: str
    rating: float
    review: str
    date: Optional[str] = None
    verified: bool = False


class HotelReviewsResponse(BaseModel):
    """Schema for paginated hotel reviews response."""

    elements: List[HotelReviewResponse]


class HotelReviewsDetailedResponse(BaseModel):
    """Schema for detailed hotel reviews response, including metadata and pagination."""

    elements: List[HotelReviewResponse]
    metadata: Dict
    paging: Dict
