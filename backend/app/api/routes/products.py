"""Product routes."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import json
import httpx

from app.schemas import (
    ProductResponse,
    ProductDetailResponse,
    ErrorResponse,
    EnrichedProductRequest,
    AmazonProductAnalysis,
    AmazonReview,
    AIVerdictRequest,
    ShortVideoReviewsResponse,
    UserVideoReviewCreate,
    UserVideoReviewResponse,
    UploadSuccessResponse
)
from app.services import SearchService, ReviewService, VideoService, AIService, ProductService
from app.services.short_video_service import short_video_service
from app.services.s3_service import S3Service
from app.api.dependencies import get_db, get_current_user
from app.config import Settings
from app.models import UserReview, Product

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["products"])

search_service = SearchService()
review_service = ReviewService()
video_service = VideoService()
ai_service = AIService()
product_service = ProductService()
s3_service = S3Service()


@router.get(
    "/product/{product_id}",
    response_model=ProductResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_product_details(
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed product information by product ID.
    First tries cache, then fetches fresh data if needed.

    - **product_id**: UUID of the product
    """
    try:
        logger.info(f"Fetching product with ID: {product_id}")
        # Get product from cache
        product = await search_service.get_product_by_id(db, str(product_id))

        if product:
            logger.info(f"Found product in cache: {product_id}")
            return product

        logger.warning(f"Product {product_id} not found in cache")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found. Please search for it first."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product details: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch product details: {str(e)}"
        )


@router.get(
    "/product/{product_id}",
    response_model=ProductResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_product_by_id(
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get product details by product UUID from search cache.
    
    Products are cached after search results are returned.
    Use the product.id from search results to retrieve details.
    
    - **product_id**: Product UUID from search results
    """
    try:
        logger.info(f"Fetching product details for ID: {product_id}")
        
        product = await product_service.get_product_by_id(db, product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product not found in cache. Product ID: {product_id}"
            )
        
        logger.info(f"Successfully fetched product: {product.title[:50]}")
        return product

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product by ID: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch product details: {str(e)}"
        )


@router.get(
    "/product/amazon/{asin}",
    response_model=ProductResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_amazon_product_details(
    asin: str,
    title: Optional[str] = Query(None),
    image: Optional[str] = Query(None),
    zipcode: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed product information by ASIN.
    
    NOTE: Products are retrieved from Google Shopping search cache.
    The search must be performed first to populate the cache.
    
    This endpoint is for backward compatibility. New clients should:
    1. Call /search to populate cache
    2. Use product.id from search results to fetch details
    
    - **asin**: Amazon Standard Identification Number (for cache lookup)
    - **title**: Optional product title from search results  
    - **image**: Optional product image from search results
    - **zipcode**: Optional zipcode parameter (for future enrichment)
    """
    try:
        logger.info(f"[DEPRECATED] Fetching product details by ASIN: {asin}")
        
        # Try to get from cache by ASIN
        product = await product_service.get_amazon_product_details(
            db,
            asin,
            product_title=title,
            product_image=image,
            zipcode=zipcode
        )
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ASIN {asin} not found in cache. Please perform a search first."
            )
        
        logger.info(f"Successfully fetched product: {product.title[:50]}")
        return product

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch product details: {str(e)}"
        )


