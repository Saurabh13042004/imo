"""Background task models."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func

from app.models import Base


class BackgroundAnalysisTask(Base):
    """Background analysis tasks."""
    __tablename__ = 'background_analysis_tasks'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    query_hash = Column(String, nullable=False)
    page = Column(Integer, nullable=False)
    status = Column(String, default='running', nullable=False)
    products_analyzed = Column(Integer, default=0)
    total_products = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    heartbeat_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
