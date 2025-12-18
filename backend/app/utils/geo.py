"""Country and geo-targeting utilities for SerpAPI integration."""

import logging
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)

# Mapping from country name to SerpAPI parameters
COUNTRY_CONFIG: Dict[str, Dict[str, str]] = {
    "India": {
        "gl": "in",  # Google locale
        "google_domain": "google.co.in",
    },
    "United States": {
        "gl": "us",
        "google_domain": "google.com",
    },
    "Canada": {
        "gl": "ca",
        "google_domain": "google.ca",
    },
    "United Kingdom": {
        "gl": "uk",
        "google_domain": "google.co.uk",
    },
    "Brazil": {
        "gl": "br",
        "google_domain": "google.com.br",
    },
    "Mexico": {
        "gl": "mx",
        "google_domain": "google.com.mx",
    },
    "Germany": {
        "gl": "de",
        "google_domain": "google.de",
    },
    "France": {
        "gl": "fr",
        "google_domain": "google.fr",
    },
    "Japan": {
        "gl": "jp",
        "google_domain": "google.co.jp",
    },
    "Australia": {
        "gl": "au",
        "google_domain": "google.com.au",
    },
}

# Default config for unknown countries
DEFAULT_CONFIG = {
    "gl": "us",
    "google_domain": "google.com",
}


def get_country_config(country: Optional[str]) -> Dict[str, str]:
    """Get SerpAPI geo configuration for a country.
    
    Args:
        country: Country name (e.g., "India", "United States")
        
    Returns:
        Dict with 'gl' (locale) and 'google_domain' keys
    """
    if not country:
        return DEFAULT_CONFIG
    
    config = COUNTRY_CONFIG.get(country, DEFAULT_CONFIG)
    logger.debug(f"[GeoConfig] Country: {country} → gl={config['gl']}, domain={config['google_domain']}")
    return config


def build_serpapi_location(
    country: Optional[str],
    city: Optional[str] = None
) -> Tuple[str, Dict[str, str]]:
    """Build SerpAPI location string and geo parameters.
    
    Args:
        country: Country name
        city: Optional city name
        
    Returns:
        Tuple of (location_string, geo_config_dict)
        location_string format: "City,Country" or "Country"
    """
    if not country:
        country = "United States"
    
    # Build location string
    if city:
        location = f"{city},{country}"
    else:
        location = country
    
    # Get geo config
    geo_config = get_country_config(country)
    
    logger.info(
        f"[SerpAPI Location] Built location string:\\n"
        f"  Country: {country}\\n"
        f"  City: {city}\\n"
        f"  Location param: {location}\\n"
        f"  gl: {geo_config['gl']}\\n"
        f"  google_domain: {geo_config['google_domain']}"
    )
    
    return location, geo_config


def log_serpapi_params(
    keyword: str,
    location: str,
    gl: str,
    hl: str,
    google_domain: str
) -> None:
    """Log SerpAPI parameters in a clear, structured way.
    
    Args:
        keyword: Search query
        location: Location string
        gl: Google locale
        hl: Language
        google_domain: Google domain
    """
    logger.info(
        f"[SerpAPI Request] Final parameters:\\n"
        f"  engine: google_shopping\\n"
        f"  q: {keyword}\\n"
        f"  location: {location}\\n"
        f"  gl: {gl}\\n"
        f"  hl: {hl}\\n"
        f"  google_domain: {google_domain}\\n"
        f"  Expected URL: https://serpapi.com/search?engine=google_shopping&q={keyword}&location={location}&gl={gl}&hl={hl}&google_domain={google_domain}"
    )