@router.get(
    "/product/intelligent/{asin}",
    response_model=AmazonProductAnalysis,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_intelligent_product_analysis(
    asin: str,
    title: Optional[str] = Query(None),
    image: Optional[str] = Query(None),
    zipcode: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get intelligent product analysis combining three layers:
    
    LAYER 1 - DATA (Amazon = Canonical Truth):
      - Title, images, variants, specs, pricing, rating, reviews
      - Source: Amazon API via Oxylabs RapidAPI
    
    LAYER 2 - ENRICHMENT (SerpAPI Optional, Non-blocking):
      - External reviews from blogs, forums, Reddit
      - Cross-store pricing comparisons
      - Doesn't override Amazon data, only supplements
    
    LAYER 3 - INTELLIGENCE (Gemini Analysis):
      - Synthesizes pros/cons from all sources
      - Generates verdict_score (1-10)
      - Identifies deal-breakers and target customers
      - Never modifies raw data, only analyzes
    
    Returns single unified JSON with all three layers integrated.
    Frontend reads from predictable paths: .amazon_reviews, .external_reviews, .analysis

    - **asin**: Amazon Standard Identification Number
    - **title**: Optional product title from search results
    - **image**: Optional product image from search results
    - **zipcode**: Optional zipcode for location-based pricing (defaults to config DEFAULT_ZIPCODE)
    """
    try:
        import asyncio
        import time
        
        start_time = time.time()
        logger.info(f"[Intelligent] Fetching product analysis for ASIN: {asin}")
        
        # ====== LAYER 1: DATA ======
        # Fetch complete Amazon product data (canonical source)
        layer1_start = time.time()
        amazon_product = await product_service.get_amazon_product_details(
            db,
            asin,
            product_title=title,
            product_image=image
        )
        layer1_time = time.time() - layer1_start
        logger.info(f"[Intelligent] Layer 1 (Amazon fetch) completed in {layer1_time:.2f}s")
        
        # ====== LAYER 1: DATA ======
        # Fetch complete Amazon product data (canonical source)
        amazon_product = await product_service.get_amazon_product_details(
            db,
            asin,
            product_title=title,
            product_image=image,
            zipcode=zipcode
        )
        
        if not amazon_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product not found on Amazon for ASIN: {asin}"
            )
        
        logger.info(f"[Intelligent] Fetched Amazon product: {amazon_product.title[:50]}")
        
        # Get raw Amazon content for detailed extraction
        raw_amazon_data = product_service._fetch_amazon_product_details(asin)
        amazon_content = {}
        if raw_amazon_data and "results" in raw_amazon_data and raw_amazon_data["results"]:
            amazon_content = raw_amazon_data["results"][0].get("content", {})
        
        # Extract reviews from Amazon (canonical source)
        amazon_reviews = []
        if "reviews" in amazon_content:
            for review in amazon_content.get("reviews", []):
                try:
                    amazon_reviews.append(AmazonReview(
                        id=review.get("id", ""),
                        author=review.get("author", "Anonymous"),
                        rating=int(review.get("rating", 0)),
                        title=review.get("title", ""),
                        content=review.get("content", ""),
                        timestamp=review.get("timestamp", ""),
                        is_verified=review.get("is_verified", False),
                        helpful_count=int(review.get("helpful_count", 0))
                    ))
                except Exception as e:
                    logger.warning(f"Failed to parse Amazon review: {e}")
        
        logger.info(f"[Intelligent] Extracted {len(amazon_reviews)} reviews from Amazon")
        
        # ====== LAYER 2 & 3: ENRICHMENT + INTELLIGENCE (PARALLEL) ======
        # Run SerpAPI enrichment, Reddit/Forum reviews, and Gemini analysis in parallel
        # All are non-blocking and can run concurrently
        
        parallel_start = time.time()
        
        async def fetch_serp_enrichment():
            """Fetch SerpAPI enrichment data"""
            try:
                data = await product_service._fetch_serpapi_enrichment(
                    title or amazon_product.title,
                    asin=asin,
                    location=zipcode
                )
                logger.info("[Intelligent] Successfully fetched SerpAPI enrichment")
                return data
            except Exception as e:
                logger.warning(f"[Intelligent] SerpAPI enrichment failed (non-blocking): {e}")
                return None
        
        async def fetch_external_reviews():
            """Fetch external reviews from Reddit and Forums"""
            try:
                # Fetch Reddit and Forum reviews
                external_source_reviews = await review_service.fetch_reviews(
                    product_title=amazon_product.title,
                    sources=["reddit", "forums"],
                    db=db
                )
                logger.info(f"[Intelligent] Fetched {len(external_source_reviews)} reviews from Reddit/Forums")
                return external_source_reviews
            except Exception as e:
                logger.warning(f"[Intelligent] External source reviews failed (non-blocking): {e}")
                return []
        
        async def fetch_ai_analysis():
            """Generate AI analysis using Gemini"""
            try:
                analysis = await ai_service.analyze_amazon_product(
                    amazon_data=amazon_content,
                    serp_data=None,  # Will be updated after SerpAPI completes
                    product_title=amazon_product.title
                )
                logger.info(f"[Intelligent] Generated AI analysis for {amazon_product.title[:50]}")
                return analysis
            except Exception as e:
                logger.warning(f"[Intelligent] AI analysis failed (non-blocking): {e}")
                return None
        
        # RUN ALL IN PARALLEL (key optimization)
        logger.info("[Intelligent] Starting parallel SerpAPI + Reddit/Forums + Gemini fetch")
        serp_data, external_source_reviews, ai_analysis = await asyncio.gather(
            fetch_serp_enrichment(),
            fetch_external_reviews(),
            fetch_ai_analysis(),
            return_exceptions=True
        )
        
        parallel_time = time.time() - parallel_start
        logger.info(f"[Intelligent] Layer 2+3 (Parallel SerpAPI + Reddit/Forums + Gemini) completed in {parallel_time:.2f}s")
        
        # Handle any exceptions from gather
        if isinstance(serp_data, Exception):
            logger.warning(f"[Intelligent] SerpAPI exception: {serp_data}")
            serp_data = None
        if isinstance(external_source_reviews, Exception):
            logger.warning(f"[Intelligent] External source reviews exception: {external_source_reviews}")
            external_source_reviews = []
        if isinstance(ai_analysis, Exception):
            logger.warning(f"[Intelligent] AI analysis exception: {ai_analysis}")
            ai_analysis = None
        
        # ====== EXTRACT ENRICHMENT DATA ======
        # Parse SerpAPI response for reviews and store info
        external_reviews = []
        external_stores = []
        external_rating = None
        external_ratings_distribution = []
        
        # Add Reddit and Forum reviews first
        for review_data in external_source_reviews:
            try:
                from app.schemas import ExternalReview
                external_reviews.append(ExternalReview(
                    source=review_data.get("source", "Unknown"),
                    author=review_data.get("author", "Anonymous"),
                    rating=review_data.get("rating"),
                    title=review_data.get("title", ""),
                    content=review_data.get("content", "")
                ))
            except Exception as e:
                logger.warning(f"Failed to parse Reddit/Forum review: {e}")
        
        logger.info(f"[Intelligent] Included {len(external_reviews)} reviews from Reddit/Forums")
        
        if serp_data:
            try:
                if serp_data and "product_results" in serp_data:
                    product_results = serp_data.get("product_results", {})
                    
                    # Extract user reviews from the immersive product response
                    # These are reviews from various sources (eBay, Amazon, Sony.com, etc.)
                    user_reviews = product_results.get("user_reviews", [])
                    for review in user_reviews:
                        try:
                            from app.schemas import ExternalReview
                            external_reviews.append(ExternalReview(
                                source=review.get("source", "SerpAPI"),
                                author=review.get("user_name", "Anonymous"),
                                rating=float(review.get("rating", 0)) if review.get("rating") else None,
                                title=review.get("title", ""),
                                content=review.get("text", review.get("snippet", ""))
                            ))
                        except Exception as e:
                            logger.warning(f"Failed to parse SerpAPI review: {e}")
                    
                    # Extract cross-store pricing (enrichment)
                    stores = product_results.get("stores", [])
                    external_stores = stores  # Store the full store data as-is
                    logger.info(f"[Intelligent] Extracted {len(stores)} cross-store offers from SerpAPI")
                    
                    # Extract external rating and ratings distribution
                    external_rating = product_results.get("rating")
                    external_ratings_distribution = product_results.get("ratings", [])
                    
                    logger.info(f"[Intelligent] Extracted {len(user_reviews)} SerpAPI reviews")
            except Exception as e:
                logger.warning(f"[Intelligent] Failed to extract SerpAPI enrichment data: {e}")
        
        # ====== BUILD UNIFIED RESPONSE ======
        # Single schema with all three layers integrated
        response = AmazonProductAnalysis(
            # Layer 1: Base data from Amazon
            asin=asin,
            parent_asin=amazon_content.get("parent_asin"),
            title=amazon_product.title,
            brand=amazon_content.get("brand"),
            manufacturer=amazon_content.get("manufacturer"),
            images=amazon_content.get("images", []),
            bullet_points=amazon_content.get("bullet_points", ""),
            description=amazon_content.get("description", ""),
            category=amazon_content.get("category", ""),
            price=float(amazon_content.get("price", 0)),
            price_strikethrough=float(amazon_content.get("price_strikethrough", 0)) if amazon_content.get("price_strikethrough") else None,
            discount_percentage=int(amazon_content.get("discount_percentage", 0)) if amazon_content.get("discount_percentage") else None,
            currency=amazon_content.get("currency", "USD"),
            buybox=amazon_content.get("buybox", []),
            variants=amazon_content.get("variation", []),
            rating=float(amazon_content.get("rating", 0)),
            rating_distribution=amazon_content.get("rating_distribution", []),
            total_reviews=int(amazon_content.get("total_reviews", 0)),
            sales_rank=amazon_content.get("sales_rank"),
            sales_volume=amazon_content.get("sales_volume"),
            
            # Layer 2: Reviews separated by source
            amazon_reviews=amazon_reviews,
            external_reviews=external_reviews,
            
            # Layer 2.5: Enrichment data from SerpAPI
            external_stores=external_stores,
            external_rating=external_rating,
            external_ratings_distribution=external_ratings_distribution,
            
            # Layer 3: Intelligence from Gemini
            analysis=ai_analysis
        )
        
        total_time = time.time() - start_time
        logger.info(f"[Intelligent] Built unified response for {asin} (reviews: {len(amazon_reviews)} Amazon + {len(external_reviews)} external)")
        logger.info(f"[Intelligent] ⚡ TOTAL TIME: {total_time:.2f}s (Layer1: {layer1_time:.2f}s + Parallel: {parallel_time:.2f}s)")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Intelligent] Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate product analysis: {str(e)}"
        )


@router.post(
    "/product/details",
    response_model=ProductResponse,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_product_details_by_source(
    source: str,
    source_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get product details by source and source_id.

    - **source**: Product source (e.g., "amazon", "walmart")
    - **source_id**: Source-specific product ID
    """
    try:
        product = await search_service.get_product_by_source(db, source, source_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        logger.info(f"Fetched product by source: {source}/{source_id}")
        return product

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch product"
        )


@router.get(
    "/product/immersive/{product_id}",
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_immersive_product_details(
    product_id: str,
):
    """
    Get detailed product information using SerpAPI Immersive Product API.
    This endpoint is used for non-Amazon products to get rich details.

    - **product_id**: UUID of the product from our database
    """
    try:
        logger.info(f"Fetching immersive product details for product: {product_id}")
        
        # For now, we'll return a placeholder
        # The frontend will pass the immersive_product_api_link from the search results
        return {
            "status": "immersive_details",
            "message": "Use the immersive_product_api_link from search results for detailed data"
        }

    except Exception as e:
        logger.error(f"Error fetching immersive product details: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch immersive product details: {str(e)}"
        )


@router.post(
    "/product/enriched/{product_id}",
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_enriched_product_details(
    product_id: str,
    request: EnrichedProductRequest,
):
    """
    Get enriched product details for non-Amazon products.
    Uses the immersive_api_link from search results to fetch detailed data.

    - **product_id**: UUID of the product from our database
    - **request**: Request body containing immersive_api_link from SerpAPI
    """
    try:
        logger.info(f"Fetching enriched details for product: {product_id}")
        
        immersive_api_link = request.immersive_api_link
        
        if not immersive_api_link:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="immersive_api_link is required"
            )

        # Fetch from SerpAPI using the provided link
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Add API key to the immersive_api_link if it's a SerpAPI endpoint
            from app.config import settings
            
            api_link = immersive_api_link
            
            # Check if API key is already in the URL
            if "api_key=" not in api_link and settings.SERPAPI_KEY:
                # Add API key to the URL
                separator = "&" if "?" in api_link else "?"
                api_link = f"{api_link}{separator}api_key={settings.SERPAPI_KEY}"
            
            logger.info(f"Calling SerpAPI immersive product endpoint: {api_link[:100]}...")
            
            response = await client.get(api_link)
            response.raise_for_status()
            immersive_data = response.json()
            
            logger.info(f"Successfully fetched immersive data for product: {product_id}")
            return {
                "product_id": product_id,
                "immersive_data": immersive_data
            }

    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching immersive product details: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch data from external API"
        )
    except Exception as e:
        logger.error(f"Error fetching enriched product details: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch enriched product details: {str(e)}"
        )


@router.post(
    "/product/{product_id}/ai-verdict",
    response_model=dict,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def generate_ai_verdict(
    product_id: str,
    request: AIVerdictRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI verdict for a product using enriched data from frontend.
    
    CRITICAL: This endpoint DOES NOT refetch product data.
    It uses ONLY the enriched_data provided in the request body.
    
    Endpoint is product-agnostic (works for Amazon, Google Shopping, Walmart, etc.)
    
    Args:
        product_id: Product UUID from database
        request: AIVerdictRequest with:
            - enriched_data: Full response from /product/enriched endpoint
            - scrape_stores: Whether to scrape store pages for insights
    
    Returns:
        { status: "ready"|"processing"|"error", verdict?: {...}, message?: "..." }
    """
    try:
        logger.info(f"[AI Verdict] Processing verdict for product: {product_id}")
        
        enriched_data = request.enriched_data
        scrape_stores = request.scrape_stores
        
        if not enriched_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="enriched_data is required in request body"
            )
        
        # Check cache first
        ai_verdict_cache = getattr(generate_ai_verdict, '_cache', {})
        if not hasattr(generate_ai_verdict, '_cache'):
            generate_ai_verdict._cache = ai_verdict_cache
        
        if product_id in ai_verdict_cache:
            logger.info(f"[AI Verdict] Cache hit for product: {product_id}")
            return {
                "status": "ready",
                "verdict": ai_verdict_cache[product_id]
            }
        
        logger.info(f"[AI Verdict] Starting verdict generation for product: {product_id}")
        
        # Optionally scrape store pages for additional insights
        store_insights = []
        if scrape_stores:
            logger.info(f"[AI Verdict] Scraping stores for product: {product_id}")
            stores = enriched_data.get("immersive_data", {}).get("product_results", {}).get("stores", [])
            store_insights = await ai_service.scrape_store_insights(stores)
            logger.info(f"[AI Verdict] Scraped {len(store_insights)} store insights")
        
        # Generate verdict using ONLY the enriched data provided
        verdict = await ai_service.generate_product_verdict(
            product_id=product_id,
            enriched_data=enriched_data,
            store_insights=store_insights
        )
        
        if verdict:
            # Cache the verdict
            ai_verdict_cache[product_id] = verdict
            logger.info(f"[AI Verdict] Successfully generated verdict for product: {product_id}")
            return {
                "status": "ready",
                "verdict": verdict
            }
        else:
            logger.warning(f"[AI Verdict] Failed to generate verdict for product: {product_id}")
            return {
                "status": "error",
                "message": "Failed to generate AI verdict"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[AI Verdict] Error generating verdict for {product_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI verdict: {str(e)}"
        )


@router.get(
    "/product/{product_id}/short-video-reviews",
    response_model=ShortVideoReviewsResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_short_video_reviews(
    product_id: UUID,
    title: str = Query(..., description="Product title for video search"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get short-form video reviews for a product.
    
    Fetches YouTube Shorts, TikTok videos, and Instagram Reels related to the product.
    Results are cached for 24 hours.
    
    Non-blocking: returns immediately, videos load in background if not cached.
    
    - **product_id**: UUID of the product
    - **title**: Product title (required for video search)
    """
    try:
        if not title or not title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product title is required"
            )
        
        # Fetch short video reviews (cached) - title parameter enables search without DB lookup
        videos = await short_video_service.fetch_short_video_reviews(
            product_id,
            title.strip()
        )
        
        # Transform to response schema
        video_responses = [
            {
                "id": video.get("id"),
                "platform": video.get("platform"),
                "video_url": video.get("video_url"),
                "thumbnail_url": video.get("thumbnail_url"),
                "creator": video.get("creator"),
                "caption": video.get("caption"),
                "likes": video.get("likes", 0),
                "views": video.get("views", 0),
                "duration": video.get("duration")
            }
            for video in videos
        ]
        
        logger.info(f"[ShortVideoReviews] Returned {len(video_responses)} videos for {product_id}")
        
        return ShortVideoReviewsResponse(
            success=True,
            product_id=product_id,
            total=len(video_responses),
            videos=video_responses
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ShortVideoReviews] Error fetching videos for {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch short video reviews: {str(e)}"
        )


@router.get("/debug/cache")
async def debug_cache():
    """Debug endpoint to check cache contents."""
    from app.services.search_service import PRODUCT_CACHE, PRODUCT_BY_SOURCE
    return {
        "cache_size": len(PRODUCT_CACHE),
        "cache_keys": list(PRODUCT_CACHE.keys()),
        "source_cache_size": len(PRODUCT_BY_SOURCE),
        "source_cache_keys": list(PRODUCT_BY_SOURCE.keys())
    }


@router.post(
    "/reviews/upload-video",
    response_model=UploadSuccessResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def upload_video_review(
    product_id: str = Form(...),  # Accept product ID string (could be UUID or source_id)
    product_title: str = Form(...),  # Product title required for product creation
    product_source: str = Form(default="google_shopping"),  # Product source (default: google_shopping)
    title: str = Form(...),
    description: str = Form(...),
    rating: int = Form(...),
    video_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Upload a video review for a product.
    
    - **product_id**: Google Shopping product ID or source-specific ID
    - **product_title**: Product title (used for creating product record if needed)
    - **product_source**: Product source like "google_shopping", "amazon", "walmart" (default: google_shopping)
    - **title**: Review title
    - **description**: Review description
    - **rating**: Rating 1-5
    - **video_file**: MP4 or MOV file (max 50MB)
    
    Returns: Approval pending message with guidelines link
    """
    try:
        # Validate inputs
        if not title or len(title) < 1 or len(title) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title must be between 1 and 200 characters"
            )
        
        if not description or len(description) < 10 or len(description) > 2000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Description must be between 10 and 2000 characters"
            )
        
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
        
        # Validate file
        if not video_file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Video file is required"
            )
        
        # Check file extension
        allowed_extensions = {'mp4', 'mov'}
        file_ext = video_file.filename.split('.')[-1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only MP4 and MOV files are allowed. Got: {file_ext}"
            )
        
        # Check file size (50MB max)
        max_size = 50 * 1024 * 1024  # 50MB
        file_content = await video_file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds 50MB limit. Size: {len(file_content) / 1024 / 1024:.2f}MB"
            )
        
        # Find or create product by source and source_id
        # Try to find existing product first
        stmt = select(Product).where(
            (Product.source == product_source) & 
            (Product.source_id == product_id)
        )
        result = await db.execute(stmt)
        product = result.scalars().first()
        
        # If product doesn't exist, create it
        if not product:
            logger.info(f"Creating new product: source={product_source}, source_id={product_id}")
            product = Product(
                title=product_title,
                source=product_source,
                source_id=product_id,
                description=None  # Can be populated later
            )
            db.add(product)
            await db.commit()
            await db.refresh(product)
            logger.info(f"Created product {product.id} for {product_source}:{product_id}")
        
        # Upload to S3
        s3_key = s3_service.upload_video(
            file_content=file_content,
            file_name=video_file.filename,
            user_id=str(current_user.id),
            product_id=str(product.id)
        )
        
        if not s3_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload video to S3"
            )
        
        # Create review record in database
        user_review = UserReview(
            user_id=current_user.id,
            product_id=product.id,
            title=title,
            description=description,
            rating=rating,
            status='pending',  # Set to pending for moderation
            s3_key=s3_key,
            video_url=None  # Will be generated when approved
        )
        
        db.add(user_review)
        await db.commit()
        await db.refresh(user_review)
        
        logger.info(
            f"User {current_user.id} uploaded video review for product {product.id}. "
            f"Review ID: {user_review.id}, S3 Key: {s3_key}"
        )
        
        # Return success response with approval message
        return UploadSuccessResponse(
            success=True,
            message="Boom! Your review video just landed in our inbox. Our team's on it—giving it a quick vibe check against our guidelines. Approval usually takes up to 1 business day, and we'll ping you the second it's live. In the meantime, sneak a peek at our video upload guidelines so your next one sails through.",
            review_id=user_review.id,
            status="pending",
            guidelines_url="/review-guidelines"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading video review: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload video review: {str(e)}"
        )


@router.get(
    "/reviews/user-reviews/{product_id}",
    response_model=list[UserVideoReviewResponse],
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_user_reviews_for_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get approved user video reviews for a product.
    
    - **product_id**: UUID of the product
    
    Returns: List of approved user video reviews
    """
    try:
        from sqlalchemy import select
        
        # Fetch only approved reviews
        query = select(UserReview).where(
            (UserReview.product_id == product_id) &
            (UserReview.status == 'approved')
        ).order_by(UserReview.created_at.desc())
        
        result = await db.execute(query)
        reviews = result.scalars().all()
        
        # Generate signed URLs for approved videos
        review_responses = []
        for review in reviews:
            video_url = None
            if review.s3_key:
                video_url = s3_service.get_signed_url(review.s3_key, expiration=7200)  # 2 hours
            
            review_responses.append(
                UserVideoReviewResponse(
                    id=review.id,
                    user_id=review.user_id,
                    product_id=review.product_id,
                    title=review.title,
                    description=review.description,
                    rating=review.rating,
                    status=review.status,
                    video_url=video_url,
                    s3_key=review.s3_key,
                    created_at=review.created_at,
                    updated_at=review.updated_at
                )
            )
        
        return review_responses
        
    except Exception as e:
        logger.error(f"Error fetching user reviews for product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user reviews: {str(e)}"
        )


@router.get(
    "/reviews/my-submissions",
    response_model=list[UserVideoReviewResponse],
    responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_my_submitted_reviews(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all video reviews submitted by the current user (all statuses).
    
    Returns: List of user's video reviews with status info
    """
    try:
        from sqlalchemy import select
        
        # Fetch all reviews by current user
        query = select(UserReview).where(
            UserReview.user_id == current_user.id
        ).order_by(UserReview.created_at.desc())
        
        result = await db.execute(query)
        reviews = result.scalars().all()
        
        # Generate signed URLs for videos (only approved ones should be accessible)
        review_responses = []
        for review in reviews:
            video_url = None
            if review.s3_key and review.status == 'approved':
                video_url = s3_service.get_signed_url(review.s3_key, expiration=7200)  # 2 hours
            
            review_responses.append(
                UserVideoReviewResponse(
                    id=review.id,
                    user_id=review.user_id,
                    product_id=review.product_id,
                    title=review.title,
                    description=review.description,
                    rating=review.rating,
                    status=review.status,
                    video_url=video_url,
                    s3_key=review.s3_key,
                    created_at=review.created_at,
                    updated_at=review.updated_at
                )
            )
        
        logger.info(f"User {current_user.id} retrieved {len(review_responses)} submitted reviews")
        return review_responses
        
    except Exception as e:
        logger.error(f"Error fetching submitted reviews for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch your reviews: {str(e)}"
        )
