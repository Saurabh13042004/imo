"""Additional product-related models."""
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models import Base


class PriceComparison(Base):
    """Price comparisons across retailers."""
    __tablename__ = 'price_comparisons'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    retailer = Column(String, nullable=False)
    price = Column(Numeric, nullable=False)
    url = Column(String)
    availability = Column(String)
    shipping = Column(String)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship('Product', back_populates='price_comparisons')


class ProductLike(Base):
    """Product likes by users."""
    __tablename__ = 'product_likes'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    product = relationship('Product', back_populates='product_likes')
