"""Request/Response schemas."""

from typing import List, Optional, Dict, Any
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
    immersive_product_page_token: Optional[str] = None
    immersive_product_api_link: Optional[str] = None


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
    # Google Shopping specific fields for immersive product details
    immersive_product_page_token: Optional[str] = None
    immersive_product_api_link: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

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
    """Search request schema with geo-targeting for SerpAPI."""

    keyword: str = Field(..., description="Search keyword (2-200 characters)")
    zipcode: Optional[str] = Field(default=None, description="Zipcode for legacy support (not used for SerpAPI geo-targeting)")
    
    # Geo-targeting for SerpAPI
    country: Optional[str] = Field(default="United States", description="Country for search results (e.g., 'India', 'United States')")
    city: Optional[str] = Field(default=None, description="City for narrower location targeting (e.g., 'Bengaluru')")
    
    # Language
    language: Optional[str] = Field(default="en", description="Language code for search interface (e.g., 'en', 'hi')")


class SearchResponse(BaseModel):
    """Search response schema."""

    success: bool
    keyword: str
    zipcode: Optional[str]
    country: Optional[str]
    city: Optional[str]
    language: Optional[str]
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


class EnrichedProductRequest(BaseModel):
    """Request for enriched product details from SerpAPI."""
    
    immersive_api_link: str = Field(..., description="SerpAPI immersive product API link")


class AIProductAnalysis(BaseModel):
    """AI-powered product analysis from Gemini."""
    
    summary: str = Field(..., description="1-2 sentence product summary")
    pros: List[str] = Field(default_factory=list, description="Top 5 pros")
    cons: List[str] = Field(default_factory=list, description="Top 5 cons")
    deal_breakers: List[str] = Field(default_factory=list, description="Deal-breaker issues")
    sentiment_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Overall sentiment 0-1")
    verdict_score: float = Field(default=5.0, ge=1.0, le=10.0, description="Verdict score 1-10")
    who_should_buy: str = Field(default="", description="Target customer types")
    who_should_avoid: str = Field(default="", description="Customer types to avoid")


class AmazonReview(BaseModel):
    """Amazon review from canonical source."""
    
    id: str
    author: str
    rating: int
    title: str
    content: str
    timestamp: str
    is_verified: bool
    helpful_count: int


class ExternalReview(BaseModel):
    """External review from SerpAPI (enrichment)."""
    
    source: str  # e.g., "reddit", "blog", "forum"
    author: str
    rating: Optional[float] = None
    title: str
    content: str


