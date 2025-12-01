"""Request/Response schemas."""

from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    """Product creation schema."""

    title: str
    source: str
    source_id: str
    asin: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[Decimal] = None
    currency: str = "USD"
    rating: Optional[Decimal] = None
    review_count: int = 0
    description: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    availability: Optional[str] = None


class ProductResponse(BaseModel):
    """Product response schema."""

    id: UUID
    title: str
    source: str
    source_id: str
    asin: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[Decimal] = None
    currency: str = "USD"
    rating: Optional[Decimal] = None
    review_count: int
    description: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    availability: Optional[str] = None
    is_detailed_fetched: bool = False
    reviews_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    """Review creation schema."""

    product_id: UUID
    source: str
    source_review_id: Optional[str] = None
    author: Optional[str] = None
    rating: Optional[Decimal] = None
    review_text: Optional[str] = None
    review_title: Optional[str] = None
    verified_purchase: bool = False
    helpful_count: int = 0
    image_urls: Optional[List[str]] = None
    posted_at: Optional[datetime] = None
    sentiment: Optional[str] = None


class ReviewResponse(BaseModel):
    """Review response schema."""

    id: UUID
    product_id: UUID
    source: str
    source_review_id: Optional[str] = None
    author: Optional[str] = None
    rating: Optional[Decimal] = None
    review_text: Optional[str] = None
    review_title: Optional[str] = None
    verified_purchase: bool
    helpful_count: int
    image_urls: Optional[List[str]] = None
    posted_at: Optional[datetime] = None
    fetched_at: datetime
    sentiment: Optional[str] = None

    class Config:
        from_attributes = True


class VideoCreate(BaseModel):
    """Video creation schema."""

    product_id: UUID
    video_id: str
    title: Optional[str] = None
    channel_name: Optional[str] = None
    channel_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    published_at: Optional[datetime] = None
    description: Optional[str] = None
    video_url: Optional[str] = None


class VideoResponse(BaseModel):
    """Video response schema."""

    id: UUID
    product_id: UUID
    video_id: str
    title: Optional[str] = None
    channel_name: Optional[str] = None
    channel_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    published_at: Optional[datetime] = None
    description: Optional[str] = None
    video_url: Optional[str] = None
    fetched_at: datetime

    class Config:
        from_attributes = True


class ProductDetailResponse(BaseModel):
    """Complete product details response."""

    id: UUID
    title: str
    source: str
    source_id: str
    asin: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[Decimal] = None
    currency: str = "USD"
    rating: Optional[Decimal] = None
    review_count: int
    description: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    availability: Optional[str] = None
    reviews_summary: Optional[str] = None
    reviews: List[ReviewResponse] = Field(default_factory=list)
    videos: List[VideoResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """Search request schema."""

    query: str
    sources: List[str] = Field(default=["amazon", "walmart", "google_shopping"])
    limit: int = Field(default=20, le=100)
    min_rating: Optional[float] = Field(default=None, ge=0, le=5)
    max_price: Optional[float] = Field(default=None, gt=0)


class SearchResponse(BaseModel):
    """Search response schema."""

    success: bool
    query: str
    total_results: int
    results: List[ProductResponse] = Field(default_factory=list)


class ReviewsRequest(BaseModel):
    """Fetch reviews request schema."""

    sources: List[str] = Field(default=["amazon", "reddit", "youtube"])
    force_refresh: bool = False


class ReviewsResponse(BaseModel):
    """Fetch reviews response schema."""

    success: bool
    product_id: UUID
    total_reviews: int
    reviews: List[ReviewResponse] = Field(default_factory=list)


class VideosRequest(BaseModel):
    """Fetch videos request schema."""

    force_refresh: bool = False
    min_views: int = Field(default=0, ge=0)


class VideosResponse(BaseModel):
    """Fetch videos response schema."""

    success: bool
    product_id: UUID
    total_videos: int
    videos: List[VideoResponse] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Error response schema."""

    success: bool = False
    error: str
    details: Optional[dict] = None
