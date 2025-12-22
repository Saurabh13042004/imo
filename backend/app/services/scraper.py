"""Scraper utilities for generic web content extraction."""

import re
import hashlib
from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

# Singleton HTTP client for scraper with larger connection pool
_scraper_client = None

def get_scraper_client() -> httpx.AsyncClient:
    """Get or create singleton HTTP client for scraper."""
    global _scraper_client
    if _scraper_client is None:
        limits = httpx.Limits(max_connections=50, max_keepalive_connections=10)
        _scraper_client = httpx.AsyncClient(timeout=10.0, limits=limits)
    return _scraper_client

# Opinion keywords for review detection
OPINION_KEYWORDS = {
    'positive': ['good', 'great', 'excellent', 'amazing', 'love', 'best', 'perfect', 'works', 'recommend', 'worth', 'quality', 'impressive', 'satisfied', 'happy', 'fantastic', 'awesome', 'brilliant'],
    'negative': ['bad', 'terrible', 'poor', 'worst', 'hate', 'issue', 'problem', 'broken', 'waste', 'disappointing', 'fail', 'regret', 'defective', 'useless', 'awful', 'horrible', 'annoying', 'frustrating'],
    'neutral': ['ok', 'okay', 'average', 'decent', 'meh', 'alright', 'neutral', 'fine']
}

# Patterns indicating JS rendering required
JS_REQUIRED_INDICATORS = [
    'enable javascript',
    'javascript required',
    'please enable javascript',
    'cookies required',
    'cookie policy',
    'accept cookies',
]

# Patterns to filter out non-review content
NOISE_PATTERNS = [
    'cookie', 'privacy policy', 'terms of service', 'advertisement',
    'click here', 'subscribe', 'follow', 'share', 'like', 'comment',
    'loading', 'error', 'exception', 'failed', 'network error',
    'sidebar', 'navigation', 'menu', 'search', 'filter', 'sort by',
    'view more', 'show more', 'load more', 'pagination',
    'newsletter', 'email', 'sign up', 'log in', 'register',
    'copyright', 'all rights reserved', 'contact us', 'about us'
]

MIN_TEXT_LENGTH = 50
MAX_TEXT_LENGTH = 3000


async def fetch_html(url: str, timeout: int = 10) -> str | None:
    """
    Fetch HTML content from a URL with error handling.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
    
    Returns:
        HTML content or None if fetch fails
    """
    try:
        client = get_scraper_client()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = await client.get(url, headers=headers, follow_redirects=True)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None


def needs_js_rendering(html: str) -> bool:
    """
    Determine if a page requires JS rendering.
    
    Args:
        html: HTML content
    
    Returns:
        True if JS rendering is needed
    """
    if not html:
        return False
    
    html_lower = html.lower()
    
    # Check for JS requirement indicators
    for indicator in JS_REQUIRED_INDICATORS:
        if indicator in html_lower:
            logger.debug(f"JS rendering required: detected '{indicator}'")
            return True
    
    # Check if page has minimal content (likely JS-rendered)
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup(['script', 'style', 'meta']):
        script.decompose()
    
    text = soup.get_text().strip()
    if len(text) < 200:
        logger.debug("JS rendering required: minimal text content")
        return True
    
    # Check if any review-like elements are present
    review_keywords = ['review', 'rating', 'star', 'comment', 'feedback', 'opinion']
    has_review_elements = any(kw in html_lower for kw in review_keywords)
    
    if not has_review_elements and len(text) > 500:
        logger.debug("JS rendering likely needed: no review elements found")
        return True
    
    return False


