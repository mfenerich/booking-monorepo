"""Hotel service module for business logic."""

import json
import math
import os
from typing import Dict, List, Tuple, Union

from booking_api import NotFoundError
from booking_db import transaction
from booking_shared_models.models import Hotel, HotelReview
from booking_shared_models.schemas import HotelReviewCreate
from sqlalchemy.ext.asyncio import AsyncSession

from .repository import (
    hotel_benefit_repository,
    hotel_image_repository,
    hotel_repository,
    hotel_review_repository,
)


async def get_hotel_by_code(session: AsyncSession, hotel_code: int) -> Hotel:
    """
    Get hotel by hotel_code.

    Args:
        session: Database session
        hotel_code: Code of the hotel to retrieve

    Returns:
        Hotel with images, benefits, and reviews

    Raises:
        NotFoundError: If hotel with the given code does not exist
    """
    hotel = await hotel_repository.get_by_hotel_code(session, hotel_code)
    if not hotel:
        raise NotFoundError(f"Hotel with code {hotel_code} not found")

    return hotel


async def list_hotels(
    session: AsyncSession,
    filters: Dict[str, Union[str, List[str], Dict[str, str]]],
    advanced_filters: List[Dict[str, str]],
    page: int = 1,
    page_size: int = 6,
) -> Tuple[List[Hotel], int, Dict]:
    """
    List hotels with filters and pagination.

    Args:
        session: Database session
        filters: Filters to apply (city, star_ratings, price range)
        advanced_filters: Advanced filters like sorting options
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (list of hotels, total count, metadata)
    """
    # Extract filters
    city = filters.get("city", "")
    star_ratings = None
    if "star_ratings" in filters and filters["star_ratings"]:
        star_ratings = [float(r) for r in filters["star_ratings"]]

    # Extract price range
    price_min = None
    price_max = None
    if "priceFilter" in filters and filters["priceFilter"]:
        price_filter = filters["priceFilter"]
        if isinstance(price_filter, dict):
            price_min = float(price_filter.get("start", 0))
            price_max = float(price_filter.get("end", 100000))

    # Extract sorting
    sort_by = None
    if advanced_filters:
        for filter_item in advanced_filters:
            if "sortBy" in filter_item:
                sort_by = filter_item["sortBy"]
                break

    # Calculate skip for pagination
    skip = (page - 1) * page_size

    # Get hotels with filters
    hotels, total = await hotel_repository.list_hotels_with_filters(
        session=session,
        city=city if city else None,
        star_ratings=star_ratings,
        price_min=price_min,
        price_max=price_max,
        sort_by=sort_by,
        skip=skip,
        limit=page_size,
    )

    # Calculate total pages
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return (
        hotels,
        total,
        {
            "currentPage": page,
            "totalPages": total_pages,
            "pageSize": page_size,
            "totalResults": total,
        },
    )


async def get_hotel_reviews(
    session: AsyncSession, hotel_id: int, page: int = 1, page_size: int = 5
) -> Tuple[List[HotelReview], Dict, Dict]:
    """
    Get reviews for a hotel with pagination and metadata.

    Args:
        session: Database session
        hotel_id: Hotel ID
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (list of reviews, metadata, pagination info)
    """
    # Calculate skip for pagination
    skip = (page - 1) * page_size

    # Get reviews with pagination
    reviews, total = await hotel_repository.get_hotel_reviews(
        session=session,
        hotel_id=hotel_id,
        skip=skip,
        limit=page_size,
    )

    # Get review statistics
    avg_rating, total_reviews, star_counts = (
        await hotel_review_repository.get_review_stats(
            session=session,
            hotel_id=hotel_id,
        )
    )

    # Calculate total pages
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    # Create metadata
    metadata = {
        "totalReviews": total_reviews,
        "averageRating": f"{avg_rating:.1f}",
        "starCounts": star_counts,
    }

    # Create pagination info
    pagination = {
        "currentPage": page,
        "totalPages": total_pages,
        "pageSize": page_size,
    }

    return reviews, metadata, pagination


async def add_hotel_review(
    session: AsyncSession, hotel_id: int, review_data: HotelReviewCreate
) -> HotelReview:
    """
    Add a review for a hotel.

    Args:
        session: Database session
        hotel_id: Hotel ID
        review_data: Review data

    Returns:
        Created review

    Raises:
        NotFoundError: If hotel with the given ID does not exist
    """
    # Check if hotel exists
    hotel = await hotel_repository.get(session, hotel_id)
    if not hotel:
        raise NotFoundError(f"Hotel with ID {hotel_id} not found")

    # Create review with transaction
    async with transaction(session):
        review = await hotel_review_repository.create(
            session,
            {
                "hotel_id": hotel_id,
                "reviewer_name": review_data.reviewer_name,
                "rating": review_data.rating,
                "review": review_data.review,
                "date": review_data.date,
                "verified": review_data.verified,
            },
        )

    return review


async def get_available_cities(session: AsyncSession) -> List[str]:
    """
    Get list of available cities.

    Args:
        session: Database session

    Returns:
        List of city names
    """
    return await hotel_repository.get_available_cities(session)


async def seed_hotels_from_data(session: AsyncSession) -> int:
    """
    Seed hotels from JSON data files.

    Args:
        session: Database session

    Returns:
        Number of hotels seeded
    """
    # Define path to JSON data
    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
    )
    hotels_file = os.path.join(
        base_dir, "frontend", "src", "mirage", "data", "hotels.json"
    )

    # Check if file exists
    if not os.path.exists(hotels_file):
        print(f"Hotels data file not found at {hotels_file}")
        return 0

    # Load hotels data
    with open(hotels_file, "r") as f:
        hotels_data = json.load(f)

    # Keep track of seeded hotels
    seeded_count = 0

    # Seed hotels with transaction
    async with transaction(session):
        for hotel_data in hotels_data:
            # Check if hotel already exists
            existing_hotel = await hotel_repository.get_by_hotel_code(
                session, hotel_data["hotelCode"]
            )
            if existing_hotel:
                continue

            # Create hotel
            hotel = await hotel_repository.create(
                session,
                {
                    "hotel_code": hotel_data["hotelCode"],
                    "title": hotel_data["title"],
                    "subtitle": hotel_data["subtitle"],
                    "city": hotel_data["city"],
                    "price": float(hotel_data["price"]),
                    "ratings": float(hotel_data["ratings"]),
                },
            )

            # Create hotel images
            for image_data in hotel_data["images"]:
                await hotel_image_repository.create(
                    session,
                    {
                        "hotel_id": hotel.id,
                        "image_url": image_data["imageUrl"],
                        "accessible_text": image_data["accessibleText"],
                    },
                )

            # Create hotel benefits
            for benefit in hotel_data["benefits"]:
                await hotel_benefit_repository.create(
                    session,
                    {
                        "hotel_id": hotel.id,
                        "benefit": benefit,
                    },
                )

            # Create hotel reviews if they exist
            if (
                "reviews" in hotel_data
                and hotel_data["reviews"]
                and "data" in hotel_data["reviews"]
            ):
                for review_data in hotel_data["reviews"]["data"]:
                    await hotel_review_repository.create(
                        session,
                        {
                            "hotel_id": hotel.id,
                            "reviewer_name": review_data["reviewerName"],
                            "rating": review_data["rating"],
                            "review": review_data["review"],
                            "date": review_data["date"],
                            "verified": review_data.get("verified", False),
                        },
                    )

            seeded_count += 1

    return seeded_count
