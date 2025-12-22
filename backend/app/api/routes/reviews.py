"""Review and video routes."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Dict, Any, List

from app.schemas import (
    ReviewsRequest,
    ReviewsResponse,
    VideosRequest,
    VideosResponse,
    ErrorResponse,
    ReviewResponse,
    VideoResponse
)
from app.services import SearchService, ReviewService, VideoService, AIService
from app.api.dependencies import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["reviews"])

search_service = SearchService()
review_service = ReviewService()
video_service = VideoService()
ai_service = AIService()


@router.post(
    "/product/{product_id}/reviews",
    response_model=ReviewsResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def fetch_product_reviews(
    product_id: UUID,
    request: ReviewsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch and aggregate product reviews from multiple sources.

    - **product_id**: UUID of the product
    - **sources**: List of sources (amazon, reddit, youtube, forum)
    - **force_refresh**: Force fetch fresh data (bypass cache)
    """
    try:
        # Get product
        product = await search_service.get_product_by_id(db, str(product_id))

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        logger.info(f"Fetching reviews for product: {product_id}")

        # Fetch reviews
        reviews = await review_service.fetch_reviews(
            db,
            product,
            request.sources,
            request.force_refresh
        )

        # Convert to response models
        review_responses = [ReviewResponse.from_orm(r) for r in reviews]

        return ReviewsResponse(
            success=True,
            product_id=product_id,
            total_reviews=len(review_responses),
            reviews=review_responses
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching reviews: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reviews"
        )


