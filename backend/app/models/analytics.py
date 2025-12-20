"""Analytics and logging related models."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, JSONB, INET
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func

from app.models import Base


class AnalyticsEvent(Base):
    """Analytics events."""
    __tablename__ = 'analytics_events'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(PG_UUID(as_uuid=True), index=True)
    event_name = Column(String, nullable=False)
    event_data = Column(JSONB, default={})
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    session_id = Column(String)
    user_agent = Column(String)
    ip_address = Column(INET)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ErrorLog(Base):
    """Error logs for debugging."""
    __tablename__ = 'error_logs'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    function_name = Column(String, nullable=False)
    error_type = Column(String, nullable=False)
    error_message = Column(String, nullable=False)
    error_details = Column(JSONB)
    query_context = Column(String)
    user_id = Column(PG_UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class UsageLog(Base):
    """Usage logs for tracking user activity."""
    __tablename__ = 'usage_logs'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    type = Column(String, nullable=False)
    count = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserInteraction(Base):
    """User interactions."""
    __tablename__ = 'user_interactions'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(PG_UUID(as_uuid=True), index=True)
    interaction_type = Column(String, nullable=False)
    content_type = Column(String)
    content_id = Column(String)
    metadata = Column(JSONB)
    session_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SubscriptionEvent(Base):
    """Subscription events."""
    __tablename__ = 'subscription_events'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(PG_UUID(as_uuid=True), index=True)
    event_type = Column(String, nullable=False)
    event_data = Column(JSONB)
    session_id = Column(String)
    user_agent = Column(String)
    ip_address = Column(String)
    referrer = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
