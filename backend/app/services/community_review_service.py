"""Service for fetching community reviews from Reddit and forums."""

import logging
from typing import List, Dict, Any
import httpx
import asyncio
from bs4 import BeautifulSoup
import re
from app.config import settings
from app.services.scraper import (
    fetch_html,
    extract_text_blocks,
    clean_text,
    get_domain,
    deduplicate_reviews,
)

logger = logging.getLogger(__name__)

# Singleton HTTP client with larger connection pool to avoid "pool is full" warnings
_http_client = None

def get_http_client() -> httpx.AsyncClient:
    """Get or create singleton HTTP client with larger pool."""
    global _http_client
    if _http_client is None:
        limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
        _http_client = httpx.AsyncClient(timeout=30.0, limits=limits)
    return _http_client


class CommunityReviewService:
    """Service for fetching and extracting community reviews."""
    
    def __init__(self):
        self.serpapi_key = settings.SERPAPI_KEY
        self.base_url = "https://serpapi.com/search"
        self.client = get_http_client()
    
    async def fetch_community_reviews(self, product_title: str, brand: str = "") -> Dict[str, Any]:
        """
        Fetch community reviews from Reddit and forums with improved queries.
        
        Args:
            product_title: Product title for search
            brand: Optional brand name
        
        Returns:
            Dict with extracted reviews
        """
        query_prefix = f"{product_title}"
        if brand:
            query_prefix = f"{brand} {product_title}"
        
        # Enhanced search queries with forum bias
        queries = [
            # Reddit searches
            f"{query_prefix} review site:reddit.com",
            f"{query_prefix} worth it reddit",
            f"{query_prefix} problems site:reddit.com",
            
            # Forum-biased searches
            f"{query_prefix} review forum",
            f"{query_prefix} discussion thread",
            f"{query_prefix} user experience forum",
            f"{query_prefix} problems site:forum",
            f"{query_prefix} issues discussion",
        ]
        
        try:
            # Fetch all search results in parallel (limited to avoid rate limits)
            results = await asyncio.gather(
                *[self._search_and_extract(q) for q in queries[:6]],  # Limit queries
                return_exceptions=True
            )
            
            # Flatten results
            all_reviews = []
            for result in results:
                if isinstance(result, list):
                    all_reviews.extend(result)
                elif isinstance(result, Exception):
                    logger.warning(f"Error in search: {result}")
            
            # Apply deduplication
            all_reviews = deduplicate_reviews(all_reviews)
            
            return {
                "reviews": all_reviews,
                "total_found": len(all_reviews),
            }
        except Exception as e:
            logger.error(f"Error fetching community reviews: {e}")
            return {"reviews": [], "total_found": 0, "error": str(e)}
    
    async def _search_and_extract(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for query and extract reviews from results.
        
        Args:
            query: Search query
        
        Returns:
            List of extracted reviews
        """
        try:
            # Get search results from SerpAPI
            search_results = await self._serpapi_search(query)
            reviews = []
            
            # Extract from organic results
            for result in search_results.get('organic_results', [])[:5]:  # Limit to top 5
                try:
                    url = result.get('link')
                    title = result.get('title', '')
                    snippet = result.get('snippet', '')
                    
                    if not url:
                        continue
                    
                    # Determine source
                    domain = get_domain(url)
                    is_reddit = 'reddit' in url.lower()
                    source = 'reddit' if is_reddit else 'forum'
                    
                    # Fetch full page content
                    html = await fetch_html(url)
                    if not html:
                        continue
                    
                    # Extract with domain-specific strategy
                    if is_reddit:
                        text_blocks = self._extract_reddit_content(html)
                    else:
                        text_blocks = self._extract_forum_content(html)
                    
                    # Add to reviews
                    for text in text_blocks:
                        cleaned = clean_text(text)
                        if cleaned and len(cleaned) >= 50:  # Enforce minimum length
                            reviews.append({
                                "source": source,
                                "text": cleaned,
                                "url": url,
                                "title": title,
                                "snippet": snippet,
                            })
                            
                except Exception as e:
                    logger.debug(f"Error extracting from {result.get('link', 'unknown')}: {e}")
                    continue
            
            return reviews
        except Exception as e:
            logger.warning(f"Error searching '{query}': {e}")
            return []
    
    def _extract_reddit_content(self, html: str) -> List[str]:
        """
        Extract Reddit-specific content: post body and top comments only.
        Remove sidebar, related answers, footer, navigation.
        
        Args:
            html: HTML content
        
        Returns:
            List of extracted text blocks
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove noise elements
            for elem in soup.find_all(['script', 'style', 'nav', 'footer', '[data-testid="sidebar"]']):
                elem.decompose()
            
            blocks = []
            
            # Extract post body
            # Reddit post content patterns
            post_patterns = [
                {'class': re.compile(r'md-|Post|post', re.I)},
                {'data-testid': re.compile(r'post-content', re.I)},
            ]
            
            for attrs in post_patterns:
                post_elem = soup.find('div', attrs=attrs)
                if post_elem:
                    text = post_elem.get_text(strip=True)
                    if text and len(text) >= 50:
                        blocks.append(text)
                        break
            
            # Extract top comments (limit to first 3)
            comment_patterns = [
                {'data-testid': re.compile(r'comment', re.I)},
                {'class': re.compile(r'comment', re.I)},
                {'class': re.compile(r'Comment', re.I)},
            ]
            
            comment_count = 0
            for attrs in comment_patterns:
                for comment_elem in soup.find_all('div', attrs=attrs, limit=3):
                    # Skip deleted comments
                    text = comment_elem.get_text(strip=True)
                    if text and '[deleted]' not in text and len(text) >= 40:
                        blocks.append(text)
                        comment_count += 1
                        if comment_count >= 3:
                            break
                if comment_count >= 3:
                    break
            
            return blocks
            
        except Exception as e:
            logger.warning(f"Error extracting Reddit content: {e}")
            return extract_text_blocks(html)  # Fallback
    
    def _extract_forum_content(self, html: str) -> List[str]:
        """
        Extract forum-specific content: discussion threads with usernames/timestamps.
        Ignore quoted replies, signatures, ads.
        
        Args:
            html: HTML content
        
        Returns:
            List of extracted text blocks
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove noise elements
            for elem in soup.find_all(['script', 'style', 'nav', 'footer', 'aside', '[class*="signature"]']):
                elem.decompose()
            
            blocks = []
            
            # Look for discussion posts/comments
            # Common forum patterns
            patterns = [
                {'class': re.compile(r'post|message|comment|reply', re.I)},
                {'class': re.compile(r'forum-post', re.I)},
                {'data-testid': re.compile(r'post|comment', re.I)},
            ]
            
            post_count = 0
            for attrs in patterns:
                for post_elem in soup.find_all('div', attrs=attrs, limit=10):
                    text = post_elem.get_text(strip=True)
                    
                    # Filter out quoted replies (typically indented or marked as quote)
                    if '>>' in text or text.startswith('>') or '[quote' in text.lower():
                        continue
                    
                    # Skip if too short
                    if len(text) < 50:
                        continue
                    
                    # Skip signatures (usually at end, after ---)
                    if '---' in text:
                        text = text.split('---')[0]
                    
                    if text and len(text) >= 40:
                        blocks.append(text)
                        post_count += 1
                        if post_count >= 10:
                            break
                
                if post_count >= 10:
                    break
            
            # Fallback to generic extraction if no forum posts found
            if not blocks:
                blocks = extract_text_blocks(html)
            
            return blocks
            
        except Exception as e:
            logger.warning(f"Error extracting forum content: {e}")
            return extract_text_blocks(html)  # Fallback
    
    async def _serpapi_search(self, query: str) -> Dict[str, Any]:
        """
        Search using SerpAPI.
        
        Args:
            query: Search query
        
        Returns:
            Search results
        """
        try:
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "engine": "google",
                "num": 10,
            }
            
            # Use persistent client instead of creating new one
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"SerpAPI search failed for '{query}': {e}")
            return {"organic_results": []}
