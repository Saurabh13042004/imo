"""Reddit integration with strict product-aware filtering."""

import logging
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime

from app.config import settings
from app.utils.product_identity import (
    extract_product_identity,
    calculate_relevance_score,
    should_reject_thread,
    has_review_intent,
    normalize_relevance_score
)

logger = logging.getLogger(__name__)

REDDIT_API_BASE = "https://oauth.reddit.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


class RedditClient:
    """Client for Reddit API integration with strict product filtering."""

    def __init__(self):
        self.client_id = settings.REDDIT_CLIENT_ID
        self.client_secret = settings.REDDIT_CLIENT_SECRET
        self.base_url = REDDIT_API_BASE
        self.access_token = None
        self.timeout = getattr(settings, 'HTTP_TIMEOUT', 10)

    async def _get_access_token(self) -> Optional[str]:
        """Get Reddit OAuth access token."""
        if not self.client_id or not self.client_secret:
            logger.debug("Reddit credentials not configured")
            return None

        if self.access_token:
            return self.access_token

        try:
            auth = (self.client_id, self.client_secret)
            data = {"grant_type": "client_credentials"}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://www.reddit.com/api/v1/access_token",
                    auth=auth,
                    data=data,
                    headers=HEADERS
                )
                response.raise_for_status()

            self.access_token = response.json()["access_token"]
            return self.access_token

        except Exception as e:
            logger.debug(f"Error getting Reddit access token: {e}")
            return None

    async def search_product(self, product_name: str) -> List[Dict[str, Any]]:
        """
        Search Reddit for VERIFIED product reviews with strict filtering.
        
        Process:
        1. Extract product identity from title
        2. Search with multiple intent-based queries
        3. Filter threads by content relevance
        4. Validate review intent in comments
        5. Score relevance of extracted reviews
        
        Only returns reviews with relevance_score >= 0.6
        """
        if not product_name or len(product_name.strip()) == 0:
            return []

        # Extract product identity for filtering
        product_identity = extract_product_identity(product_name)
        logger.info(f"Extracted identity: {product_identity}")

        all_reviews = []
        seen_ids = set()

        # Intent-based queries for better discovery
        queries = [
            f'"{product_name}" review',
            f'{product_identity.get("model", "")} {product_identity.get("edition", "")} review' if product_identity.get("model") else None,
            f'{product_identity.get("model", "")} {product_identity.get("edition", "")} worth it' if product_identity.get("model") else None,
            f'{product_identity.get("model", "")} problems experience' if product_identity.get("model") else None,
        ]
        
        queries = [q for q in queries if q]  # Remove None entries
        
        logger.debug(f"Reddit queries for '{product_name}': {queries}")

        for query in queries:
            try:
                logger.debug(f"Searching Reddit: {query}")
                reviews = await self._search_query(query, product_identity)
                logger.debug(f"Query '{query}': found {len(reviews)} validated reviews")

                for review in reviews:
                    review_id = review.get("external_review_id")
                    if review_id and review_id not in seen_ids:
                        all_reviews.append(review)
                        seen_ids.add(review_id)

            except Exception as e:
                logger.warning(f"Error with query '{query}': {e}")
                continue

        logger.info(f"Discovered {len(all_reviews)} verified Reddit reviews for '{product_name}'")
        return all_reviews

    async def _search_query(self, query: str, product_identity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search Reddit with product-aware filtering.
        
        Steps:
        1. Query Reddit search API
        2. REJECT threads that don't mention model+edition
        3. REJECT threads with stock/leak/rumor keywords
        4. REJECT question-only threads without ownership
        5. Fetch and validate comments from remaining threads
        """
        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=self.timeout) as client:
                # Use Reddit's public JSON API
                url = "https://www.reddit.com/search.json"
                params = {
                    "q": query,
                    "sort": "relevance",
                    "t": "all",
                    "limit": 25,  # Fetch more to filter strictly
                    "type": "link"
                }

                response = await client.get(url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()

                threads = data.get("data", {}).get("children", [])
                logger.debug(f"Found {len(threads)} threads for query '{query}'")

                all_reviews = []
                accepted_threads = 0

                for thread_data in threads:
                    try:
                        thread = thread_data.get("data", {})
                        thread_id = thread.get("id", "")
                        thread_title = thread.get("title", "")
                        thread_body = thread.get("selftext", "")
                        permalink = thread.get("permalink", "")
                        score = thread.get("score", 0)
                        num_comments = thread.get("num_comments", 0)

                        # THREAD-LEVEL FILTERING
                        should_reject, reason = should_reject_thread(thread_title, thread_body, product_identity)
                        if should_reject:
                            logger.debug(f"Rejected thread '{thread_title[:50]}...': {reason}")
                            continue

                        # Minimum comments for quality
                        if num_comments < 3:
                            logger.debug(f"Thread has too few comments: {num_comments}")
                            continue

                        logger.debug(f"Accepted thread: '{thread_title[:60]}...'")
                        accepted_threads += 1

                        # FETCH AND VALIDATE COMMENTS
                        reviews = await self._fetch_thread_reviews(
                            thread_id, permalink, thread_title, product_identity
                        )
                        
                        if reviews:
                            logger.debug(f"Extracted {len(reviews)} valid reviews from thread")
                            all_reviews.extend(reviews)

                    except Exception as e:
                        logger.warning(f"Error processing thread '{thread_title[:40]}...': {e}")
                        continue

                logger.debug(f"Processed {accepted_threads} threads, extracted {len(all_reviews)} reviews")
                return all_reviews

        except httpx.TimeoutException:
            logger.warning(f"Reddit search timeout for query: {query}")
            return []
        except Exception as e:
            logger.error(f"Error searching Reddit: {e}")
            return []

    async def _fetch_thread_reviews(
        self,
        thread_id: str,
        permalink: str,
        thread_title: str,
        product_identity: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Fetch and validate comments from a Reddit thread.
        
        Filters:
        - Only top-level comments
        - Minimum 50 characters
        - Must have review/ownership intent
        - Relevance score >= 0.6
        """
        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=self.timeout) as client:
                url = f"https://www.reddit.com{permalink}.json"
                params = {"limit": 100, "depth": 1, "sort": "best"}

                response = await client.get(url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()

                reviews = []

                # Data structure: [thread_data, comments_data]
                if isinstance(data, list) and len(data) > 1:
                    comments_data = data[1]
                    children = comments_data.get("data", {}).get("children", [])

                    logger.debug(f"Fetched {len(children)} comments from thread")

                    for comment_data in children:
                        try:
                            comment = comment_data.get("data", {})
                            
                            # Skip moderator comments and deleted content
                            if comment.get("author") in ["[deleted]", "AutoModerator", None]:
                                continue

                            comment_body = comment.get("body", "")
                            comment_id = comment.get("id", "")
                            author = comment.get("author", "Unknown")
                            created_utc = comment.get("created_utc", 0)

                            # Minimum length check
                            if len(comment_body) < 50:
                                continue

                            # Must have review intent
                            if not has_review_intent(comment_body):
                                continue

                            # Calculate relevance score
                            relevance_score = calculate_relevance_score(comment_body, product_identity)

                            # CRITICAL: Reject if score < 0.6
                            if relevance_score < 0.6:
                                continue

                            # Create review object
                            review = {
                                "external_review_id": f"reddit_{thread_id}_{comment_id}",
                                "source_review_id": f"reddit_{thread_id}_{comment_id}",
                                "author": author,
                                "rating": None,
                                "title": thread_title[:100],
                                "content": comment_body[:2000],
                                "review_text": comment_body[:2000],
                                "source": "Reddit",
                                "source_url": f"https://reddit.com{permalink}",
                                "relevance_score": normalize_relevance_score(relevance_score),
                                "review_date": datetime.utcfromtimestamp(created_utc).isoformat() if created_utc else None,
                            }

                            reviews.append(review)

                        except Exception as e:
                            logger.debug(f"Error processing comment: {e}")
                            continue

                return reviews

        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching thread: {permalink}")
            return []
        except Exception as e:
            logger.warning(f"Error fetching thread reviews: {e}")
            return []