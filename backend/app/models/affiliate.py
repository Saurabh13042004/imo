"""Affiliate and tracking related models."""
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models import Base


class AffiliateClick(Base):
    """Affiliate click tracking."""
    __tablename__ = 'affiliate_clicks'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    subscription_status = Column(String, default='free')
    conversion_value = Column(Numeric, default=0)
    session_id = Column(String)

    # Relationships
    product = relationship('Product', back_populates='affiliate_clicks')
