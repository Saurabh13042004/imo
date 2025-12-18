"""Search routes."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import SearchRequest, SearchResponse, ErrorResponse
from app.services import SearchService
from app.api.dependencies import get_db
from app.config import settings
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
    Search for products globally with geo-targeting.

    - **keyword**: Search keyword (required, 2-200 characters)
    - **country**: Country for search results (default: "United States")
    - **city**: Optional city for narrower location targeting
    - **language**: Language code for search interface (default: "en")
    - **zipcode**: Legacy field, not used for SerpAPI geo-targeting
    """
    try:
        # Validate keyword
        if not validate_search_query(request.keyword):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid search keyword. Must be 2-200 characters."
            )

        logger.info(
            f"[SearchRoute] Search request:\\n"
            f"  Keyword: {request.keyword}\\n"
            f"  Country: {request.country}\\n"
            f"  City: {request.city}\\n"
            f"  Language: {request.language}\\n"
            f"  Zipcode: {request.zipcode} (legacy, not used)"
        )

        # Perform search
        results, total_count = await search_service.search_all_sources(db, request)

        return SearchResponse(
            success=True,
            keyword=request.keyword,
            zipcode=request.zipcode,
            country=request.country,
            city=request.city,
            language=request.language,
            total_results=total_count,
            results=results
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[SearchRoute] Search error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed. Please try again."
        )
