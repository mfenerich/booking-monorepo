from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class HotelImageBase(BaseModel):
    """Base schema for hotel images."""
    
    image_url: str
    accessible_text: Optional[str] = None


class HotelImageCreate(HotelImageBase):
    """Schema for creating hotel images."""
    
    pass


class HotelImage(HotelImageBase):
    """Schema for API responses with hotel images."""
    
    id: int
    hotel_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class HotelBenefitBase(BaseModel):
    """Base schema for hotel benefits."""
    
    benefit: str


class HotelBenefitCreate(HotelBenefitBase):
    """Schema for creating hotel benefits."""
    
    pass


class HotelBenefit(HotelBenefitBase):
    """Schema for API responses with hotel benefits."""
    
    id: int
    hotel_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class HotelReviewBase(BaseModel):
    """Base schema for hotel reviews."""
    
    reviewer_name: str
    rating: float
    review: str
    date: Optional[str] = None
    verified: bool = False


class HotelReviewCreate(HotelReviewBase):
    """Schema for creating hotel reviews."""
    
    pass


class HotelReview(HotelReviewBase):
    """Schema for API responses with hotel reviews."""
    
    id: int
    hotel_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class HotelBase(BaseModel):
    """Base schema for hotels."""
    
    title: str
    subtitle: Optional[str] = None
    city: str
    price: float
    ratings: Optional[float] = None
    hotel_code: int


class HotelCreate(HotelBase):
    """Schema for creating hotels."""
    
    images: List[HotelImageCreate] = []
    benefits: List[HotelBenefitCreate] = []
    reviews: List[HotelReviewCreate] = []


class Hotel(HotelBase):
    """Schema for API responses with hotels."""
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    images: List[HotelImage] = []
    benefits: List[str] = []
    reviews: Optional[List[HotelReview]] = None
    
    model_config = ConfigDict(from_attributes=True)


class HotelInList(BaseModel):
    """Schema for hotels in list responses, matching the frontend expected format."""
    
    hotelCode: int = Field(..., alias="hotel_code")
    title: str
    subtitle: Optional[str] = None
    price: str  # Price formatted as string
    ratings: str  # Ratings formatted as string
    city: str
    images: List[HotelImageBase]
    benefits: List[str]
    
    model_config = ConfigDict(from_attributes=True)


class HotelDetailed(HotelInList):
    """Schema for detailed hotel responses, including reviews."""
    
    description: List[str] = []
    reviews: Optional[dict] = None
    
    model_config = ConfigDict(from_attributes=True)


class HotelBookingEnquiry(BaseModel):
    """Schema for hotel booking enquiry responses."""
    
    name: str
    cancellationPolicy: str = "Free cancellation 1 day prior to stay"
    checkInTime: str = "12:00 PM"
    checkOutTime: str = "10:00 AM"
    currentNightRate: float
    maxGuestsAllowed: int = 5
    maxRoomsAllowedPerGuest: int = 3
    
    model_config = ConfigDict(from_attributes=True)


class HotelReviewsResponse(BaseModel):
    """Schema for paginated reviews response."""
    
    elements: List[HotelReview]
    
    model_config = ConfigDict(from_attributes=True)


class ReviewMetadata(BaseModel):
    """Schema for review metadata."""
    
    totalReviews: int
    averageRating: str
    starCounts: dict
    
    model_config = ConfigDict(from_attributes=True)


class ReviewPagination(BaseModel):
    """Schema for review pagination."""
    
    currentPage: int
    totalPages: int
    pageSize: int
    
    model_config = ConfigDict(from_attributes=True)
