"""Search routes."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import SearchRequest, SearchResponse, ErrorResponse
from app.services import SearchService
from app.api.dependencies import get_db
from app.utils.validators import validate_search_query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["search"])

search_service = SearchService()


@router.post(
    "/search",
    response_model=SearchResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def search_products(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Search for products across multiple sources.

    - **query**: Search query (required, 2-200 characters)
    - **sources**: List of sources to search (amazon, walmart, google_shopping)
    - **limit**: Maximum number of results (default: 20, max: 100)
    - **min_rating**: Minimum product rating (0-5)
    - **max_price**: Maximum product price
    """
    try:
        # Validate query
        if not validate_search_query(request.query):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid search query. Must be 2-200 characters."
            )

        # Validate sources
        valid_sources = {"amazon", "walmart", "google_shopping"}
        for source in request.sources:
            if source.lower() not in valid_sources:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid source: {source}. Must be one of: {', '.join(valid_sources)}"
                )

        logger.info(f"Search request: query={request.query}, sources={request.sources}")

        # Perform search
        results = await search_service.search_all_sources(db, request)

        return SearchResponse(
            success=True,
            query=request.query,
            total_results=len(results),
            results=results
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed. Please try again."
        )
