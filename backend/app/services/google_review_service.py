"""Google Shopping Review Scraper - Selenium Version (Proven Working Pattern)."""

import logging
import time
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

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
        max_clicks: int = 5
    ) -> Dict[str, Any]:
        """Fetch reviews using proven Selenium pattern."""
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
                
                # Load reviews with smart stop
                logger.info("Loading reviews (smart stop)...")
                all_reviews = self._load_reviews_smart(driver, wait, max_clicks)
                
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
    
    def _load_reviews_smart(self, driver, wait, max_rounds: int) -> List[Dict[str, Any]]:
        """Load reviews with smart stop when count stabilizes."""
        
        last_count = 0
        stable_rounds = 0
        
        for i in range(max_rounds):
            # Expand all reviews first
            self._expand_all_reviews(driver)
            time.sleep(1)
            
            # Get current count
            reviews = driver.find_elements(By.CSS_SELECTOR, 'div[data-attrid="user_review"]')
            count = len(reviews)
            logger.info(f"  [{i+1}] Reviews loaded: {count}")
            
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
            if not self._click_more_reviews(driver, wait):
                logger.info("  ✗ No more reviews button — stopping")
                break
            
            time.sleep(1.5)
        
        # Extract and parse all reviews
        return self._parse_reviews(driver)
    
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
    
    def _parse_reviews(self, driver) -> List[Dict[str, Any]]:
        """Parse all reviews from DOM."""
        results = []
        
        try:
            review_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-attrid="user_review"]')
            
            for r in review_elements:
                def safe(css):
                    try:
                        return r.find_element(By.CSS_SELECTOR, css).text
                    except:
                        return ""
                
                name = safe(".cbsD0d")
                rating_text = safe(".yi40Hd")
                review_text = safe(".v168Le")
                
                # Parse rating (e.g., "5" from "Rated 5 out of 5")
                rating = 0
                if rating_text:
                    import re
                    match = re.search(r'\d', rating_text)
                    if match:
                        rating = int(match.group())
                
                # Only add if we have text and rating
                if review_text and len(review_text) > 10 and rating > 0:
                    results.append({
                        "reviewer_name": name or "Anonymous",
                        "rating": rating,
                        "title": "",  # Google Shopping doesn't have separate titles
                        "text": review_text,
                        "review_date": "",
                        "source": "Google Shopping"
                    })
            
            logger.info(f"  Parsed {len(results)} reviews")
            
        except Exception as e:
            logger.warning(f"Error parsing reviews: {e}")
        
        return results
    
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