class AmazonProductAnalysis(BaseModel):
    """Complete Amazon product with all 3 layers: Data + Enrichment + Intelligence.
    
    This is the stable, unified JSON schema served to UI.
    Single source of truth per field (clearly marked).
    """
    
    # ============ LAYER 1: BASE DATA (Amazon = Canonical Truth) ============
    asin: str = Field(..., description="Amazon ASIN - unique product identifier")
    parent_asin: Optional[str] = Field(None, description="Parent ASIN for variants")
    title: str = Field(..., description="Product title from Amazon")
    brand: Optional[str] = Field(None, description="Brand from Amazon")
    manufacturer: Optional[str] = Field(None, description="Manufacturer from Amazon")
    
    # Images (from Amazon)
    images: List[str] = Field(default_factory=list, description="Product images from Amazon")
    
    # Description & Specs (from Amazon)
    bullet_points: str = Field(default="", description="Key features from Amazon")
    description: str = Field(default="", description="Full description from Amazon")
    category: Optional[List[Dict[str, Any]]] = Field(default=None, description="Product category from Amazon (array of category objects)")
    
    # Pricing (Amazon buybox is canonical for Amazon price)
    price: float = Field(default=0.0, description="Current Amazon price")
    price_strikethrough: Optional[float] = Field(None, description="Original price before discount")
    discount_percentage: Optional[int] = Field(None, description="Discount % from Amazon")
    currency: str = Field(default="USD")
    
    # Amazon offers/buybox (canonical for Amazon purchasing)
    buybox: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Amazon buybox offers with seller info"
    )
    
    # Variants (from Amazon)
    variants: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Available product variants from Amazon"
    )
    
    # Rating (from Amazon)
    rating: float = Field(default=0.0, description="Average rating from Amazon reviews")
    rating_distribution: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Rating breakdown % from Amazon (5★, 4★, etc)"
    )
    total_reviews: int = Field(default=0, description="Total review count from Amazon")
    
    # Sales rank (from Amazon)
    sales_rank: Optional[List[Dict[str, Any]]] = Field(None, description="Best seller rank from Amazon (array of rank objects)")
    sales_volume: Optional[str] = Field(None, description="Sales volume from Amazon")
    
    # ============ LAYER 2: REVIEWS (Separate by Source) ============
    
    # Amazon reviews (verified purchases, official platform)
    amazon_reviews: List[AmazonReview] = Field(
        default_factory=list,
        description="Top reviews from Amazon (canonical source)"
    )
    
    # External reviews (enrichment from SerpAPI)
    external_reviews: List[ExternalReview] = Field(
        default_factory=list,
        description="Reviews from external sources (blogs, forums, Reddit, etc) - enrichment only"
    )
    
    # ============ LAYER 2.5: ENRICHMENT DATA (SerpAPI) ============
    # Cross-store pricing and external ratings (enrichment only, supplements Amazon data)
    external_stores: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Cross-store pricing from SerpAPI (eBay, Walmart, etc) - enrichment only"
    )
    
    external_rating: Optional[float] = Field(
        None,
        description="External rating/review count aggregated from SerpAPI sources"
    )
    
    external_ratings_distribution: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="External rating breakdown from SerpAPI (5★, 4★, etc) - supplements Amazon ratings"
    )
    
    # ============ LAYER 3: INTELLIGENCE (Gemini Analysis) ============
    analysis: Optional[AIProductAnalysis] = Field(
        None,
        description="AI-generated analysis combining Amazon + external reviews (Gemini)"
    )
    
    # ============ METADATA ============
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class VideosResponse(BaseModel):
    """Fetch videos response schema."""

    success: bool
    product_id: UUID
    total_videos: int
    videos: List[VideoResponse] = Field(default_factory=list)


class AIVerdictRequest(BaseModel):
    """Request to generate AI verdict for a product."""
    
    enriched_data: Dict[str, Any] = Field(..., description="Full enriched product data from /product/enriched endpoint")
    scrape_stores: bool = Field(default=False, description="Whether to scrape store pages for additional insights")


class AIVerdictResponse(BaseModel):
    """AI verdict response schema."""
    
    id: UUID = Field(..., description="Verdict ID")
    product_id: UUID = Field(..., description="Product UUID")
    imo_score: float = Field(..., ge=0.0, le=10.0, description="IMO Score 0-10")
    summary: str = Field(..., description="Product verdict summary")
    pros: List[str] = Field(default_factory=list, description="Top pros")
    cons: List[str] = Field(default_factory=list, description="Top cons")
    who_should_buy: Optional[str] = Field(None, description="Target customer profile")
    who_should_avoid: Optional[str] = Field(None, description="Who should avoid this product")
    deal_breakers: List[str] = Field(default_factory=list, description="Deal-breaker issues")
    created_at: datetime = Field(..., description="When verdict was generated")
    
    class Config:
        from_attributes = True


class AIVerdictStatusResponse(BaseModel):
    """AI verdict processing status response."""
    
    status: str = Field(..., description="Status: 'processing', 'ready', or 'error'")
    verdict: Optional[AIVerdictResponse] = Field(None, description="Completed verdict (if ready)")
    message: Optional[str] = Field(None, description="Status message or error details")


class ErrorResponse(BaseModel):
    """Error response schema."""

    success: bool = False
    error: str
    details: Optional[dict] = None


