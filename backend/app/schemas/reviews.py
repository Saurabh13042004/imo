"""Schemas for review APIs."""

from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID


class ReviewItem(BaseModel):
    """Single review item."""
    text: str
    confidence: Optional[float] = None
    rating: Optional[float] = None
    store: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None


class CommunityReviewSummary(BaseModel):
    """Summary of community reviews."""
    overall_sentiment: str  # positive, mixed, negative
    common_praises: List[str] = []
    common_complaints: List[str] = []


class CommunityReviewResponse(BaseModel):
    """Response for community reviews API."""
    success: bool
    product_id: UUID
    source: str = "community"
    summary: CommunityReviewSummary
    reviews: List[ReviewItem]
    total_found: int


class StoreSummary(BaseModel):
    """Summary of store reviews."""
    average_rating: float
    trust_score: float
    verified_patterns: dict  # {positive: [], negative: []}


class StoreReviewResponse(BaseModel):
    """Response for store reviews API."""
    success: bool
    product_id: UUID
    source: str = "store"
    summary: StoreSummary
    reviews: List[ReviewItem]
    total_found: int


# Stateless API Request Schemas
class CommunityReviewRequest(BaseModel):
    """Request for stateless community reviews API."""
    product_name: str
    brand: Optional[str] = None


class StoreReviewRequest(BaseModel):
    """Request for stateless store reviews API."""
    product_name: str
    store_urls: List[str]