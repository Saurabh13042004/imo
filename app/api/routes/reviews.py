"""Review and video routes."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

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
