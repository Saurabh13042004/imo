"""Search routes."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import SearchRequest, SearchResponse, ErrorResponse
from app.services import SearchService
from app.services.search_limit_service import SearchLimitService
from app.api.dependencies import get_db, get_optional_user
from app.models.user import Profile
from app.config import settings
from app.utils.validators import validate_search_query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["search"])

search_service = SearchService()
search_limit_service = SearchLimitService()


@router.post(
    "/search",
    response_model=SearchResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def search_products(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[Profile] = Depends(get_optional_user),
    x_session_id: Optional[str] = Header(None)
):
    """
    Search for products globally with geo-targeting.

    - **keyword**: Search keyword (required, 2-200 characters)
    - **country**: Country for search results (default: "United States")
    - **city**: Optional city for narrower location targeting
    - **language**: Language code for search interface (default: "en")
    - **zipcode**: Legacy field, not used for SerpAPI geo-targeting
    
    **Search Limits:**
    - Guest users: 1 free search (10 products)
    - Registered users: 3 free searches per day (10 products each)
    - Premium/Trial users: Unlimited searches
    """
    try:
        # Validate keyword
        if not validate_search_query(request.keyword):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid search keyword. Must be 2-200 characters."
            )

        # Check search access
        user_id = str(current_user.id) if current_user else None
        has_access, remaining, message = await search_limit_service.check_search_access(
            db=db,
            user_id=user_id,
            session_id=x_session_id
        )

        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=message
            )

        logger.info(
            f"[SearchRoute] Search request:\\n"
            f"  User ID: {user_id or 'Guest'}\\n"
            f"  Session ID: {x_session_id or 'None'}\\n"
            f"  Keyword: {request.keyword}\\n"
            f"  Country: {request.country}\\n"
            f"  City: {request.city}\\n"
            f"  Remaining searches: {remaining}\\n"
            f"  Message: {message}"
        )

        # Perform search
        results, total_count = await search_service.search_all_sources(db, request)

        # Increment search count (only if search was successful)
        await search_limit_service.increment_search_count(
            db=db,
            user_id=user_id,
            session_id=x_session_id
        )

        # Determine result limit based on user type
        is_premium = current_user and remaining == -1  # -1 means unlimited (premium)
        result_limit = search_limit_service.get_result_limit(
            is_premium=is_premium,
            is_registered=current_user is not None
        )

        # Apply result limit if not premium
        if result_limit > 0 and len(results) > result_limit:
            results = results[:result_limit]
            total_count = result_limit

        # Calculate remaining after this search
        new_remaining = remaining - 1 if remaining > 0 else remaining

        return SearchResponse(
            success=True,
            keyword=request.keyword,
            zipcode=request.zipcode,
            country=request.country,
            city=request.city,
            language=request.language,
            total_results=total_count,
            results=results,
            remaining_searches=new_remaining if new_remaining >= 0 else None,
            search_limit_message=message if new_remaining >= 0 else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[SearchRoute] Search error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed. Please try again."
        )


@router.get("/search/limits")
async def get_search_limits(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[Profile] = Depends(get_optional_user),
    x_session_id: Optional[str] = Header(None)
):
    """
    Get current search limits and remaining searches for the user.
    
    Returns information about:
    - Remaining searches
    - Daily limit
    - Whether user has unlimited access
    """
    try:
        user_id = str(current_user.id) if current_user else None
        has_access, remaining, message = await search_limit_service.check_search_access(
            db=db,
            user_id=user_id,
            session_id=x_session_id
        )

        return {
            "has_access": has_access,
            "remaining_searches": remaining if remaining >= 0 else None,
            "is_unlimited": remaining == -1,
            "message": message,
            "user_type": "premium" if remaining == -1 else ("registered" if current_user else "guest"),
            "daily_limit": 3 if current_user and remaining != -1 else (1 if not current_user else None)
        }

    except Exception as e:
        logger.error(f"Error getting search limits: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get search limits"
        )
