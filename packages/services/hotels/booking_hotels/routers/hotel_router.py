"""Hotel router for API endpoints."""

import json
import logging

from booking_api import SuccessResponse
from booking_api.responses import PaginatedResponse
from booking_db import get_db
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas import (AddReviewRequest, HotelBookingDetailsResponse,
                       HotelDetailedResponse, HotelListItem,
                       HotelReviewsDetailedResponse)
from ..services import (add_hotel_review, get_available_cities,
                        get_hotel_by_code, get_hotel_reviews, list_hotels)

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["hotels"])


@router.get(
    "/hotels",
    response_model=PaginatedResponse[HotelListItem],
    summary="List Hotels",
    description="Retrieve a paginated list of hotels with filtering and sorting options.",
)
async def get_hotels(
    filters: str = Query("{}"),
    advancedFilters: str = Query("[]"),
    currentPage: int = Query(1, ge=1),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[HotelListItem]:
    """
    Get a list of hotels with filtering options.

    Args:
        filters: JSON string of filter criteria (city, star_ratings, etc.)
        advancedFilters: JSON string of advanced filter options (sorting, etc.)
        currentPage: Current page number (1-indexed)
        session: Database session dependency

    Returns:
        PaginatedResponse with hotels list, metadata, and pagination info
    """
    try:
        # Parse filters
        filters_dict = json.loads(filters)
        advanced_filters = json.loads(advancedFilters)

        # Get hotels
        hotels, total, pagination = await list_hotels(
            session=session,
            filters=filters_dict,
            advanced_filters=advanced_filters,
            page=currentPage,
            page_size=6,  # Hardcoded to match frontend expectation
        )

        # Convert to response format
        hotels_list = []
        for hotel in hotels:
            # Format price and ratings as strings to match frontend expectations
            price = f"{hotel.price}"
            ratings = f"{hotel.ratings}"

            # Get benefits as list of strings
            benefits = [benefit.benefit for benefit in hotel.benefits]

            # Create hotel list item
            hotel_item = HotelListItem(
                hotelCode=hotel.hotel_code,
                title=hotel.title,
                subtitle=hotel.subtitle,
                price=price,
                ratings=ratings,
                city=hotel.city,
                images=[{
                    "imageUrl": image.image_url,
                    "accessibleText": image.accessible_text
                } for image in hotel.images],
                benefits=benefits,
            )
            hotels_list.append(hotel_item)

        # Create a proper PaginatedResponse object
        return PaginatedResponse(
            message="Hotels retrieved successfully",
            items=hotels_list,
            page=pagination["currentPage"],
            page_size=pagination["pageSize"],
            total=total
        )
    except Exception as e:
        logger.error(f"Error listing hotels: {str(e)}")
        raise


@router.get(
    "/hotel/{hotelId}",
    response_model=SuccessResponse[HotelDetailedResponse],
    summary="Get Hotel Details",
    description="Retrieve detailed information about a specific hotel.",
)
async def get_hotel_detail(
    hotelId: int,
    session: AsyncSession = Depends(get_db),
) -> SuccessResponse[HotelDetailedResponse]:
    """
    Get detailed information about a specific hotel.

    Args:
        hotelId: The hotel code
        session: Database session dependency

    Returns:
        SuccessResponse with hotel details
    """
    try:
        # Get hotel by code
        hotel = await get_hotel_by_code(session, hotelId)

        # Format response
        benefits = [benefit.benefit for benefit in hotel.benefits]
        
        # Default description (to match frontend expectation)
        description = [
            "A serene stay awaits at our plush hotel, offering a blend of luxury and comfort with top-notch amenities.",
            "Experience the pinnacle of elegance in our beautifully designed rooms with stunning cityscape views.",
            "Indulge in gastronomic delights at our in-house restaurants, featuring local and international cuisines.",
            "Unwind in our state-of-the-art spa and wellness center, a perfect retreat for the senses.",
            "Located in the heart of the city, our hotel is the ideal base for both leisure and business travelers.",
        ]

        # Create detailed response
        hotel_detail = HotelDetailedResponse(
            hotelCode=hotel.hotel_code,
            title=hotel.title,
            subtitle=hotel.subtitle,
            price=str(hotel.price),
            ratings=str(hotel.ratings),
            city=hotel.city,
            images=[{
                "imageUrl": image.image_url,
                "accessibleText": image.accessible_text
            } for image in hotel.images],
            benefits=benefits,
            description=description,
        )

        return SuccessResponse(
            message="Hotel details retrieved successfully",
            data=hotel_detail
        )
    except Exception as e:
        logger.error(f"Error getting hotel details: {str(e)}")
        raise


@router.get(
    "/hotel/{hotelId}/booking/enquiry",
    response_model=SuccessResponse[HotelBookingDetailsResponse],
    summary="Get Hotel Booking Details",
    description="Retrieve booking information for a specific hotel.",
)
async def get_hotel_booking_details(
    hotelId: int,
    session: AsyncSession = Depends(get_db),
) -> SuccessResponse[HotelBookingDetailsResponse]:
    """
    Get booking information for a specific hotel.

    Args:
        hotelId: The hotel code
        session: Database session dependency

    Returns:
        SuccessResponse with hotel booking details
    """
    try:
        # Get hotel by code
        hotel = await get_hotel_by_code(session, hotelId)

        # Create booking details response
        booking_details = HotelBookingDetailsResponse(
            name=hotel.title,
            cancellationPolicy="Free cancellation 1 day prior to stay",
            checkInTime="12:00 PM",
            checkOutTime="10:00 AM",
            currentNightRate=float(hotel.price),
            maxGuestsAllowed=5,
            maxRoomsAllowedPerGuest=3,
        )

        return SuccessResponse(
            message="Hotel booking details retrieved successfully",
            data=booking_details
        )
    except Exception as e:
        logger.error(f"Error getting hotel booking details: {str(e)}")
        raise


@router.get(
    "/hotel/{hotelId}/reviews",
    response_model=SuccessResponse,
    summary="Get Hotel Reviews",
    description="Retrieve reviews for a specific hotel with pagination.",
)
async def get_hotel_review_list(
    hotelId: int,
    currentPage: int = Query(1, ge=1),
    session: AsyncSession = Depends(get_db),
) -> SuccessResponse:
    """
    Get reviews for a specific hotel with pagination.

    Args:
        hotelId: The hotel code
        currentPage: Current page number (1-indexed)
        session: Database session dependency

    Returns:
        SuccessResponse with hotel reviews, metadata, and pagination info
    """
    try:
        # Get hotel by code (to get hotel ID)
        hotel = await get_hotel_by_code(session, hotelId)

        # Get reviews with pagination and metadata
        reviews, metadata, pagination = await get_hotel_reviews(
            session=session,
            hotel_id=hotel.id,
            page=currentPage,
            page_size=5,  # Hardcoded to match frontend expectation
        )

        # Convert to response format
        reviews_list = []
        for review in reviews:
            review_item = {
                "reviewerName": review.reviewer_name,
                "rating": review.rating,
                "review": review.review,
                "date": review.date,
                "verified": review.verified,
            }
            reviews_list.append(review_item)

        return SuccessResponse(
            message="Hotel reviews retrieved successfully",
            data={
                "elements": reviews_list,
                "metadata": metadata,
                "paging": pagination
            }
        )
    except Exception as e:
        logger.error(f"Error getting hotel reviews: {str(e)}")
        raise


@router.put(
    "/hotel/add-review",
    response_model=SuccessResponse,
    summary="Add Hotel Review",
    description="Add a new review for a hotel.",
)
async def add_review(
    review_data: AddReviewRequest,
    session: AsyncSession = Depends(get_db),
) -> SuccessResponse:
    """
    Add a new review for a hotel.

    Args:
        review_data: Review data
        session: Database session dependency

    Returns:
        SuccessResponse confirming the review addition
    """
    try:
        # Get hotel by code
        hotel = await get_hotel_by_code(session, review_data.hotelId)

        # Add review
        await add_hotel_review(
            session=session,
            hotel_id=hotel.id,
            review_data={
                "reviewer_name": review_data.reviewerName,
                "rating": review_data.rating,
                "review": review_data.review,
                "date": f"Date of stay: {review_data.date}",
                "verified": False,  # New reviews start as unverified
            },
        )

        return SuccessResponse(
            message="Review added successfully",
            data={
                "status": "Review added successfully"
            }
        )
    except Exception as e:
        logger.error(f"Error adding hotel review: {str(e)}")
        raise


@router.get(
    "/availableCities",
    response_model=SuccessResponse,
    summary="Get Available Cities",
    description="Retrieve a list of available cities for hotel filtering.",
)
async def get_cities(
    session: AsyncSession = Depends(get_db),
) -> SuccessResponse:
    """
    Get a list of available cities.

    Args:
        session: Database session dependency

    Returns:
        SuccessResponse with list of cities
    """
    try:
        # Get available cities
        cities = await get_available_cities(session)

        return SuccessResponse(
            message="Available cities retrieved successfully",
            data={
                "elements": cities
            }
        )
    except Exception as e:
        logger.error(f"Error getting available cities: {str(e)}")
        raise


@router.get(
    "/hotels/verticalFilters",
    response_model=SuccessResponse,
    summary="Get Filter Options",
    description="Retrieve filter options for hotel search.",
)
async def get_filter_options() -> SuccessResponse:
    """
    Get filter options for hotel search.

    Returns:
        SuccessResponse with filter options
    """
    try:
        # Static filter options to match frontend expectation
        filters = [
            {
                "filterId": "star_ratings",
                "title": "Star ratings",
                "filters": [
                    {
                        "id": "5_star_rating",
                        "title": "5 Star",
                        "value": "5",
                    },
                    {
                        "id": "4_star_rating",
                        "title": "4 Star",
                        "value": "4",
                    },
                    {
                        "id": "3_star_rating",
                        "title": "3 Star",
                        "value": "3",
                    },
                ],
            },
            {
                "filterId": "propety_type",
                "title": "Property type",
                "filters": [
                    {
                        "id": "prop_type_hotel",
                        "title": "Hotel",
                    },
                    {
                        "id": "prop_type_apartment",
                        "title": "Apartment",
                    },
                    {
                        "id": "prop_type_villa",
                        "title": "Villa",
                    },
                ],
            },
        ]

        return SuccessResponse(
            message="Filter options retrieved successfully",
            data={
                "elements": filters
            }
        )
    except Exception as e:
        logger.error(f"Error getting filter options: {str(e)}")
        raise


@router.get(
    "/nearbyHotels",
    response_model=SuccessResponse,
    summary="Get Nearby Hotels",
    description="Retrieve a list of nearby hotels (currently returns hotels in Pune).",
)
async def get_nearby_hotels(
    session: AsyncSession = Depends(get_db),
) -> SuccessResponse:
    """
    Get a list of nearby hotels (currently returns hotels in Pune).

    Args:
        session: Database session dependency

    Returns:
        SuccessResponse with list of nearby hotels
    """
    try:
        # Get hotels in Pune (to match frontend expectation)
        hotels, _, _ = await list_hotels(
            session=session,
            filters={"city": "pune"},
            advanced_filters=[],
            page=1,
            page_size=10,
        )

        # Convert to response format
        hotels_list = []
        for hotel in hotels:
            # Format price and ratings as strings to match frontend expectations
            price = f"{hotel.price}"
            ratings = f"{hotel.ratings}"

            # Get benefits as list of strings
            benefits = [benefit.benefit for benefit in hotel.benefits]

            # Create hotel list item
            hotel_item = HotelListItem(
                hotelCode=hotel.hotel_code,
                title=hotel.title,
                subtitle=hotel.subtitle,
                price=price,
                ratings=ratings,
                city=hotel.city,
                images=[{
                    "imageUrl": image.image_url,
                    "accessibleText": image.accessible_text
                } for image in hotel.images],
                benefits=benefits,
            )
            hotels_list.append(hotel_item)

        return SuccessResponse(
            message="Nearby hotels retrieved successfully",
            data={
                "elements": hotels_list
            }
        )
    except Exception as e:
        logger.error(f"Error getting nearby hotels: {str(e)}")
        raise


@router.get(
    "/popularDestinations",
    response_model=SuccessResponse,
    summary="Get Popular Destinations",
    description="Retrieve a list of popular destinations.",
)
async def get_popular_destinations() -> SuccessResponse:
    """
    Get a list of popular destinations.

    Returns:
        SuccessResponse with list of popular destinations
    """
    try:
        # Static popular destinations to match frontend expectation
        destinations = [
            {
                "code": 1211,
                "name": "Mumbai",
                "imageUrl": "/images/cities/mumbai.jpg",
            },
            {
                "code": 1212,
                "name": "Bangkok",
                "imageUrl": "/images/cities/bangkok.jpg",
            },
            {
                "code": 1213,
                "name": "London",
                "imageUrl": "/images/cities/london.jpg",
            },
            {
                "code": 1214,
                "name": "Dubai",
                "imageUrl": "/images/cities/dubai.jpg",
            },
            {
                "code": 1215,
                "name": "Oslo",
                "imageUrl": "/images/cities/oslo.jpg",
            },
        ]

        return SuccessResponse(
            message="Popular destinations retrieved successfully",
            data={
                "elements": destinations
            }
        )
    except Exception as e:
        logger.error(f"Error getting popular destinations: {str(e)}")
        raise
