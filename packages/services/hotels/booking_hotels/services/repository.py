"""Hotel repository module."""

from typing import List, Optional, Tuple

from booking_db import Repository
from booking_shared_models.models import Hotel, HotelBenefit, HotelImage, HotelReview
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class HotelRepository(Repository[Hotel]):
    """Repository for Hotel model operations."""

    def __init__(self):
        """Initialize with Hotel model."""
        super().__init__(Hotel)

    async def get_by_hotel_code(
        self, session: AsyncSession, hotel_code: int
    ) -> Optional[Hotel]:
        """Get a hotel by hotel_code with images, benefits, and reviews."""
        stmt = (
            select(Hotel)
            .where(Hotel.hotel_code == hotel_code)
            .options(
                selectinload(Hotel.images),
                selectinload(Hotel.benefits),
                selectinload(Hotel.reviews),
            )
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    async def list_hotels_with_filters(
        self,
        session: AsyncSession,
        city: Optional[str] = None,
        star_ratings: Optional[List[float]] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        sort_by: Optional[str] = None,
        skip: int = 0,
        limit: int = 6,
    ) -> Tuple[List[Hotel], int]:
        """
        List hotels with filters.

        Args:
            session: Database session
            city: Filter by city
            star_ratings: Filter by star ratings
            price_min: Filter by minimum price
            price_max: Filter by maximum price
            sort_by: Sort by criteria (e.g., "price_asc", "price_desc")
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of hotels, total count)
        """
        # Create base query
        stmt = select(Hotel).options(
            selectinload(Hotel.images),
            selectinload(Hotel.benefits),
        )

        # Apply filters
        if city:
            stmt = stmt.where(func.lower(Hotel.city) == city.lower())

        if star_ratings:
            # Check if hotel rating is close to any of the selected ratings
            rating_conditions = [
                func.abs(Hotel.ratings - rating) <= 0.5 for rating in star_ratings
            ]
            if rating_conditions:
                from sqlalchemy import or_

                stmt = stmt.where(or_(*rating_conditions))

        if price_min is not None:
            stmt = stmt.where(Hotel.price >= price_min)

        if price_max is not None:
            stmt = stmt.where(Hotel.price <= price_max)

        # Apply sorting
        if sort_by:
            if sort_by == "priceLowToHigh":
                stmt = stmt.order_by(Hotel.price.asc())
            elif sort_by == "priceHighToLow":
                stmt = stmt.order_by(Hotel.price.desc())

        # Count total results before pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await session.scalar(count_stmt)

        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)

        # Execute query
        result = await session.execute(stmt)
        hotels = result.scalars().all()

        return list(hotels), total

    async def get_hotel_reviews(
        self, session: AsyncSession, hotel_id: int, skip: int = 0, limit: int = 5
    ) -> Tuple[List[HotelReview], int]:
        """
        Get reviews for a hotel with pagination.

        Args:
            session: Database session
            hotel_id: Hotel ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of reviews, total count)
        """
        # Get total count
        count_stmt = select(func.count(HotelReview.id)).where(
            HotelReview.hotel_id == hotel_id
        )
        total = await session.scalar(count_stmt)

        # Get paginated reviews
        stmt = (
            select(HotelReview)
            .where(HotelReview.hotel_id == hotel_id)
            .order_by(HotelReview.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        reviews = result.scalars().all()

        return list(reviews), total

    async def get_available_cities(self, session: AsyncSession) -> List[str]:
        """
        Get list of available cities.

        Args:
            session: Database session

        Returns:
            List of city names
        """
        stmt = select(Hotel.city).distinct()
        result = await session.execute(stmt)
        cities = result.scalars().all()
        return list(cities)


class HotelImageRepository(Repository[HotelImage]):
    """Repository for HotelImage model operations."""

    def __init__(self):
        """Initialize with HotelImage model."""
        super().__init__(HotelImage)


class HotelBenefitRepository(Repository[HotelBenefit]):
    """Repository for HotelBenefit model operations."""

    def __init__(self):
        """Initialize with HotelBenefit model."""
        super().__init__(HotelBenefit)


class HotelReviewRepository(Repository[HotelReview]):
    """Repository for HotelReview model operations."""

    def __init__(self):
        """Initialize with HotelReview model."""
        super().__init__(HotelReview)

    async def get_review_stats(
        self, session: AsyncSession, hotel_id: int
    ) -> Tuple[float, int, dict]:
        """
        Get review statistics for a hotel.

        Args:
            session: Database session
            hotel_id: Hotel ID

        Returns:
            Tuple of (average rating, total reviews, star counts)
        """
        # Get total reviews and average rating
        stmt = select(func.count(HotelReview.id), func.avg(HotelReview.rating)).where(
            HotelReview.hotel_id == hotel_id
        )
        result = await session.execute(stmt)
        total_reviews, avg_rating = result.one()

        # Get star counts
        star_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for i in range(1, 6):
            stmt = select(func.count(HotelReview.id)).where(
                HotelReview.hotel_id == hotel_id, func.floor(HotelReview.rating) == i
            )
            result = await session.execute(stmt)
            star_counts[i] = result.scalar() or 0

        return avg_rating or 0, total_reviews or 0, star_counts


# Single instances
hotel_repository = HotelRepository()
hotel_image_repository = HotelImageRepository()
hotel_benefit_repository = HotelBenefitRepository()
hotel_review_repository = HotelReviewRepository()
