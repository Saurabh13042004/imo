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
from app.tasks.review_tasks import (
    fetch_community_reviews_task,
    fetch_store_reviews_task,
    fetch_google_reviews_task
)

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
    Fetch and normalize community reviews from Reddit and forums (ASYNC - Celery Task).
    
    No database dependency - stateless operation.
    Uses SerpAPI for search and Gemini AI for normalization.
    
    Returns immediately with task_id for polling results.
    
    Architecture:
    1. Dispatch async task to Celery worker
    2. Return task_id to client
    3. Client polls /reviews/community/status/{task_id} for results
    
    Request body:
    {
        "product_name": string (required),
        "brand": string (optional)
    }
    
    Response:
    {
        "success": true,
        "task_id": "string - UUID of the async task",
        "status": "PENDING|STARTED|SUCCESS|FAILURE",
        "message": "Task has been queued for processing"
    }
    """
    try:
        # Extract request parameters
        product_name = body.get("product_name")
        brand = body.get("brand", "")
        
        if not product_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="product_name is required"
            )
        
        logger.info(f"Queuing community reviews task for: {product_name}")
        
        # Dispatch async task
        task = fetch_community_reviews_task.delay(
            product_name=product_name,
            brand=brand
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "status": "PENDING",
            "message": "Task has been queued for processing. Use task_id to poll results.",
            "polling_endpoint": f"/api/v1/reviews/community/status/{task.id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error queuing community reviews task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue community reviews task: {str(e)}"
        )


# Store Reviews API - Stateless
@router.post("/reviews/store")
async def get_store_reviews_stateless(
    body: Dict[str, Any] = Body(...)
):
    """
    Fetch and normalize store reviews from retailer websites (ASYNC - Celery Task).
    
    No database dependency - stateless operation.
    Generically scrapes reviews and uses Gemini AI for normalization.
    
    Returns immediately with task_id for polling results.
    
    Architecture:
    1. Dispatch async task to Celery worker
    2. Return task_id to client
    3. Client polls /reviews/store/status/{task_id} for results
    
    Request body:
    {
        "product_name": string,
        "store_urls": string[] (required - at least 1 URL)
    }
    
    Response:
    {
        "success": true,
        "task_id": "string - UUID of the async task",
        "status": "PENDING|STARTED|SUCCESS|FAILURE",
        "message": "Task has been queued for processing"
    }
    """
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
        
        logger.info(f"Queuing store reviews task for: {product_name} from {len(store_urls)} URLs")
        
        # Dispatch async task
        task = fetch_store_reviews_task.delay(
            product_name=product_name,
            store_urls=store_urls
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "status": "PENDING",
            "message": "Task has been queued for processing. Use task_id to poll results.",
            "polling_endpoint": f"/api/v1/reviews/store/status/{task.id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error queuing store reviews task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue store reviews task: {str(e)}"
        )


# Google Shopping Reviews API - Stateless
@router.post("/reviews/google")
async def get_google_reviews_stateless(
    body: Dict[str, Any] = Body(...)
):
    """
    Fetch and normalize Google Shopping reviews (ASYNC - Celery Task).
    
    No database dependency - stateless operation.
    Uses Playwright to scrape and Gemini AI for normalization.
    
    Returns immediately with task_id for polling results.
    
    Architecture:
    1. Dispatch async task to Celery worker
    2. Return task_id to client
    3. Client polls /reviews/google/status/{task_id} for results
    
    Request body:
    {
        "product_name": string (required),
        "google_shopping_url": string (required - full Google Shopping URL)
    }
    
    Response:
    {
        "success": true,
        "task_id": "string - UUID of the async task",
        "status": "PENDING|STARTED|SUCCESS|FAILURE",
        "message": "Task has been queued for processing"
    }
    """
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
        
        logger.info(f"Queuing Google Shopping reviews task for: {product_name}")
        logger.debug(f"Google Shopping URL: {google_shopping_url}")
        
        # Dispatch async task
        task = fetch_google_reviews_task.delay(
            product_name=product_name,
            google_shopping_url=google_shopping_url
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "status": "PENDING",
            "message": "Task has been queued for processing. Use task_id to poll results.",
            "polling_endpoint": f"/api/v1/reviews/google/status/{task.id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error queuing Google reviews task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue Google reviews task: {str(e)}"
        )


# Task Status Endpoints
@router.get("/reviews/status/{task_id}")
async def get_review_task_status(task_id: str):
    """
    Check the status of a review task and retrieve results if available.
    
    Path parameters:
        task_id: The UUID of the task returned from the review endpoints
    
    Response statuses:
        PENDING: Task is waiting to be processed
        STARTED: Task is currently processing
        PROGRESS: Task is streaming partial results (meta contains intermediate data)
        SUCCESS: Task completed, results are available
        FAILURE: Task failed, check 'error' field
        RETRY: Task is being retried
    """
    from app.celery_app import celery_app
    
    try:
        task_result = celery_app.AsyncResult(task_id)
        
        # Build response based on task state
        response = {
            "task_id": task_id,
            "status": task_result.state,
            "ready": task_result.ready(),
            "successful": task_result.successful() if task_result.ready() else None,
        }
        
        # Include result if available
        if task_result.state == "SUCCESS":
            response["result"] = task_result.result
            response["message"] = "Task completed successfully"
        elif task_result.state == "PROGRESS":
            # Include intermediate/partial results
            response["state_meta"] = task_result.info if isinstance(task_result.info, dict) else {}
            response["message"] = "Task is streaming results progressively"
        elif task_result.state == "FAILURE":
            response["error"] = str(task_result.info)
            response["message"] = "Task failed"
        elif task_result.state in ["PENDING", "STARTED"]:
            response["message"] = f"Task is {task_result.state.lower()}"
        elif task_result.state == "RETRY":
            response["message"] = "Task is being retried"
            response["retries"] = task_result.info.get("retries", 0) if isinstance(task_result.info, dict) else 0
        
        return response
        
    except Exception as e:
        logger.error(f"Error checking task status {task_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check task status: {str(e)}"
        )


@router.get("/reviews/community/status/{task_id}")
async def get_community_review_task_status(task_id: str):
    """Check status of community reviews task."""
    return await get_review_task_status(task_id)


@router.get("/reviews/store/status/{task_id}")
async def get_store_review_task_status(task_id: str):
    """Check status of store reviews task."""
    return await get_review_task_status(task_id)


@router.get("/reviews/google/status/{task_id}")
async def get_google_review_task_status(task_id: str):
    """Check status of Google Shopping reviews task."""
    return await get_review_task_status(task_id)