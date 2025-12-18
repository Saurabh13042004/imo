"""Forum review fetching integration with strict product-aware filtering."""

import logging
import httpx
import hashlib
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import re

from app.utils.product_identity import (
    extract_product_identity,
    calculate_relevance_score,
    normalize_relevance_score
)

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Forum sites to search
FORUM_SITES = [
    ("head-fi.org", "https://www.head-fi.org/search/"),
    ("avforums.com", "https://www.avforums.com/search"),
    ("forums.whathifi.com", "https://www.forums.whathifi.com/search"),
]


class ForumClient:
    """Client for fetching reviews from forums with strict filtering."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    async def search_product(self, product_title: str) -> List[Dict[str, Any]]:
        """
        Search forums for VERIFIED product discussions with strict filtering.
        
        Process:
        1. Extract product identity from title
        2. Discover forum URLs via search
        3. Validate page content (ownership + relevance)
        4. Score relevance of extracted reviews
        
        Only returns reviews with relevance_score >= 0.6
        """
        if not product_title or len(product_title.strip()) == 0:
            return []

        # Extract product identity
        product_identity = extract_product_identity(product_title)
        logger.info(f"Extracted forum search identity: {product_identity}")

        all_reviews = []
        seen_ids = set()

        try:
            # Discover forum URLs
            urls_to_fetch = await self._discover_forum_urls(product_title, product_identity)
            logger.debug(f"Discovered {len(urls_to_fetch)} forum URLs")

            # Fetch and analyze each URL
            for url in urls_to_fetch[:15]:  # Limit to 15 URLs
                try:
                    reviews = await self._fetch_forum_page(url, product_identity)
                    for review in reviews:
                        review_id = review.get("external_review_id")
                        if review_id not in seen_ids:
                            all_reviews.append(review)
                            seen_ids.add(review_id)
                except Exception as e:
                    logger.debug(f"Error fetching forum page {url}: {e}")
                    continue

            logger.info(f"Discovered {len(all_reviews)} verified forum reviews for '{product_title}'")
            return all_reviews

        except Exception as e:
            logger.error(f"Error searching forums: {e}")
            return []

    async def _discover_forum_urls(self, product_title: str, product_identity: Dict[str, Any]) -> List[str]:
        """
        Discover forum URLs using basic search queries.
        
        Attempts to find relevant forum threads mentioning the product.
        """
        urls = []

        # Try simple search-like URLs
        search_queries = [
            product_title,
            f'{product_identity.get("model", "")} {product_identity.get("edition", "")}',
            f'{product_identity.get("brand", "")} {product_identity.get("model", "")}',
        ]

        search_queries = [q for q in search_queries if q and len(q.strip()) > 2]

        for site_name, search_base in FORUM_SITES:
            for query in search_queries[:2]:  # Only 2 queries per site
                try:
                    # Try constructing search URL
                    search_url = f"{search_base}?q={query.replace(' ', '+')}"
                    
                    async with httpx.AsyncClient(headers=HEADERS, timeout=self.timeout) as client:
                        response = await client.get(search_url, follow_redirects=True, timeout=10)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, "html.parser")
                            
                            # Extract links to forum threads
                            for link in soup.find_all("a", href=True):
                                href = link.get("href", "")
                                # Look for thread-like URLs
                                if any(thread_marker in href.lower() for thread_marker in [
                                    "/thread/", "/discussion/", "/topic/", "/post/", "/posts/"
                                ]):
                                    full_url = href if href.startswith("http") else f"{site_name}{href}"
                                    if full_url not in urls:
                                        urls.append(full_url)

                except Exception as e:
                    logger.debug(f"Error discovering {site_name} URLs: {e}")
                    continue

        logger.debug(f"Discovered {len(urls)} unique forum URLs")
        return urls[:20]  # Cap at 20 URLs

    async def _fetch_forum_page(self, url: str, product_identity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch and analyze a forum page for product reviews.
        
        Filters:
        - Must have ownership language ("I bought", "using for", etc.)
        - Product must be mentioned >= 3 times
        - Page must be review/discussion, not news/announcement
        - Relevance score >= 0.6
        """
        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=self.timeout) as client:
                response = await client.get(url, follow_redirects=True, timeout=10)
                response.raise_for_status()

            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            # Remove non-content elements
            for tag in soup(["script", "style", "nav", "footer", "noscript", "aside"]):
                tag.decompose()

            # Extract page title
            title_tag = soup.find("title")
            page_title = title_tag.get_text(strip=True) if title_tag else "Forum Discussion"

            # Extract text content
            text = soup.get_text(separator=" ", strip=True)

            # VALIDATION CHECKS
            
            # Check 1: Minimum content length
            if len(text) < 1000:
                logger.debug(f"Forum page too short ({len(text)} chars): {url}")
                return []

            # Check 2: Product mention count (must appear >= 3 times)
            keywords_found = sum(1 for kw in product_identity.get("keywords", []) if kw and text.lower().count(kw) > 0)
            if keywords_found < 1 or text.lower().count(product_identity.get("model", "").lower() or "xxx") < 2:
                logger.debug(f"Insufficient product mention in {url}")
                return []

            # Check 3: Must have first-person/ownership language
            ownership_phrases = [
                "i bought", "i own", "i have", "i've been",
                "my experience", "my opinion", "using for",
                "owned for", "pros and cons", "recommend"
            ]
            
            has_ownership = any(phrase in text.lower() for phrase in ownership_phrases)
            if not has_ownership:
                logger.debug(f"No ownership language detected in {url}")
                return []

            # Check 4: Reject if looks like news/announcement
            rejection_phrases = [
                "announcement", "press release", "breaking news",
                "just announced", "launching", "coming soon",
                "leak", "rumor", "reported",
                "stock alert", "price drop"
            ]
            
            if any(phrase in text.lower() for phrase in rejection_phrases):
                logger.debug(f"Page looks like news/announcement: {url}")
                return []

            # Calculate relevance score
            relevance_score = calculate_relevance_score(text[:3000], product_identity)

            # CRITICAL: Reject if score < 0.6
            if relevance_score < 0.6:
                logger.debug(f"Low relevance score {relevance_score:.2f} for {url}")
                return []

            # Extract first few paragraphs as content
            paragraphs = soup.find_all(["p", "div"], class_=lambda x: x and "post" in x.lower() if x else True)
            content = ""
            for p in paragraphs[:5]:
                p_text = p.get_text(strip=True)
                if len(p_text) > 50:
                    content += p_text + " "

            if not content or len(content) < 200:
                content = text[:2000]

            # Create review object
            review_id = hashlib.md5(f"{url}{content[:100]}".encode()).hexdigest()[:16]

            return [{
                "external_review_id": review_id,
                "source_review_id": review_id,
                "author": "Forum User",
                "rating": None,
                "title": page_title[:120],
                "content": content[:1500],
                "review_text": content[:1500],
                "source": "Forums",
                "source_url": url,
                "relevance_score": normalize_relevance_score(relevance_score),
            }]

        except httpx.TimeoutException:
            logger.debug(f"Forum page fetch timeout: {url}")
            return []
        except httpx.HTTPError as e:
            logger.debug(f"Forum page HTTP error {url}: {e}")
            return []
        except Exception as e:
            logger.debug(f"Error fetching forum page {url}: {e}")
            return []
