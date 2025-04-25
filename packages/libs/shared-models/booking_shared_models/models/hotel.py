from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .user import Base


class Hotel(Base):
    """Hotel model for storing hotel details."""

    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    hotel_code = Column(Integer, unique=True, index=True, nullable=False)
    title = Column(String, index=True, nullable=False)
    subtitle = Column(String, nullable=True)
    city = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    ratings = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    images = relationship("HotelImage", back_populates="hotel", cascade="all, delete-orphan")
    benefits = relationship("HotelBenefit", back_populates="hotel", cascade="all, delete-orphan")
    reviews = relationship("HotelReview", back_populates="hotel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Hotel(id={self.id}, title={self.title}, city={self.city})>"


class HotelImage(Base):
    """Hotel image model for storing hotel images."""

    __tablename__ = "hotel_images"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String, nullable=False)
    accessible_text = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    hotel = relationship("Hotel", back_populates="images")

    def __repr__(self):
        return f"<HotelImage(id={self.id}, hotel_id={self.hotel_id})>"


class HotelBenefit(Base):
    """Hotel benefit model for storing hotel benefits."""

    __tablename__ = "hotel_benefits"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)
    benefit = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    hotel = relationship("Hotel", back_populates="benefits")

    def __repr__(self):
        return f"<HotelBenefit(id={self.id}, hotel_id={self.hotel_id}, benefit={self.benefit})>"


class HotelReview(Base):
    """Hotel review model for storing hotel reviews."""

    __tablename__ = "hotel_reviews"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)
    reviewer_name = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    review = Column(Text, nullable=False)
    date = Column(String, nullable=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    hotel = relationship("Hotel", back_populates="reviews")

    def __repr__(self):
        return f"<HotelReview(id={self.id}, hotel_id={self.hotel_id}, rating={self.rating})>"
