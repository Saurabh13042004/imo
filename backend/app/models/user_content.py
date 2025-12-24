"""User-generated content models."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, CheckConstraint, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models import Base


class UserReview(Base):
    """User-generated reviews."""
    __tablename__ = 'user_reviews'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    video_url = Column(String)
    title = Column(String, nullable=False)
    description = Column(String)
    rating = Column(Integer, nullable=False)
    status = Column(String, default='pending', nullable=False)  # 'pending', 'approved', 'rejected'
    s3_key = Column(String, nullable=True)  # S3 storage key for video
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    product = relationship('Product', back_populates='user_reviews')
    likes = relationship('Like', back_populates='review')
    comments = relationship('Comment', back_populates='review')

    __table_args__ = (
        CheckConstraint('(rating >= 1) AND (rating <= 5)', name='user_reviews_rating_check'),
    )


class Like(Base):
    """Likes on reviews."""
    __tablename__ = 'likes'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    review_id = Column(PG_UUID(as_uuid=True), ForeignKey('user_reviews.id'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    review = relationship('UserReview', back_populates='likes')


class Comment(Base):
    """Comments on reviews."""
    __tablename__ = 'comments'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    review_id = Column(PG_UUID(as_uuid=True), ForeignKey('user_reviews.id'), nullable=False, index=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    review = relationship('UserReview', back_populates='comments')


class ProductReview(Base):
    """Reviews for products from external sources."""
    __tablename__ = 'product_reviews'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    external_review_id = Column(String, unique=True, nullable=False)
    reviewer_name = Column(String)
    rating = Column(Integer, nullable=False)
    title = Column(String)
    review_text = Column(String)
    verified_purchase = Column(Boolean, default=False)
    review_date = Column(DateTime(timezone=True))
    positive_feedback = Column(Integer, default=0)
    negative_feedback = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    source = Column(String, default='Unknown')

    # Relationships
    product = relationship('Product')
