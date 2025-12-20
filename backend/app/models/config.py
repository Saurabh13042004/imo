"""Application configuration model."""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func

from app.models import Base


class AppConfig(Base):
    """Application configuration settings."""
    __tablename__ = 'app_config'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    config_key = Column(String, unique=True, nullable=False, index=True)
    config_value = Column(JSONB, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
