"""Subscription and payment related models."""
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models import Base


class Subscription(Base):
    """User subscriptions."""
    __tablename__ = 'subscriptions'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=False, index=True)
    plan_type = Column(String, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    subscription_end = Column(DateTime(timezone=True))
    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    trial_end = Column(DateTime(timezone=True))

    # Relationships
    user = relationship('Profile', back_populates='subscriptions')


class PaymentTransaction(Base):
    """Payment transactions."""
    __tablename__ = 'payment_transactions'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=False, index=True)
    transaction_id = Column(String, unique=True, nullable=False)
    amount = Column(Numeric, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, default='pending', nullable=False)
    stripe_session_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship('Profile', back_populates='payment_transactions')


class SearchUnlock(Base):
    """Search query unlocks."""
    __tablename__ = 'search_unlocks'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=False, index=True)
    search_query = Column(String, nullable=False)
    unlock_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    payment_amount = Column(Numeric, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship('Profile', back_populates='search_unlocks')