@router.post(
    "/product/{product_id}/videos",
    response_model=VideosResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def fetch_product_videos(
    product_id: UUID,
    request: VideosRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch YouTube review videos for a product.

    - **product_id**: UUID of the product
    - **force_refresh**: Force fetch fresh data (bypass cache)
    - **min_views**: Minimum number of views for videos to include
    """
    try:
        # Get product
        product = await search_service.get_product_by_id(db, str(product_id))

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        logger.info(f"Fetching videos for product: {product_id}")

        # Fetch videos
        videos = await video_service.fetch_product_videos(
            db,
            product,
            request.force_refresh,
            request.min_views
        )

        # Convert to response models
        video_responses = [VideoResponse.from_orm(v) for v in videos]

        return VideosResponse(
            success=True,
            product_id=product_id,
            total_videos=len(video_responses),
            videos=video_responses
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching videos: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch videos"
        )


# Community Reviews API - Stateless
@router.post("/reviews/community")
async def get_community_reviews_stateless(
    body: Dict[str, Any] = Body(...)
):
    """
    Fetch and normalize community reviews from Reddit and forums.
    
    No database dependency - stateless operation.
    Uses SerpAPI for search and Gemini AI for normalization.
    
    Architecture:
    1. Search for product across Reddit and forums (forum-biased queries)
    2. Extract Reddit posts + top comments (ignore sidebar/nav)
    3. Extract forum discussions (ignore quoted replies/ads)
    4. Deduplicate near-identical reviews (>90% similarity)
    5. Validate reviews with AI (remove questions, specs, nav text)
    6. Normalize and extract sentiment/praises/complaints
    
    Request body:
    {
        "product_name": string (required),
        "brand": string (optional)
    }
    """
    from app.services.community_review_service import CommunityReviewService
    from app.services.ai_review_service import AIReviewService

    try:
        # Extract request parameters
        product_name = body.get("product_name")
        brand = body.get("brand", "")
        
        if not product_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="product_name is required"
            )
        
        logger.info(f"Fetching community reviews for: {product_name}")
        
        # Step 1: Fetch raw reviews from Reddit and forums
        community_service = CommunityReviewService()
        raw_data = await community_service.fetch_community_reviews(
            product_title=product_name,
            brand=brand
        )
        
        raw_reviews = raw_data.get("reviews", [])
        logger.info(f"Raw reviews fetched: {len(raw_reviews)}")
        
        # Step 2: Validate with AI (remove non-reviews)
        ai_service = AIReviewService()
        validation_result = await ai_service.validate_and_normalize_reviews(
            raw_reviews,
            context="community"
        )
        validated_reviews = validation_result.get("reviews", [])
        logger.info(f"Validated reviews: {len(validated_reviews)} (filtered {validation_result.get('filtered_count', 0)})")
        
        # Step 3: Normalize with AI
        normalized = await ai_service.normalize_community_reviews(validated_reviews)
        
        # Build response
        return {
            "success": True,
            "product_name": product_name,
            "source": "community",
            "summary": {
                "overall_sentiment": normalized.get("overall_sentiment", "neutral"),
                "common_praises": normalized.get("common_praises", []),
                "common_complaints": normalized.get("common_complaints", []),
            },
            "reviews": [
                {
                    "source": r.get("source", "unknown"),
                    "text": r.get("text", ""),
                    "confidence": r.get("validation_confidence", 1.0),
                }
                for r in validated_reviews[:20]
            ],
            "total_found": len(validated_reviews),
            "raw_count": len(raw_reviews),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching community reviews: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch community reviews: {str(e)}"
        )


# Store Reviews API - Stateless
@router.post("/reviews/store")
async def get_store_reviews_stateless(
    body: Dict[str, Any] = Body(...)
):
    """
    Fetch and normalize store reviews from retailer websites.
    
    No database dependency - stateless operation.
    Generically scrapes reviews and uses Gemini AI for normalization.
    
    Architecture:
    1. Fetch each store URL with httpx
    2. Detect if JS rendering needed (cookies, enable javascript, no review elements)
    3. If needed, render with Playwright/Selenium (limited to 2 per request)
    4. Extract review elements (avoid cookie banners, nav, headers, footers)
    5. Deduplicate exact and near-identical reviews (>90% similarity)
    6. Validate reviews with AI (remove non-reviews)
    7. Normalize and extract ratings/trust scores
    
    Request body:
    {
        "product_name": string,
        "store_urls": string[] (required - at least 1 URL)
    }
    """
    from app.services.store_review_service import StoreReviewService
    from app.services.ai_review_service import AIReviewService

    try:
        # Extract request parameters
        product_name = body.get("product_name")
        store_urls = body.get("store_urls", [])
        
        if not product_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="product_name is required"
            )
        
        if not store_urls or len(store_urls) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="store_urls is required (at least 1 URL)"
            )
        
        logger.info(f"Fetching store reviews for: {product_name} from {len(store_urls)} URLs")
        
        # Step 1: Fetch raw reviews from specified URLs
        store_service = StoreReviewService()
        raw_data = await store_service.fetch_store_reviews(store_urls)
        raw_reviews = raw_data.get("reviews", [])
        logger.info(f"Raw reviews fetched: {len(raw_reviews)}")
        
        # Step 2: Validate with AI (remove non-reviews, noise)
        ai_service = AIReviewService()
        validation_result = await ai_service.validate_and_normalize_reviews(
            raw_reviews,
            context="store"
        )
        validated_reviews = validation_result.get("reviews", [])
        logger.info(f"Validated reviews: {len(validated_reviews)} (filtered {validation_result.get('filtered_count', 0)})")
        
        # Step 3: Normalize with AI
        normalized = await ai_service.normalize_store_reviews(validated_reviews)
        
        # Build response
        return {
            "success": True,
            "product_name": product_name,
            "source": "store",
            "summary": {
                "average_rating": normalized.get("average_rating", 0),
                "trust_score": normalized.get("trust_score", 0),
                "verified_patterns": normalized.get("verified_patterns", {"positive": [], "negative": []}),
            },
            "reviews": [
                {
                    "store": r.get("store", "unknown"),
                    "text": r.get("text", ""),
                    "rating": r.get("rating"),
                    "confidence": r.get("validation_confidence", 1.0),
                }
                for r in validated_reviews[:25]
            ],
            "total_found": len(validated_reviews),
            "raw_count": len(raw_reviews),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching store reviews: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch store reviews: {str(e)}"
        )


# Google Shopping Reviews API - Stateless
@router.post("/reviews/google")
async def get_google_reviews_stateless(
    body: Dict[str, Any] = Body(...)
):
    """
    Fetch and normalize Google Shopping reviews.
    
    No database dependency - stateless operation.
    Uses Playwright to scrape and Gemini AI for normalization.
    
    Architecture:
    1. Navigate to Google Shopping product page
    2. Click "More reviews" button until it disappears (max 50 clicks)
    3. Expand all reviews to show full text
    4. Extract review fields (name, rating, date, title, text, source)
    5. Deduplicate exact and near-duplicate reviews (>95% similarity)
    6. Validate reviews with AI (remove non-reviews)
    7. Normalize and extract patterns/sentiment
    
    Request body:
    {
        "product_name": string (required),
        "google_shopping_url": string (required - full Google Shopping URL)
    }
    """
    from app.services.google_review_service import GoogleReviewService
    from app.services.ai_review_service import AIReviewService
    
    try:
        # Extract request parameters
        product_name = body.get("product_name")
        google_shopping_url = body.get("google_shopping_url")
        
        if not product_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="product_name is required"
            )
        
        if not google_shopping_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="google_shopping_url is required"
            )
        
        logger.info(f"Fetching Google Shopping reviews for: {product_name}")
        logger.debug(f"Google Shopping URL: {google_shopping_url}")
        
        # Step 1: Scrape Google Shopping page
        logger.debug("Step 1: Starting Google Shopping scraper...")
        google_service = GoogleReviewService()
        scrape_result = google_service.fetch_google_reviews(
            google_shopping_url=google_shopping_url,
            product_name=product_name
        )
        
        if not scrape_result.get("success"):
            error_msg = scrape_result.get('error', 'Unknown error')
            logger.error(f"Google Shopping scraper failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to scrape Google Shopping: {error_msg}"
            )
        
        # Extract reviews from scrape result
        raw_reviews = scrape_result.get("reviews", [])
        logger.info(f"Raw reviews scraped: {len(raw_reviews)}")
        logger.debug(f"Scrape result keys: {scrape_result.keys()}")
        logger.debug(f"Scrape success: {scrape_result.get('success')}")
        logger.debug(f"Source URL: {scrape_result.get('source_url', 'N/A')}")
        
        # Log first few reviews as samples
        if raw_reviews:
            logger.debug(f"Sample of first {min(3, len(raw_reviews))} reviews:")
            for idx, review in enumerate(raw_reviews[:3]):
                logger.debug(f"  Review {idx + 1}: {review}")
        
        # Limit to first 100 reviews to speed up processing
        if len(raw_reviews) > 100:
            logger.info(f"Limiting to first 100 reviews for faster processing (found {len(raw_reviews)})")
            raw_reviews = raw_reviews[:100]
        
        # Step 2: For Google Shopping reviews, skip AI validation (they're already vetted)
        # Just use the reviews as-is with basic validation
        logger.debug(f"Step 2: Applying basic validation to {len(raw_reviews)} reviews...")
        validated_reviews = [r for r in raw_reviews if r.get("text") and len(r.get("text", "")) > 10]
        filtered_count = len(raw_reviews) - len(validated_reviews)
        logger.info(f"Basic validation: {len(validated_reviews)} reviews (filtered {filtered_count})")
        
        if filtered_count > 0:
            logger.debug(f"Filtered out {filtered_count} reviews due to invalid text")
        
        # Step 3: Build summary from reviews directly
        logger.debug("Step 3: Building response summary...")
        logger.info("Building response...")
        try:
            # Calculate basic stats
            ratings = [r.get("rating", 0) for r in validated_reviews if r.get("rating")]
            average_rating = sum(ratings) / len(ratings) if ratings else 0
            
            # Simple sentiment based on average rating
            if average_rating >= 4.5:
                overall_sentiment = "very_positive"
            elif average_rating >= 4.0:
                overall_sentiment = "positive"
            elif average_rating >= 3.0:
                overall_sentiment = "neutral"
            elif average_rating >= 2.0:
                overall_sentiment = "negative"
            else:
                overall_sentiment = "very_negative"
            
            normalized = {
                "average_rating": round(average_rating, 1),
                "overall_sentiment": overall_sentiment,
                "common_praises": [],
                "common_complaints": [],
                "verified_patterns": {"positive": [], "negative": []},
            }
        except Exception as e:
            logger.warning(f"Could not calculate summary: {e}")
            normalized = {
                "average_rating": 0,
                "overall_sentiment": "neutral",
                "common_praises": [],
                "common_complaints": [],
                "verified_patterns": {"positive": [], "negative": []},
            }
        
        # Build response
        return {
            "success": True,
            "product_name": product_name,
            "source": "google_shopping",
            "summary": {
                "average_rating": normalized.get("average_rating", 0),
                "overall_sentiment": normalized.get("overall_sentiment", "neutral"),
                "common_praises": normalized.get("common_praises", []),
                "common_complaints": normalized.get("common_complaints", []),
                "verified_patterns": normalized.get("verified_patterns", {"positive": [], "negative": []}),
            },
            "reviews": [
                {
                    "reviewer_name": r.get("reviewer_name", "Anonymous"),
                    "rating": r.get("rating", 0),
                    "date": r.get("date", ""),
                    "title": r.get("title", ""),
                    "text": r.get("text", ""),
                    "source": r.get("source", "Google"),
                    "confidence": r.get("validation_confidence", 1.0),
                }
                for r in validated_reviews[:50]
            ],
            "total_found": len(validated_reviews),
            "raw_count": len(raw_reviews),
            "filtered_count": len(raw_reviews) - len(validated_reviews),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Google reviews: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch Google reviews: {str(e)}"
        )