"""Subscription and payment related models."""
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Boolean, DateTime, Date, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models import Base


class Subscription(Base):
    """User subscriptions."""
    __tablename__ = 'subscriptions'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=False, index=True)
    plan_type = Column(String, nullable=False, default='free')  # free, trial, premium
    billing_cycle = Column(String, nullable=True)  # monthly, yearly
    is_active = Column(Boolean, default=False, nullable=False)
    subscription_start = Column(DateTime(timezone=True), server_default=func.now())
    subscription_end = Column(DateTime(timezone=True), nullable=True)
    trial_start = Column(DateTime(timezone=True), nullable=True)
    trial_end = Column(DateTime(timezone=True), nullable=True)
    stripe_customer_id = Column(String, unique=True, nullable=True)
    stripe_subscription_id = Column(String, unique=True, nullable=True)
    stripe_product_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship('Profile', back_populates='subscriptions')
    payment_transactions = relationship('PaymentTransaction', back_populates='subscription')


class PaymentTransaction(Base):
    """Payment transactions."""
    __tablename__ = 'payment_transactions'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=False, index=True)
    subscription_id = Column(PG_UUID(as_uuid=True), ForeignKey('subscriptions.id'), nullable=True)
    transaction_id = Column(String, unique=True, nullable=False)
    amount = Column(Numeric, nullable=False)
    currency = Column(String, default='usd')
    type = Column(String, nullable=False)  # subscription, one_time, refund
    status = Column(String, default='pending', nullable=False)  # pending, success, failed, refunded
    stripe_payment_intent_id = Column(String, unique=True, nullable=True)
    stripe_session_id = Column(String, nullable=True)
    metadata_json = Column(String, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship('Profile', back_populates='payment_transactions')
    subscription = relationship('Subscription', back_populates='payment_transactions')


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


class PriceAlert(Base):
    """Price alerts for products."""
    __tablename__ = 'price_alerts'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=True, index=True)  # nullable for non-authenticated users
    product_id = Column(String, nullable=False, index=True)
    product_name = Column(String, nullable=False)
    product_url = Column(String, nullable=False)
    target_price = Column(Numeric, nullable=False)
    current_price = Column(Numeric, nullable=True)
    currency = Column(String, default='usd')
    email = Column(String, nullable=False, index=True)  # Email for both authenticated and non-authenticated users
    is_active = Column(Boolean, default=True, nullable=False)
    alert_sent = Column(Boolean, default=False, nullable=False)
    alert_sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship('Profile', back_populates='price_alerts', foreign_keys=[user_id])


class DailySearchUsage(Base):
    """Track daily search usage for free users."""
    __tablename__ = 'daily_search_usage'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=True, index=True)  # nullable for guest users
    session_id = Column(String, nullable=True, index=True)  # For tracking guest users
    search_date = Column(Date, nullable=False, index=True)  # Date of search (without time)
    search_count = Column(Integer, default=0, nullable=False)  # Number of searches performed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Unique constraint: one record per user per day (or session per day for guests)
    __table_args__ = (
        # For registered users: unique by user_id + date
        # For guest users: unique by session_id + date
        {'schema': None}
    )

