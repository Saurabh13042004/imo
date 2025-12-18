"""Location service for converting zipcodes to formatted location strings for SerpAPI."""

import logging
import httpx
from typing import Optional, Dict, Any
from app.utils.helpers import format_location_for_serpapi

logger = logging.getLogger(__name__)

# Cache for zipcode -> location lookups (to avoid repeated API calls)
LOCATION_CACHE: Dict[str, Dict[str, Any]] = {}


class LocationService:
    """Service for handling location-related operations."""

    @staticmethod
    async def get_location_string_for_serpapi(zipcode: str) -> str:
        """Get formatted location string for SerpAPI from zipcode.
        
        This method:
        1. Checks cache first
        2. Makes a backend geolocation API call if not cached
        3. Formats the result as "City, State, Country"
        4. Falls back to default if not found
        
        Args:
            zipcode: Postal code/zipcode
            
        Returns:
            Formatted location string for SerpAPI (e.g., "Austin, Texas, United States")
        """
        try:
            # Check cache first
            if zipcode in LOCATION_CACHE:
                logger.debug(f"[Location] Cache hit for zipcode: {zipcode}")
                cached = LOCATION_CACHE[zipcode]
                return format_location_for_serpapi(
                    zipcode=zipcode,
                    city=cached.get("city"),
                    state=cached.get("state"),
                    country=cached.get("country")
                )
            
            # Attempt to get location data (this would be from ipinfo.io or similar)
            # For now, we'll use a mapping of common zipcodes
            location_data = await LocationService._lookup_zipcode(zipcode)
            
            if location_data:
                # Cache the result
                LOCATION_CACHE[zipcode] = location_data
                logger.info(
                    f"[Location] Resolved zipcode {zipcode} to "
                    f"{location_data.get('city')}, {location_data.get('state')}, {location_data.get('country')}"
                )
                return format_location_for_serpapi(
                    zipcode=zipcode,
                    city=location_data.get("city"),
                    state=location_data.get("state"),
                    country=location_data.get("country")
                )
            
            # Fallback: just use zipcode
            logger.warning(f"[Location] Could not resolve zipcode {zipcode}, using zipcode as-is")
            return zipcode
            
        except Exception as e:
            logger.error(f"[Location] Error getting location string: {e}", exc_info=True)
            # Fallback to zipcode
            return zipcode

    @staticmethod
    async def _lookup_zipcode(zipcode: str) -> Optional[Dict[str, Any]]:
        """Look up zipcode to get city, state, country.
        
        Uses a combination of:
        1. Built-in mapping for common zipcodes
        2. External API if needed (geocodio, nominatim, etc.)
        
        Args:
            zipcode: Postal code to look up
            
        Returns:
            Dict with city, state, country or None if not found
        """
        try:
            # Built-in mapping for common US zipcodes
            US_ZIPCODE_MAP = {
                "60607": {"city": "Chicago", "state": "Illinois", "country": "United States"},
                "60611": {"city": "Chicago", "state": "Illinois", "country": "United States"},
                "60614": {"city": "Chicago", "state": "Illinois", "country": "United States"},
                "10001": {"city": "New York", "state": "New York", "country": "United States"},
                "10002": {"city": "New York", "state": "New York", "country": "United States"},
                "90001": {"city": "Los Angeles", "state": "California", "country": "United States"},
                "90210": {"city": "Los Angeles", "state": "California", "country": "United States"},
                "98101": {"city": "Seattle", "state": "Washington", "country": "United States"},
                "77001": {"city": "Houston", "state": "Texas", "country": "United States"},
                "75201": {"city": "Dallas", "state": "Texas", "country": "United States"},
                "30303": {"city": "Atlanta", "state": "Georgia", "country": "United States"},
                "02101": {"city": "Boston", "state": "Massachusetts", "country": "United States"},
                "85001": {"city": "Phoenix", "state": "Arizona", "country": "United States"},
                "19101": {"city": "Philadelphia", "state": "Pennsylvania", "country": "United States"},
                "78201": {"city": "San Antonio", "state": "Texas", "country": "United States"},
                "92101": {"city": "San Diego", "state": "California", "country": "United States"},
                "94102": {"city": "San Francisco", "state": "California", "country": "United States"},
                "80202": {"city": "Denver", "state": "Colorado", "country": "United States"},
                "89101": {"city": "Las Vegas", "state": "Nevada", "country": "United States"},
                "33101": {"city": "Miami", "state": "Florida", "country": "United States"},
            }
            
            # Built-in mapping for Indian postal codes (common ones)
            INDIA_POSTAL_MAP = {
                "50000": {"city": "Hyderabad", "state": "Telangana", "country": "India"},
                "50001": {"city": "Hyderabad", "state": "Telangana", "country": "India"},
                "50002": {"city": "Hyderabad", "state": "Telangana", "country": "India"},
                "50003": {"city": "Hyderabad", "state": "Telangana", "country": "India"},
                "50004": {"city": "Hyderabad", "state": "Telangana", "country": "India"},
                "50005": {"city": "Hyderabad", "state": "Telangana", "country": "India"},
                "40001": {"city": "Mumbai", "state": "Maharashtra", "country": "India"},
                "40002": {"city": "Mumbai", "state": "Maharashtra", "country": "India"},
                "30001": {"city": "Bangalore", "state": "Karnataka", "country": "India"},
                "30002": {"city": "Bangalore", "state": "Karnataka", "country": "India"},
                "70001": {"city": "Kolkata", "state": "West Bengal", "country": "India"},
                "70002": {"city": "Kolkata", "state": "West Bengal", "country": "India"},
                "11001": {"city": "New Delhi", "state": "Delhi", "country": "India"},
                "11002": {"city": "New Delhi", "state": "Delhi", "country": "India"},
            }
            
            # Check US map first
            if zipcode in US_ZIPCODE_MAP:
                return US_ZIPCODE_MAP[zipcode]
            
            # Check India map
            if zipcode in INDIA_POSTAL_MAP:
                return INDIA_POSTAL_MAP[zipcode]
            
            # Try Nominatim (free, no API key needed) as fallback
            logger.debug(f"[Location] Zipcode {zipcode} not in local maps, attempting Nominatim lookup")
            async with httpx.AsyncClient(timeout=5) as client:
                # Use Nominatim reverse geocoding to get location from postal code
                response = await client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={
                        "postalcode": zipcode,
                        "format": "json",
                        "limit": 1
                    },
                    headers={"User-Agent": "IMO-Backend"}
                )
                
                if response.status_code == 200:
                    results = response.json()
                    if results:
                        result = results[0]
                        # Extract location components from address
                        address = result.get("address", {})
                        return {
                            "city": address.get("city") or address.get("town") or result.get("name", ""),
                            "state": address.get("state", ""),
                            "country": address.get("country", "")
                        }
            
            logger.debug(f"[Location] Could not resolve zipcode {zipcode} from any source")
            return None
            
        except Exception as e:
            logger.error(f"[Location] Error in _lookup_zipcode: {e}", exc_info=True)
            return None
