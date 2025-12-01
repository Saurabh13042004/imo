"""Review model."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import Column, String, Numeric, Integer, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid

from app.models import Base


class Review(Base):
    """Review database model."""

    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    source = Column(String(50), nullable=False)  # 'amazon', 'reddit', 'youtube', 'forum'
    source_review_id = Column(String(200), nullable=True)
    author = Column(String(200), nullable=True)
    rating = Column(Numeric(3, 2), nullable=True)
    review_text = Column(Text, nullable=True)
    review_title = Column(String(500), nullable=True)
    verified_purchase = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    image_urls = Column(ARRAY(String), nullable=True)
    posted_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    sentiment = Column(String(20), nullable=True)  # 'positive', 'negative', 'neutral'

    # Relationships
    product = relationship("Product", back_populates="reviews")

    __table_args__ = (
        Index("idx_reviews_product", "product_id"),
        Index("idx_reviews_source", "source"),
        Index("idx_reviews_product_source", "product_id", "source", "source_review_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Review(id={self.id}, product_id={self.product_id}, source={self.source})>"
