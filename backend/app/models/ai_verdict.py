"""AI Verdict model for storing generated product verdicts."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, Text, DateTime, Boolean, Index, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import uuid

from app.models import Base


class AIVerdict(Base):
    """AI Verdict database model for storing Gemini-generated product verdicts."""

    __tablename__ = "ai_verdicts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Verdict data (from Gemini analysis)
    imo_score = Column(Float, nullable=False)  # 0-10 scale
    summary = Column(Text, nullable=False)
    pros = Column(JSON, nullable=False, default=list)  # List[str]
    cons = Column(JSON, nullable=False, default=list)  # List[str]
    who_should_buy = Column(Text, nullable=True)
    who_should_avoid = Column(Text, nullable=True)
    deal_breakers = Column(JSON, nullable=False, default=list)  # List[str]
    
    # Metadata
    verdict_type = Column(String(50), nullable=False, default="product")  # 'product', 'quick_scan', etc
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_ai_verdicts_product_id", "product_id"),
        Index("idx_ai_verdicts_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AIVerdict(product_id={self.product_id}, imo_score={self.imo_score})>"
