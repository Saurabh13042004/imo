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
