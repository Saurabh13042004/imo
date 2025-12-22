"""Product model."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, String, Numeric, Integer, Text, DateTime, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid

from app.models import Base


class Product(Base):
    """Product database model."""

    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False, index=True)
    source = Column(String(50), nullable=False)  # 'amazon', 'walmart', 'google_shopping'
    source_id = Column(String(200), nullable=False)
    asin = Column(String(20), nullable=True)  # Amazon specific
    url = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(10), default="USD")
    rating = Column(Numeric(3, 2), nullable=True)
    review_count = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    description_source = Column(String(50), nullable=True)
    description_quality_score = Column(Integer, nullable=True)
    description_fetched_at = Column(DateTime, nullable=True)
    brand = Column(String(200), nullable=True)
    category = Column(String(200), nullable=True)
    availability = Column(String(50), nullable=True)
    is_detailed_fetched = Column(Boolean, default=False)
    reviews_summary = Column(Text, nullable=True)
    # Google Shopping specific fields for immersive product details
    immersive_product_page_token = Column(Text, nullable=True)
    immersive_product_api_link = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="product", cascade="all, delete-orphan")
    affiliate_clicks = relationship("AffiliateClick", back_populates="product", cascade="all, delete-orphan")
    price_comparisons = relationship("PriceComparison", back_populates="product", cascade="all, delete-orphan")
    product_likes = relationship("ProductLike", back_populates="product", cascade="all, delete-orphan")
    user_reviews = relationship("UserReview", back_populates="product", cascade="all, delete-orphan")
    product_reviews = relationship("ProductReview", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_products_source_id", "source", "source_id", unique=True),
        Index("idx_products_title", "title"),
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, title={self.title}, source={self.source})>"
