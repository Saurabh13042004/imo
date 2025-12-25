"""Celery tasks for review operations."""

import logging
import asyncio
from typing import Dict, Any, List
from app.celery_app import celery_app
from app.services.community_review_service import CommunityReviewService
from app.services.ai_review_service import AIReviewService
from app.services.store_review_service import StoreReviewService
from app.services.google_review_service import GoogleReviewService

logger = logging.getLogger(__name__)


def run_async_in_thread(coro):
    """Helper to run async code in Celery worker thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    name="app.tasks.review_tasks.fetch_community_reviews",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="reviews"
)
def fetch_community_reviews_task(
    self,
    product_name: str,
    brand: str = ""
) -> Dict[str, Any]:
    """
    Celery task for fetching community reviews from Reddit and forums.
    
    Args:
        product_name: Name of the product
        brand: Optional brand name
        
    Returns:
        Dictionary with normalized reviews and metadata
    """
    try:
        logger.info(f"[Task {self.request.id}] Starting community reviews fetch for: {product_name}")
        
        # Step 1: Fetch raw reviews
        community_service = CommunityReviewService()
        raw_data = run_async_in_thread(
            community_service.fetch_community_reviews(
                product_title=product_name,
                brand=brand
            )
        )
        
        raw_reviews = raw_data.get("reviews", [])
        logger.info(f"[Task {self.request.id}] Raw reviews fetched: {len(raw_reviews)}")
        
        # Step 2: Validate with AI
        ai_service = AIReviewService()
        validation_result = run_async_in_thread(
            ai_service.validate_and_normalize_reviews(
                raw_reviews,
                context="community"
            )
        )
        validated_reviews = validation_result.get("reviews", [])
        logger.info(
            f"[Task {self.request.id}] Validated reviews: {len(validated_reviews)} "
            f"(filtered {validation_result.get('filtered_count', 0)})"
        )
        
        # Step 3: Normalize with AI to get sentiment/summary
        normalized = run_async_in_thread(
            ai_service.normalize_community_reviews(validated_reviews)
        )
        
        # Step 4: Format community reviews with Gemini AI (extract rating and 1-2 line summary)
        logger.info(f"[Task {self.request.id}] Formatting community reviews with Gemini AI...")
        formatted_result = run_async_in_thread(
            ai_service.format_community_reviews(validated_reviews)
        )
        formatted_reviews = formatted_result.get("formatted_reviews", [])
        logger.info(f"[Task {self.request.id}] Formatted {len(formatted_reviews)} reviews")
        
        # Return complete result
        result = {
            "success": True,
            "product_name": product_name,
            "source": "community",
            "summary": {
                "overall_sentiment": normalized.get("overall_sentiment", "neutral"),
                "common_praises": normalized.get("common_praises", []),
                "common_complaints": normalized.get("common_complaints", []),
            },
            "reviews": formatted_reviews,  # Now returns structured reviews with rating, title, text
            "total_found": len(validated_reviews),
            "raw_count": len(raw_reviews),
        }
        
        logger.info(f"[Task {self.request.id}] Community reviews task completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"[Task {self.request.id}] Error fetching community reviews: {e}", exc_info=True)
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task(
    name="app.tasks.review_tasks.fetch_store_reviews",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="reviews"
)
def fetch_store_reviews_task(
    self,
    product_name: str,
    store_urls: List[str]
) -> Dict[str, Any]:
    """
    Celery task for fetching store reviews from retailer websites.
    
    Args:
        product_name: Name of the product
        store_urls: List of store URLs to scrape
        
    Returns:
        Dictionary with normalized reviews and metadata
    """
    try:
        logger.info(
            f"[Task {self.request.id}] Starting store reviews fetch for: {product_name} "
            f"from {len(store_urls)} URLs"
        )
        
        # Step 1: Fetch raw reviews
        store_service = StoreReviewService()
        raw_data = run_async_in_thread(
            store_service.fetch_store_reviews(store_urls)
        )
        raw_reviews = raw_data.get("reviews", [])
        logger.info(f"[Task {self.request.id}] Raw reviews fetched: {len(raw_reviews)}")
        
        # Step 2: Validate with AI
        ai_service = AIReviewService()
        validation_result = run_async_in_thread(
            ai_service.validate_and_normalize_reviews(
                raw_reviews,
                context="store"
            )
        )
        validated_reviews = validation_result.get("reviews", [])
        logger.info(
            f"[Task {self.request.id}] Validated reviews: {len(validated_reviews)} "
            f"(filtered {validation_result.get('filtered_count', 0)})"
        )
        
        # Step 3: Normalize with AI
        normalized = run_async_in_thread(
            ai_service.normalize_store_reviews(validated_reviews)
        )
        
        # Return complete result
        result = {
            "success": True,
            "product_name": product_name,
            "source": "store",
            "summary": {
                "average_rating": normalized.get("average_rating", 0),
                "trust_score": normalized.get("trust_score", 0),
                "verified_patterns": normalized.get("verified_patterns", {"positive": [], "negative": []}),
            },
            "reviews": [
                {
                    "store": r.get("store", "unknown"),
                    "text": r.get("text", ""),
                    "rating": r.get("rating"),
                    "confidence": r.get("validation_confidence", 1.0),
                }
                for r in validated_reviews[:25]
            ],
            "total_found": len(validated_reviews),
            "raw_count": len(raw_reviews),
        }
        
        logger.info(f"[Task {self.request.id}] Store reviews task completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"[Task {self.request.id}] Error fetching store reviews: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task(
    name="app.tasks.review_tasks.fetch_google_reviews",
    bind=True,
    max_retries=2,
    default_retry_delay=90,
    queue="reviews",
    time_limit=1800,  # 30 minutes
    soft_time_limit=1500,  # 25 minutes
)
def fetch_google_reviews_task(
    self,
    product_name: str,
    google_shopping_url: str
) -> Dict[str, Any]:
    """
    Celery task for fetching Google Shopping reviews with progressive streaming.
    
    Updates task state with partial results as reviews are scraped incrementally,
    allowing the frontend to display reviews progressively without waiting.
    
    Args:
        product_name: Name of the product
        google_shopping_url: Full Google Shopping URL
        
    Returns:
        Dictionary with normalized reviews and metadata
    """
    try:
        logger.info(
            f"[Task {self.request.id}] Starting Google Shopping reviews fetch for: {product_name}"
        )
        
        # Step 1: Scrape Google Shopping page with direct streaming to task state
        logger.info(f"[Task {self.request.id}] Google Shopping URL: {google_shopping_url}")
        google_service = GoogleReviewService()
        scrape_result = google_service.fetch_google_reviews_with_streaming(
            google_shopping_url=google_shopping_url,
            product_name=product_name,
            celery_task=self  # Pass task so service can update state directly
        )
        
        if not scrape_result.get("success"):
            error_msg = scrape_result.get('error', 'Unknown error')
            logger.error(f"[Task {self.request.id}] Google Shopping scraper failed: {error_msg}")
            raise Exception(f"Failed to scrape Google Shopping: {error_msg}")
        
        raw_reviews = scrape_result.get("reviews", [])
        logger.info(f"[Task {self.request.id}] ✓ Final: {len(raw_reviews)} reviews scraped")
        
        # Limit to first 100 reviews for faster processing
        if len(raw_reviews) > 100:
            logger.info(
                f"[Task {self.request.id}] Limiting to first 100 reviews "
                f"(found {len(raw_reviews)})"
            )
            raw_reviews = raw_reviews[:100]
        
        # Step 2: Apply basic validation
        logger.debug(f"[Task {self.request.id}] Applying basic validation...")
        validated_reviews = [
            r for r in raw_reviews 
            if r.get("text") and len(r.get("text", "")) > 10
        ]
        filtered_count = len(raw_reviews) - len(validated_reviews)
        logger.info(
            f"[Task {self.request.id}] Basic validation: {len(validated_reviews)} reviews "
            f"(filtered {filtered_count})"
        )
        
        # Step 3: Build summary from validated reviews
        logger.debug(f"[Task {self.request.id}] Building response summary...")
        try:
            ratings = [r.get("rating", 0) for r in validated_reviews if r.get("rating")]
            average_rating = sum(ratings) / len(ratings) if ratings else 0
            
            if average_rating >= 4.5:
                overall_sentiment = "very_positive"
            elif average_rating >= 4.0:
                overall_sentiment = "positive"
            elif average_rating >= 3.0:
                overall_sentiment = "neutral"
            elif average_rating >= 2.0:
                overall_sentiment = "negative"
            else:
                overall_sentiment = "very_negative"
            
            normalized = {
                "average_rating": round(average_rating, 1),
                "overall_sentiment": overall_sentiment,
                "common_praises": [],
                "common_complaints": [],
                "verified_patterns": {"positive": [], "negative": []},
            }
        except Exception as e:
            logger.warning(f"[Task {self.request.id}] Could not calculate summary: {e}")
            normalized = {
                "average_rating": 0,
                "overall_sentiment": "neutral",
                "common_praises": [],
                "common_complaints": [],
                "verified_patterns": {"positive": [], "negative": []},
            }
        
        # Return final result with all reviews
        result = {
            "success": True,
            "product_name": product_name,
            "source": "google_shopping",
            "summary": {
                "average_rating": normalized.get("average_rating", 0),
                "overall_sentiment": normalized.get("overall_sentiment", "neutral"),
                "common_praises": normalized.get("common_praises", []),
                "common_complaints": normalized.get("common_complaints", []),
                "verified_patterns": normalized.get("verified_patterns", {"positive": [], "negative": []}),
            },
            "reviews": [
                {
                    "reviewer_name": r.get("reviewer_name", "Anonymous"),
                    "rating": r.get("rating", 0),
                    "date": r.get("date", ""),
                    "title": r.get("title", ""),
                    "text": r.get("text", ""),
                    "source": r.get("source", "Google"),
                    "confidence": r.get("validation_confidence", 1.0),
                }
                for r in validated_reviews[:50]
            ],
            "total_found": len(validated_reviews),
            "raw_count": len(raw_reviews),
            "filtered_count": len(raw_reviews) - len(validated_reviews),
        }
        
        logger.info(f"[Task {self.request.id}] ✓ Google reviews task completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"[Task {self.request.id}] Error fetching Google reviews: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=90 * (2 ** self.request.retries))


@celery_app.task(
    name="app.tasks.review_tasks.generate_ai_verdict_task",
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    queue="default",
    time_limit=600,  # 10 minutes
    soft_time_limit=540,  # 9 minutes
)
def generate_ai_verdict_task(
    self,
    product_id: str,
    enriched_data: Dict[str, Any],
    scrape_stores: bool = False
) -> Dict[str, Any]:
    """
    Celery task for generating AI verdict asynchronously.
    
    This task:
    1. Scrapes store insights (if requested)
    2. Calls Gemini AI to generate product verdict
    3. Returns verdict with IMO score, pros/cons, recommendation
    
    Args:
        product_id: Product UUID
        enriched_data: Full enriched product data from SerpAPI/immersive
        scrape_stores: Whether to scrape store pages for insights
        
    Returns:
        Dictionary with verdict data and metadata
    """
    try:
        logger.info(f"[Task {self.request.id}] Starting AI verdict generation for product: {product_id}")
        
        from app.services.ai_service import AIService
        import copy
        
        ai_service = AIService()
        
        # Normalize all review dates to ISO format
        enriched_data = copy.deepcopy(enriched_data)
        if "immersive_data" in enriched_data and isinstance(enriched_data["immersive_data"], dict):
            # Date normalization is already done in the API, but do it again for safety
            pass
        
        # Step 1: Optionally scrape store insights (non-blocking, improves verdict quality)
        store_insights = []
        if scrape_stores:
            try:
                logger.info(f"[Task {self.request.id}] Scraping store insights...")
                stores = enriched_data.get("immersive_data", {}).get("product_results", {}).get("stores", [])
                
                # Run async scraping in thread
                store_insights = run_async_in_thread(
                    ai_service.scrape_store_insights(stores)
                )
                
                logger.info(f"[Task {self.request.id}] ✓ Scraped {len(store_insights)} store insights")
                
                # Update task state with progress
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'status': 'Analyzing store insights...',
                        'stage': 'store_scraping',
                        'progress': 30
                    }
                )
            except Exception as e:
                logger.warning(f"[Task {self.request.id}] Store scraping failed (non-blocking): {e}")
                store_insights = []
        
        # Update progress: about to call Gemini
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Generating AI verdict with Gemini...',
                'stage': 'gemini_generation',
                'progress': 50
            }
        )
        
        # Step 2: Generate verdict using Gemini
        logger.info(f"[Task {self.request.id}] Calling Gemini to generate verdict...")
        
        verdict = run_async_in_thread(
            ai_service.generate_product_verdict(
                product_id=product_id,
                enriched_data=enriched_data,
                store_insights=store_insights
            )
        )
        
        if not verdict:
            raise Exception("Failed to generate verdict from Gemini")
        
        logger.info(f"[Task {self.request.id}] ✓ Verdict generated successfully")
        logger.info(f"[Task {self.request.id}] Verdict: IMO Score {verdict.get('imo_score', 'N/A')}")
        
        # Step 3: Return complete verdict
        result = {
            "success": True,
            "product_id": product_id,
            "verdict": verdict,
            "generated_at": None,  # Frontend can add this if needed
        }
        
        logger.info(f"[Task {self.request.id}] ✓ AI verdict task completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"[Task {self.request.id}] Error generating AI verdict: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
