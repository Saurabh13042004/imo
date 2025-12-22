"""Service for fetching and scraping store reviews."""

import logging
from typing import List, Dict, Any
import asyncio
import json
from app.services.scraper import (
    fetch_html,
    extract_text_blocks,
    extract_rating,
    clean_text,
    get_domain,
    needs_js_rendering,
    deduplicate_reviews,
)

logger = logging.getLogger(__name__)

# Track JS-rendered pages to limit overhead
_js_render_count = 0
_MAX_JS_RENDERS_PER_REQUEST = 2


async def render_with_browser(url: str) -> str | None:
    """
    Render page with headless browser (Selenium/Playwright fallback).
    ONLY used when httpx fetching indicates JS requirement.
    
    Args:
        url: URL to render
    
    Returns:
        Rendered HTML or None
    """
    try:
        # Try Playwright first (faster)
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set timeout and navigate
                await page.goto(url, timeout=30000, wait_until="networkidle")
                
                # Wait for review elements
                try:
                    await page.wait_for_selector(
                        "[class*='review'], [class*='rating'], [class*='comment'], .star, [data-testid*='review']",
                        timeout=5000
                    )
                except:
                    logger.warning(f"No review elements found on {url}")
                
                html = await page.content()
                await browser.close()
                return html
                
        except ImportError:
            # Fallback to Selenium
            from selenium import webdriver
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=options)
            try:
                driver.get(url)
                
                # Wait for review elements
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((
                            By.CSS_SELECTOR,
                            "[class*='review'], [class*='rating'], .star, [data-testid*='review']"
                        ))
                    )
                except:
                    logger.warning(f"No review elements found on {url}")
                
                html = driver.page_source
                return html
            finally:
                driver.quit()
                
    except Exception as e:
        logger.error(f"Browser rendering failed for {url}: {e}")
        return None


class StoreReviewService:
    """Service for scraping and extracting store reviews."""
    
    async def fetch_store_reviews(self, urls: List[str]) -> Dict[str, Any]:
        """
        Fetch reviews from multiple store URLs with smart strategy selection.
        
        Args:
            urls: List of store URLs to scrape
        
        Returns:
            Dict with extracted reviews
        """
        if not urls:
            return {"reviews": [], "total_found": 0}
        
        try:
            # Fetch from all URLs in parallel
            results = await asyncio.gather(
                *[self._scrape_store(url) for url in urls],
                return_exceptions=True
            )
            
            # Flatten results
            all_reviews = []
            for result in results:
                if isinstance(result, list):
                    all_reviews.extend(result)
                elif isinstance(result, Exception):
                    logger.warning(f"Error scraping store: {result}")
            
            # Apply deduplication
            all_reviews = deduplicate_reviews(all_reviews)
            
            return {
                "reviews": all_reviews,
                "total_found": len(all_reviews),
            }
        except Exception as e:
            logger.error(f"Error fetching store reviews: {e}")
            return {"reviews": [], "total_found": 0, "error": str(e)}
    
    async def _scrape_store(self, url: str) -> List[Dict[str, Any]]:
        """
        Scrape reviews from a single store URL with strategy selection.
        
        Args:
            url: Store URL
        
        Returns:
            List of extracted reviews
        """
        try:
            # Step 1: Try initial httpx fetch
            html = await fetch_html(url)
            if not html:
                logger.warning(f"Failed to fetch {url}")
                return []
            
            # Step 2: Check if JS rendering is needed
            global _js_render_count
            if needs_js_rendering(html) and _js_render_count < _MAX_JS_RENDERS_PER_REQUEST:
                logger.info(f"Escalating to JS rendering for {url}")
                _js_render_count += 1
                html = await render_with_browser(url)
                if not html:
                    logger.warning(f"Browser rendering failed for {url}")
                    return []
            
            # Step 3: Extract reviews
            return await self._extract_reviews_from_html(html, url)
            
        except Exception as e:
            logger.warning(f"Error scraping store {url}: {e}")
            return []
    
    async def _extract_reviews_from_html(self, html: str, url: str) -> List[Dict[str, Any]]:
        """
        Extract reviews from HTML with strict filtering.
        
        Args:
            html: HTML content
            url: Source URL
        
        Returns:
            List of extracted reviews
        """
        try:
            store_name = get_domain(url)
            reviews = []
            
            # Extract text blocks (already filters noise and duplicates)
            text_blocks = extract_text_blocks(html, min_length=50)
            
            for text in text_blocks:
                try:
                    cleaned = clean_text(text)
                    if cleaned and len(cleaned) >= 50:  # Enforce minimum length
                        # Try to extract rating
                        rating = extract_rating(text)
                        
                        reviews.append({
                            "store": store_name,
                            "text": cleaned,
                            "rating": rating,
                            "url": url,
                        })
                except Exception as e:
                    logger.debug(f"Error processing text block from {store_name}: {e}")
                    continue
            
            logger.info(f"Extracted {len(reviews)} reviews from {store_name}")
            return reviews
            
        except Exception as e:
            logger.warning(f"Error extracting reviews: {e}")
            return []