def extract_text_blocks(html: str, min_length: int = MIN_TEXT_LENGTH) -> List[str]:
    """
    Extract text blocks from HTML that might contain reviews.
    Implements strict filtering to avoid noise.
    
    Args:
        html: HTML content
        min_length: Minimum text length to consider
    
    Returns:
        List of extracted text blocks
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style', 'meta', 'noscript']):
            script.decompose()
        
        blocks = []
        
        # Extract from common review containers with preference for meaningful tags
        selectors = [
            ('article', {}),
            ('div', {'class': re.compile(r'review|comment|feedback|opinion|rating', re.I)}),
            ('div', {'data-testid': re.compile(r'review|comment', re.I)}),
            ('p', {}),
            ('span', {}),
        ]
        
        seen_hashes = set()  # Track seen content for dedup
        
        for tag_name, attrs in selectors:
            for elem in soup.find_all(tag_name, attrs=attrs, limit=200):
                text = elem.get_text(strip=True)
                
                # Length checks
                if len(text) < min_length or len(text) > MAX_TEXT_LENGTH:
                    continue
                
                # Check if contains opinion keywords
                text_lower = text.lower()
                has_opinion = any(
                    keyword in text_lower 
                    for keywords in OPINION_KEYWORDS.values() 
                    for keyword in keywords
                )
                
                if not has_opinion:
                    continue
                
                # Filter noise patterns
                is_noise = any(pattern in text_lower for pattern in NOISE_PATTERNS)
                if is_noise:
                    continue
                
                # Avoid repeated social media text
                if len(text) < 80 and text.count(' ') < 5:
                    continue  # Skip very short fragments
                
                # Deduplicate
                text_hash = hashlib.md5(text.encode()).hexdigest()
                if text_hash in seen_hashes:
                    continue
                seen_hashes.add(text_hash)
                
                blocks.append(text)
        
        return blocks
    except Exception as e:
        logger.warning(f"Error extracting text blocks: {e}")
        return []


def extract_rating(text: str) -> float | None:
    """
    Extract rating from text using regex patterns.
    
    Args:
        text: Text that might contain rating
    
    Returns:
        Rating (1-5) or None
    """
    try:
        # Match patterns like: 4.5, 4/5, ★★★★, 5 out of 5
        patterns = [
            r'(\d+\.?\d*)\s*(?:out of|/)\s*5',  # 4.5/5, 4 out of 5
            r'★{1,5}',  # Star ratings
            r'(?:rating|score)[:\s]+(\d+\.?\d*)',  # Rating: 4.5
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if '★' in match.group(0):
                    return float(match.group(0).count('★'))
                else:
                    rating = float(match.group(1))
                    return min(5.0, max(1.0, rating))  # Clamp to 1-5
        
        return None
    except Exception as e:
        logger.warning(f"Error extracting rating: {e}")
        return None


def extract_username(html: str) -> str | None:
    """
    Extract potential username/author from HTML.
    
    Args:
        html: HTML content
    
    Returns:
        Username or None
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for common author patterns
        patterns = [
            soup.find('span', class_=re.compile(r'author|user|name', re.I)),
            soup.find('div', class_=re.compile(r'reviewer|commenter', re.I)),
            soup.find('meta', attrs={'name': 'author'}),
        ]
        
        for elem in patterns:
            if elem:
                if elem.name == 'meta':
                    return elem.get('content', '').strip()
                text = elem.get_text(strip=True)
                if text and len(text) < 50:  # Usernames are typically short
                    return text
        
        return None
    except Exception as e:
        logger.warning(f"Error extracting username: {e}")
        return None


def clean_text(text: str) -> str:
    """
    Clean extracted text for consistency.
    
    Args:
        text: Raw text
    
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove common HTML artifacts
    text = re.sub(r'&[a-z]+;', '', text, flags=re.IGNORECASE)
    
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    return text.strip()


def get_domain(url: str) -> str:
    """
    Extract domain name from URL.
    
    Args:
        url: URL
    
    Returns:
        Domain name
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        return domain.split('.')[0]  # Get main domain name
    except Exception:
        return 'unknown'


def text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts (0-1).
    
    Args:
        text1: First text
        text2: Second text
    
    Returns:
        Similarity score (0=completely different, 1=identical)
    """
    if not text1 or not text2:
        return 0.0
    
    # Normalize texts
    t1 = ' '.join(text1.lower().split())[:200]  # First 200 chars
    t2 = ' '.join(text2.lower().split())[:200]
    
    return SequenceMatcher(None, t1, t2).ratio()


def deduplicate_reviews(reviews: List[Dict[str, Any]], similarity_threshold: float = 0.90) -> List[Dict[str, Any]]:
    """
    Remove exact and near-duplicate reviews.
    
    Args:
        reviews: List of review dicts with 'text' key
        similarity_threshold: Threshold for near-duplicate detection (0.90 = 90% similar)
    
    Returns:
        Deduplicated list
    """
    if not reviews:
        return []
    
    # First pass: exact duplicates
    seen_hashes = {}
    unique_reviews = []
    
    for review in reviews:
        text = review.get('text', '').strip()
        if not text:
            continue
        
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        if text_hash not in seen_hashes:
            seen_hashes[text_hash] = True
            unique_reviews.append(review)
    
    logger.info(f"After exact dedup: {len(unique_reviews)} from {len(reviews)}")
    
    # Second pass: near-duplicates using similarity
    final_reviews = []
    
    for i, review in enumerate(unique_reviews):
        text_i = review.get('text', '')
        is_duplicate = False
        
        # Compare against already-kept reviews
        for kept_review in final_reviews:
            text_kept = kept_review.get('text', '')
            similarity = text_similarity(text_i, text_kept)
            
            if similarity >= similarity_threshold:
                logger.debug(f"Removing near-duplicate: {similarity:.2f} similarity")
                is_duplicate = True
                break
        
        if not is_duplicate:
            final_reviews.append(review)
    
    logger.info(f"After similarity dedup: {len(final_reviews)} from {len(unique_reviews)}")
    
    return final_reviews
