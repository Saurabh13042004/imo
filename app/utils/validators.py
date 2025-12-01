"""Input validators."""

import re
from typing import Optional


def validate_search_query(query: str) -> bool:
    """Validate search query."""
    if not query or len(query) < 2 or len(query) > 200:
        return False
    return True


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
    return re.match(pattern, url) is not None


def validate_rating(rating: float) -> bool:
    """Validate rating is between 0 and 5."""
    return 0 <= rating <= 5


def validate_source(source: str) -> bool:
    """Validate source is supported."""
    valid_sources = {"amazon", "walmart", "google_shopping", "reddit", "youtube", "forum"}
    return source.lower() in valid_sources


def validate_sentiment(sentiment: str) -> bool:
    """Validate sentiment value."""
    valid_sentiments = {"positive", "negative", "neutral"}
    return sentiment.lower() in valid_sentiments
