"""Utility helpers."""

import re
from typing import Optional, List


def sanitize_input(text: str, max_length: int = 500) -> str:
    """Sanitize user input."""
    if not text:
        return ""
    # Remove special characters but keep spaces
    text = re.sub(r"[^\w\s-]", "", text)
    return text[:max_length].strip()


def validate_price(price: float) -> bool:
    """Validate price is reasonable."""
    return 0 < price <= 1000000


def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL."""
    if not url:
        return None
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency for display."""
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def clean_html(text: str) -> str:
    """Remove HTML tags from text."""
    if not text:
        return ""
    import re
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text).strip()


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to max length with ellipsis."""
    if not text:
        return ""
    if len(text) > max_length:
        return text[:max_length].rsplit(" ", 1)[0] + "..."
    return text


def format_location_for_serpapi(
    zipcode: str,
    city: Optional[str] = None,
    state: Optional[str] = None,
    country: Optional[str] = None
) -> str:
    """Format location string for SerpAPI requests.
    
    SerpAPI expects location in format: "City, State, Country"
    Example: "Austin, Texas, United States"
    
    Args:
        zipcode: Postal code (used as fallback)
        city: City name
        state: State/region name
        country: Country name
        
    Returns:
        Formatted location string suitable for SerpAPI
    """
    # Build location string from available parts
    location_parts = []
    
    if city:
        location_parts.append(city)
    if state:
        location_parts.append(state)
    if country:
        location_parts.append(country)
    
    # If we have meaningful parts, use them
    if location_parts:
        formatted = ", ".join(location_parts)
        return formatted
    
    # Fallback to zipcode if no city/state/country available
    # For compatibility with systems that only have zipcode
    if zipcode:
        return zipcode
    
    # Last resort fallback
    return "United States"
