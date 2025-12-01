"""Product routes."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.schemas import (
    ProductResponse,
    ProductDetailResponse,
    ErrorResponse
)
from app.services import SearchService, ReviewService, VideoService, AIService
from app.api.dependencies import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["products"])

search_service = SearchService()
review_service = ReviewService()
video_service = VideoService()
ai_service = AIService()


@router.get(
    "/product/{product_id}",
    response_model=ProductDetailResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_product_details(
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed product information including reviews and videos.

    - **product_id**: UUID of the product
    """
    try:
        # Get product
        product = await search_service.get_product_by_id(db, str(product_id))

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        logger.info(f"Fetched product details: {product_id}")

        return ProductDetailResponse(
            **{**ProductResponse.from_orm(product).dict(), "reviews": product.reviews, "videos": product.videos}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product details: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch product details"
        )


@router.post(
    "/product/details",
    response_model=ProductDetailResponse,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_product_details_by_source(
    product_id: Optional[UUID] = None,
    source: Optional[str] = None,
    source_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get product details by ID or by source + source_id.

    Provide either:
    - **product_id**: UUID of the product, OR
    - **source** and **source_id**: Marketplace source and product ID
    """
    try:
        product = None

        if product_id:
            product = await search_service.get_product_by_id(db, str(product_id))
        elif source and source_id:
            product = await search_service.get_product_by_source(db, source, source_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide either product_id or both source and source_id"
            )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        logger.info(f"Fetched product by source: {source}/{source_id if source_id else product_id}")

        return ProductDetailResponse(
            **{**ProductResponse.from_orm(product).dict(), "reviews": product.reviews, "videos": product.videos}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch product"
        )
