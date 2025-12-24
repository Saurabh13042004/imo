"""Utility helpers."""

import re
from typing import Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


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


def parse_relative_date(date_str: Optional[str]) -> Optional[str]:
    """
    Parse relative date strings from SerpAPI reviews and convert to ISO format.
    
    Handles various formats:
    - Absolute dates: "2024-12-25", "Dec 25, 2024", "25/12/2024"
    - Relative dates: "a year ago", "7 months ago", "2 weeks ago", "3 days ago"
    - Special cases: "TL; DR", mixed text with dates
    
    Args:
        date_str: Date string from SerpAPI review
        
    Returns:
        ISO format date string (YYYY-MM-DDTHH:MM:SSZ) or None if parsing fails
    """
    if not date_str or not isinstance(date_str, str):
        return None
    
    date_str = date_str.strip()
    
    if not date_str:
        return None
    
    try:
        # Try to parse as ISO format first
        if 'T' in date_str or '-' in date_str[:10]:
            try:
                parsed = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return parsed.isoformat() + 'Z'
            except (ValueError, AttributeError):
                pass
        
        # Handle relative date formats
        # "a year ago", "1 year ago"
        year_match = re.search(r'(\d+)?\s*year[s]?\s+ago', date_str, re.IGNORECASE)
        if year_match:
            years = int(year_match.group(1)) if year_match.group(1) else 1
            calculated_date = datetime.utcnow() - timedelta(days=365 * years)
            return calculated_date.isoformat() + 'Z'
        
        # "a month ago", "7 months ago"
        month_match = re.search(r'(\d+)?\s*month[s]?\s+ago', date_str, re.IGNORECASE)
        if month_match:
            months = int(month_match.group(1)) if month_match.group(1) else 1
            # Approximate months to days (30 days per month)
            calculated_date = datetime.utcnow() - timedelta(days=30 * months)
            return calculated_date.isoformat() + 'Z'
        
        # "a week ago", "2 weeks ago"
        week_match = re.search(r'(\d+)?\s*week[s]?\s+ago', date_str, re.IGNORECASE)
        if week_match:
            weeks = int(week_match.group(1)) if week_match.group(1) else 1
            calculated_date = datetime.utcnow() - timedelta(weeks=weeks)
            return calculated_date.isoformat() + 'Z'
        
        # "a day ago", "3 days ago"
        day_match = re.search(r'(\d+)?\s*day[s]?\s+ago', date_str, re.IGNORECASE)
        if day_match:
            days = int(day_match.group(1)) if day_match.group(1) else 1
            calculated_date = datetime.utcnow() - timedelta(days=days)
            return calculated_date.isoformat() + 'Z'
        
        # "an hour ago", "2 hours ago"
        hour_match = re.search(r'(\d+)?\s*hour[s]?\s+ago', date_str, re.IGNORECASE)
        if hour_match:
            hours = int(hour_match.group(1)) if hour_match.group(1) else 1
            calculated_date = datetime.utcnow() - timedelta(hours=hours)
            return calculated_date.isoformat() + 'Z'
        
        # Try common date formats
        common_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%B %d, %Y',
            '%b %d, %Y',
            '%d %B %Y',
            '%d %b %Y',
            '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y %H:%M:%S',
        ]
        
        for fmt in common_formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.isoformat() + 'Z'
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date string: {date_str}")
        return None
        
    except Exception as e:
        logger.warning(f"Error parsing date '{date_str}': {e}")
        return None

