"""User and authentication related models."""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models import Base


class Profile(Base):
    """User profiles."""
    __tablename__ = 'profiles'

    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    password_hash = Column(String, nullable=True)
    avatar_url = Column(String)
    oauth_provider = Column(String, nullable=True)
    oauth_provider_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    subscription_tier = Column(String, default='free')
    access_level = Column(String, default='basic')

    # Relationships
    subscriptions = relationship('Subscription', back_populates='user')
    payment_transactions = relationship('PaymentTransaction', back_populates='user')
    search_unlocks = relationship('SearchUnlock', back_populates='user')
    price_alerts = relationship('PriceAlert', back_populates='user')


class UserRole(Base):
    """User roles."""
    __tablename__ = 'user_roles'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    role = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
