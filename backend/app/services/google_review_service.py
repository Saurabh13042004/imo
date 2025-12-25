"""Google Shopping Review Scraper - Selenium Version (Proven Working Pattern)."""

import logging
import time
import threading
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class GoogleReviewService:
    """Service for scraping Google Shopping reviews."""
    
    # CSS Selectors
    REVIEW_CONTAINER = 'div[jsname="Vjrt5"][data-ved]'
    REVIEW_ITEM = 'div[data-attrid="user_review"]'
    MORE_REVIEWS_BTN = 'div[role="button"][jsaction*="trigger.MS0zad"]'
    
    def __init__(self):
        """Initialize service."""
        pass
    
    def fetch_google_reviews(
        self, 
        google_shopping_url: str,
        product_name: str,
        max_clicks: int = 10,
        on_batch_loaded=None  # Callback: called when each batch loads
    ) -> Dict[str, Any]:
        """Fetch reviews using proven Selenium pattern.
        
        Args:
            on_batch_loaded: Optional callback(count, reviews) called when batch loads
        """
        try:
            logger.info("=" * 80)
            logger.info("GOOGLE SHOPPING SCRAPER - SELENIUM (PROVEN PATTERN)")
            logger.info(f"Product: {product_name}")
            logger.info(f"Max iterations: {max_clicks}")
            logger.info("=" * 80)
            
            if not self._is_valid_google_shopping_url(google_shopping_url):
                raise ValueError("Invalid Google Shopping URL")
            
            # Setup Chrome
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            service = Service()
            driver = webdriver.Chrome(service=service, options=options)
            wait = WebDriverWait(driver, 15)
            
            try:
                logger.info(f"Loading {google_shopping_url}")
                driver.get(google_shopping_url)
                logger.info("✓ Page loaded")
                time.sleep(2)
                
                # Load reviews with smart stop (now with callback)
                logger.info("Loading reviews (smart stop)...")
                all_reviews = self._load_reviews_smart(driver, wait, max_clicks, on_batch_loaded)
                
                logger.info("=" * 80)
                logger.info(f"✓ SUCCESS: {len(all_reviews)} reviews extracted")
                logger.info("=" * 80)
                
                return {
                    "success": True,
                    "product_name": product_name,
                    "total_reviews": len(all_reviews),
                    "reviews": all_reviews,
                    "source_url": google_shopping_url
                }
                
            finally:
                driver.quit()
                
        except Exception as e:
            logger.error(f"Scraping error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "reviews": []
            }
    
    def fetch_google_reviews_with_streaming(
        self,
        google_shopping_url: str,
        product_name: str,
        celery_task=None,
        max_clicks: int = 6  # Reduced from 10 for faster loading
    ) -> Dict[str, Any]:
        """Fetch reviews and stream batches directly to Celery task state.
        
        Args:
            celery_task: Celery task instance with update_state() method
        """
        try:
            logger.info("=" * 80)
            logger.info("GOOGLE SHOPPING SCRAPER - SELENIUM WITH DIRECT STREAMING")
            logger.info(f"Product: {product_name}")
            logger.info(f"Celery task: {celery_task}")
            logger.info("=" * 80)
            
            if not self._is_valid_google_shopping_url(google_shopping_url):
                raise ValueError("Invalid Google Shopping URL")
            
            # Setup Chrome
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            service = Service()
            driver = webdriver.Chrome(service=service, options=options)
            wait = WebDriverWait(driver, 15)
            
            try:
                logger.info(f"Loading {google_shopping_url}")
                driver.get(google_shopping_url)
                logger.info("✓ Page loaded")
                time.sleep(2)
                
                # Load reviews with direct streaming
                logger.info("Loading reviews (smart stop with streaming)...")
                all_reviews = self._load_reviews_smart_with_streaming(
                    driver, wait, max_clicks, celery_task
                )
                
                logger.info("=" * 80)
                logger.info(f"✓ SUCCESS: {len(all_reviews)} reviews extracted")
                logger.info("=" * 80)
                
                return {
                    "success": True,
                    "product_name": product_name,
                    "total_reviews": len(all_reviews),
                    "reviews": all_reviews,
                    "source_url": google_shopping_url
                }
                
            finally:
                driver.quit()
                
        except Exception as e:
            logger.error(f"Scraping error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "reviews": []
            }
    
    def _load_reviews_smart(self, driver, wait, max_rounds: int, on_batch_loaded=None) -> List[Dict[str, Any]]:
        """Load reviews with smart stop when count stabilizes - optimized timing.
        
        Args:
            on_batch_loaded: Callback(count, reviews) called after each batch loads
        """
        
        last_count = 0
        stable_rounds = 0
        logger.info(f"[_load_reviews_smart] Starting with callback: {on_batch_loaded is not None}")
        
        for i in range(max_rounds):
            # Expand all reviews ASYNC (don't wait for all to complete)
            self._expand_all_reviews_fast(driver)
            time.sleep(0.5)  # Reduced from 1s
            
            # Get current reviews
            reviews_raw = driver.find_elements(By.CSS_SELECTOR, 'div[data-attrid="user_review"]')
            count = len(reviews_raw)
            logger.info(f"  [{i+1}] Reviews loaded: {count}")
            
            # Parse reviews loaded so far and send via callback
            if count > last_count:
                logger.info(f"  [{i+1}] Count increased: {last_count} -> {count}, calling callback: {on_batch_loaded is not None}")
                if on_batch_loaded:
                    try:
                        current_reviews = self._parse_reviews(driver)
                        logger.info(f"  [{i+1}] Parsed {len(current_reviews)} reviews, invoking callback...")
                        on_batch_loaded(count, current_reviews)
                        logger.info(f"  [{i+1}] → Streamed {len(current_reviews)} reviews to UI")
                    except Exception as e:
                        logger.warning(f"  [{i+1}] → Callback error: {e}", exc_info=True)
                else:
                    logger.info(f"  [{i+1}] No callback provided, skipping")
            
            # Check if stabilized
            if count == last_count:
                stable_rounds += 1
            else:
                stable_rounds = 0
            
            if stable_rounds >= 2:
                logger.info("  ✓ Review count stabilized — stopping")
                break
            
            last_count = count
            
            # Try to load more
            if not self._click_more_reviews_fast(driver, wait):
                logger.info("  ✗ No more reviews button — stopping")
                break
            
            time.sleep(0.8)  # Reduced from 1.5s
        
        # Extract and parse all reviews (final return)
        return self._parse_reviews(driver)
    
    def _load_reviews_smart_with_streaming(self, driver, wait, max_rounds: int, celery_task=None) -> List[Dict[str, Any]]:
        """Load reviews with smart stop and direct streaming to Celery task state.
        
        Args:
            celery_task: Celery task instance with update_state() method
        """
        
        last_count = 0
        stable_rounds = 0
        batch_counter = 0
        
        logger.info(f"[_load_reviews_smart_with_streaming] Starting - celery_task: {celery_task is not None}")
        
        for i in range(max_rounds):
            # Expand all reviews ASYNC (don't wait for all to complete)
            self._expand_all_reviews_fast(driver)
            time.sleep(0.2)  # Reduced from 0.5s
            
            # Get current reviews
            reviews_raw = driver.find_elements(By.CSS_SELECTOR, 'div[data-attrid="user_review"]')
            count = len(reviews_raw)
            logger.info(f"  [{i+1}] Reviews loaded: {count}")
            
            # Stream batch if count increased
            if count > last_count and celery_task:
                batch_counter += 1
                try:
                    current_reviews = self._parse_reviews(driver)
                    logger.info(f"  [{i+1}] 🔄 Batch {batch_counter}: {len(current_reviews)} reviews parsed")
                    
                    # Format for UI
                    formatted = [
                        {
                            "reviewer_name": r.get("reviewer_name", "Anonymous"),
                            "rating": r.get("rating", 0),
                            "date": r.get("date", ""),
                            "title": r.get("title", ""),
                            "text": r.get("text", ""),
                            "source": r.get("source", "Google"),
                            "confidence": r.get("validation_confidence", 1.0),
                        }
                        for r in current_reviews
                    ]
                    
                    # Send PROGRESS update to task
                    celery_task.update_state(
                        state='PROGRESS',
                        meta={
                            'current': len(formatted),
                            'total': count,
                            'batch': batch_counter,
                            'status': f'Batch {batch_counter}: {count} reviews scraped',
                            'reviews': formatted,
                        }
                    )
                    logger.info(f"  [{i+1}] ✓ Batch {batch_counter} sent to frontend ({len(formatted)} reviews)")
                except Exception as e:
                    logger.warning(f"  [{i+1}] Streaming error: {e}", exc_info=True)
            
            # Check if stabilized
            if count == last_count:
                stable_rounds += 1
            else:
                stable_rounds = 0
            
            if stable_rounds >= 2:
                logger.info("  ✓ Review count stabilized — stopping")
                break
            
            last_count = count
            
            # Try to load more
            if not self._click_more_reviews_fast(driver, wait):
                logger.info("  ✗ No more reviews button — stopping")
                break
            
            time.sleep(0.4)  # Reduced from 0.8s
        
        # Extract and parse all reviews (final return)
        return self._parse_reviews(driver)
    
    def _expand_all_reviews_fast(self, driver):
        """Click all 'Read more' buttons PARALLEL - optimized version."""
        try:
            buttons = driver.find_elements(
                By.CSS_SELECTOR,
                'div[jsaction*="trigger.nNRzZb"]'
            )
            
            if not buttons:
                return
            
            # Use ThreadPoolExecutor for parallel clicking
            with ThreadPoolExecutor(max_workers=5) as executor:
                def click_button(button):
                    try:
                        driver.execute_script("arguments[0].click();", button)
                        return True
                    except:
                        return False
                
                # Submit all clicks to thread pool
                futures = [executor.submit(click_button, b) for b in buttons]
                # Wait for all to complete with timeout
                for future in as_completed(futures, timeout=5):
                    try:
                        future.result()
                    except:
                        pass
        except:
            pass

    def _expand_all_reviews(self, driver):
        """Click all 'Read more' buttons to expand review text."""
        try:
            buttons = driver.find_elements(
                By.CSS_SELECTOR,
                'div[jsaction*="trigger.nNRzZb"]'
            )
            for b in buttons:
                try:
                    driver.execute_script("arguments[0].click();", b)
                except:
                    pass
        except:
            pass
    
    def _click_more_reviews(self, driver, wait) -> bool:
        """Click 'More reviews' button using standard click."""
        try:
            btn = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div[role="button"][jsaction*="trigger.MS0zad"]')
            ))
            driver.execute_script("arguments[0].click();", btn)
            return True
        except:
            return False

    def _click_more_reviews_fast(self, driver, wait) -> bool:
        """Click 'More reviews' button with reduced timeout - fast version."""
        try:
            # Use short timeout (3s instead of 10s)
            short_wait = WebDriverWait(driver, 3)
            btn = short_wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div[role="button"][jsaction*="trigger.MS0zad"]')
            ))
            driver.execute_script("arguments[0].click();", btn)
            return True
        except:
            return False
    
    def _parse_reviews(self, driver) -> List[Dict[str, Any]]:
        """Parse all reviews from DOM - optimized with parallel extraction."""
        try:
            review_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-attrid="user_review"]')
            
            # Extract all review data first (fast)
            review_data = []
            for r in review_elements:
                try:
                    name = r.find_element(By.CSS_SELECTOR, ".cbsD0d").text
                    rating_text = r.find_element(By.CSS_SELECTOR, ".yi40Hd").text
                    review_text = r.find_element(By.CSS_SELECTOR, ".v168Le").text
                    
                    # Extract source - "Reviewed on ebay.com" or similar
                    source = "Google Shopping"
                    try:
                        source_elem = r.find_element(By.CSS_SELECTOR, ".xuBzLd")
                        source_text = source_elem.text.strip()
                        # Parse "Reviewed on ebay.com" -> "ebay.com"
                        if "Reviewed on" in source_text:
                            source = source_text.replace("Reviewed on ", "").strip()
                    except:
                        pass
                    
                    review_data.append((name, rating_text, review_text, source))
                except:
                    pass
            
            # Process reviews in parallel
            results = []
            with ThreadPoolExecutor(max_workers=8) as executor:
                def process_review(data):
                    name, rating_text, review_text, source = data
                    
                    # Parse rating
                    rating = 0
                    if rating_text:
                        import re
                        match = re.search(r'\d', rating_text)
                        if match:
                            rating = int(match.group())
                    
                    # Only return if valid
                    if review_text and len(review_text) > 10 and rating > 0:
                        return {
                            "reviewer_name": name or "Anonymous",
                            "rating": rating,
                            "title": "",
                            "text": review_text,
                            "review_date": "",
                            "source": source
                        }
                    return None
                
                # Submit all to thread pool
                futures = [executor.submit(process_review, data) for data in review_data]
                
                # Collect results
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result:
                            results.append(result)
                    except:
                        pass
            
            logger.info(f"  Parsed {len(results)} reviews")
            return results
            
        except Exception as e:
            logger.warning(f"Error parsing reviews: {e}")
            return []
    
    def _is_valid_google_shopping_url(self, url: str) -> bool:
        """Validate that URL is a Google Shopping URL."""
        try:
            parsed = urlparse(url)
            
            # Check domain
            if 'google' not in parsed.netloc:
                return False
            
            # Check for shopping parameters
            params = parse_qs(parsed.query)
            has_shopping = 'ibp' in params or 'prds' in params or 'udm' in params
            
            return has_shopping
        except:
            return False

