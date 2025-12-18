"""Utility routes for helper functions."""

import logging
import httpx
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/utils", tags=["utils"])


class GeolocationResponse(BaseModel):
    """Response model for geolocation endpoint."""
    zipcode: str
    city: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: str


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str


@router.get(
    "/geolocation",
    response_model=GeolocationResponse,
    responses={
        500: {"model": ErrorResponse}
    }
)
async def get_user_geolocation():
    """
    Get user's geolocation based on their IP address.
    
    Supports users worldwide. Uses ipinfo.io API to determine the user's location
    from their IP address. No user permission required.
    
    Postal Code Handling:
    - US Users: Returns standard 5-digit ZIP codes (e.g., "60607")
    - International Users: Converts postal codes to 5-char format (e.g., "50000" for India's "500001")
    
    Returns:
        - zipcode: Location identifier (5-char format for universal use)
        - city: City name
        - state: State/region name  
        - latitude/longitude: Coordinates (if available)
        - source: Geolocation service used
    
    Falls back gracefully if service unavailable (returns 500 error for frontend to handle).
    """
    try:
        # Use ipinfo.io for IP-based geolocation (free tier)
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(
                "https://ipinfo.io/json",
                headers={
                    "User-Agent": "IMO-Backend-Geolocation"
                }
            )
            
            if response.status_code != 200:
                logger.warning(f"ipinfo.io request failed: {response.status_code}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve geolocation data"
                )
            
            data = response.json()
            
            # Extract postal code (works for all countries)
            postal_code = data.get("postal", "")
            if not postal_code:
                logger.warning(f"No postal code available from ipinfo.io for country {data.get('country')}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Unable to determine postal code"
                )
            
            # Convert postal code to standardized format
            # For US (5 digits), keep as-is
            # For others, convert to 5-char alphanumeric identifier
            if postal_code.isdigit() and len(postal_code) >= 5:
                zipcode = postal_code[:5]
            else:
                # For non-US postal codes, create a 5-char identifier
                # Remove spaces and dashes, then pad to 5 chars
                cleaned = postal_code.replace(" ", "").replace("-", "")
                zipcode = (cleaned[:5] + "00000")[:5]  # Pad to 5 chars
            
            logger.info(f"Location detected - Country: {data.get('country')}, City: {data.get('city')}, Postal: {postal_code}, Zipcode: {zipcode}")
            
            # Parse latitude and longitude if available
            latitude = None
            longitude = None
            if "loc" in data:
                try:
                    loc_parts = data["loc"].split(",")
                    latitude = float(loc_parts[0])
                    longitude = float(loc_parts[1])
                except (ValueError, IndexError):
                    logger.warning(f"Failed to parse coordinates: {data.get('loc')}")
            
            return GeolocationResponse(
                zipcode=zipcode[:5],  # Ensure 5 digits
                city=data.get("city", ""),
                state=data.get("region", ""),
                latitude=latitude,
                longitude=longitude,
                source="ipinfo.io"
            )
            
    except httpx.RequestError as e:
        logger.error(f"Geolocation request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to geolocation service"
        )
    except HTTPException:
        # Re-raise HTTPExceptions (already properly formatted)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in geolocation endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
