"""AI service for product verdict generation using Google Gemini."""

import logging
from typing import List, Optional, Dict, Any
import json
import asyncio

import google.generativeai as genai
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered product verdict generation using Google Gemini."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
        self.initialized = bool(self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash') if self.initialized else None

    def _parse_gemini_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse Gemini response and extract JSON."""
        try:
            # Clean up response - remove markdown code blocks if present
            text = response_text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            # Parse JSON
            analysis = json.loads(text)
            
            # Validate required fields
            required_fields = ["summary", "pros", "cons", "imo_score"]
            for field in required_fields:
                if field not in analysis:
                    logger.warning(f"Gemini response missing field: {field}")
            
            logger.info("Successfully parsed Gemini product verdict")
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            logger.debug(f"Raw response: {response_text[:200]}")
            return None
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}", exc_info=True)
            return None

    async def scrape_store_insights(self, stores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scrape store pages for pricing, availability, warranty, and credibility signals.
        Best-effort, non-blocking operation.
        
        Args:
            stores: List of store dicts from SerpAPI with 'link' key
            
        Returns:
            List of scraped store insights
        """
        insights = []
        
        if not stores:
            return insights
        
        logger.info(f"[Store Scraping] Starting scrape of {len(stores)} stores")
        
        # Scrape stores in parallel with timeout
        tasks = []
        for store in stores[:5]:  # Limit to first 5 stores to avoid rate limiting
            if isinstance(store, dict) and store.get("link"):
                tasks.append(self._scrape_single_store(store))
        
        if not tasks:
            return insights
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, dict):
                    insights.append(result)
                elif isinstance(result, Exception):
                    logger.warning(f"[Store Scraping] Error scraping store: {result}")
        except Exception as e:
            logger.error(f"[Store Scraping] Error during parallel scraping: {e}")
        
        logger.info(f"[Store Scraping] Successfully scraped {len(insights)} stores")
        return insights

    async def _scrape_single_store(self, store: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Scrape a single store page for insights.
        
        Args:
            store: Store dict with 'name', 'link', optional 'price'
            
        Returns:
            Dict with store insights or None
        """
        try:
            store_name = store.get("name", "Unknown Store")
            store_link = store.get("link")
            original_price = store.get("price") or store.get("extracted_price")
            
            if not store_link:
                return None
            
            logger.debug(f"[Store Scraping] Scraping: {store_name} ({store_link[:50]}...)")
            
            # Fetch page with short timeout
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(store_link, follow_redirects=True)
                response.raise_for_status()
                html = response.text[:10000]  # Limit to first 10KB
            
            # Extract insights from HTML (simple pattern matching)
            insights = {
                "store_name": store_name,
                "store_link": store_link,
                "price": original_price,
                "availability_status": self._extract_availability(html),
                "has_warranty": "warranty" in html.lower() or "guarantee" in html.lower(),
                "has_free_shipping": "free shipping" in html.lower() or "free delivery" in html.lower(),
                "has_return_policy": "return" in html.lower() or "exchange" in html.lower(),
                "has_reviews": "review" in html.lower() or "rating" in html.lower(),
            }
            
            logger.debug(f"[Store Scraping] Scraped {store_name}: {insights}")
            return insights
            
        except asyncio.TimeoutError:
            logger.debug(f"[Store Scraping] Timeout scraping store: {store.get('name', 'Unknown')}")
            return None
        except Exception as e:
            logger.debug(f"[Store Scraping] Error scraping store: {e}")
            return None

    def _extract_availability(self, html: str) -> str:
        """Extract availability status from HTML."""
        html_lower = html.lower()
        
        if "in stock" in html_lower or "in-stock" in html_lower:
            return "In Stock"
        elif "out of stock" in html_lower or "out-of-stock" in html_lower:
            return "Out of Stock"
        elif "limited" in html_lower:
            return "Limited Availability"
        elif "coming soon" in html_lower:
            return "Coming Soon"
        else:
            return "Availability Unknown"

    async def generate_product_verdict(
        self,
        product_id: str,
        enriched_data: Dict[str, Any],
        store_insights: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate AI verdict using ONLY the enriched_data provided.
        
        CRITICAL: This method does NOT refetch product data.
        It uses the enriched_data passed as parameter - the single source of truth.
        
        Args:
            product_id: UUID of the product
            enriched_data: Full enriched product data from /product/enriched endpoint
            store_insights: Optional scraped store insights
            
        Returns:
            Dict with verdict data or None on failure
        """
        if not self.initialized:
            logger.warning("[AI Verdict] Gemini API key not configured")
            return None
        
        try:
            # Extract product info from enriched data
            # Handle both immersive product format and Amazon format
            immersive_data = enriched_data.get("immersive_data", {})
            product_results = immersive_data.get("product_results", {})
            
            title = enriched_data.get("title", product_results.get("title", "Unknown Product"))
            description = enriched_data.get("description", "")
            category = enriched_data.get("category", "")
            price = enriched_data.get("price", 0)
            rating = enriched_data.get("rating", 0)
            total_reviews = enriched_data.get("total_reviews", 0)
            
            logger.info(f"[AI Verdict] Generating verdict for: {title}")
            
            # Extract reviews from enriched data
            user_reviews = product_results.get("user_reviews", [])[:10]
            amazon_reviews = enriched_data.get("amazon_reviews", [])[:10]
            external_reviews = enriched_data.get("external_reviews", [])[:5]
            
            all_reviews = user_reviews + amazon_reviews + external_reviews
            
            # Build reviews text
            reviews_text = ""
            for review in all_reviews[:10]:
                if isinstance(review, dict):
                    rating_val = review.get("rating", 5)
                    content = (
                        review.get("text") or 
                        review.get("content") or 
                        review.get("review_text") or 
                        review.get("snippet", "")
                    )
                    if content:
                        reviews_text += f"[{rating_val}★] {content[:300]}\n"
            
            # Build stores text with scraped insights
            stores_text = ""
            if store_insights:
                for insight in store_insights:
                    stores_text += f"- {insight['store_name']}: ${insight.get('price', 'N/A')} | "
                    stores_text += f"Stock: {insight['availability_status']} | "
                    stores_text += f"Warranty: {'Yes' if insight['has_warranty'] else 'No'} | "
                    stores_text += f"Free Shipping: {'Yes' if insight['has_free_shipping'] else 'No'}\n"
            else:
                # Use store info from enriched data if no scraping done
                stores = product_results.get("stores", [])
                for store in stores[:5]:
                    store_name = store.get("name", "Store")
                    store_price = store.get("extracted_price") or store.get("price", "N/A")
                    stores_text += f"- {store_name}: ${store_price}\n"
            
            # Build the Gemini prompt with strict JSON structure
            prompt = f"""You are an expert product analyst. Generate a verdict for this product based on the data provided.

PRODUCT INFORMATION:
Title: {title}
Category: {category}
Current Price: ${price}
Rating: {rating}/5.0 ({total_reviews} reviews)
Description: {description[:300]}

CUSTOMER REVIEWS:
{reviews_text if reviews_text else "No reviews available"}

STORE OFFERS:
{stores_text if stores_text else "No store offers available"}

ANALYSIS TASK:
Analyze all information above and provide a verdict in STRICT JSON format ONLY.

Do NOT include any markdown, code blocks, or explanations - ONLY valid JSON.

Requirements:
1. imo_score: 0-10 scale (0=worst, 10=best) based on reviews, pricing, and availability
2. summary: 1-2 sentences summarizing product quality and value
3. pros: Top 5 pros from reviews and specs (string array)
4. cons: Top 5 cons from reviews (string array)
5. who_should_buy: Target customer profile (string)
6. who_should_avoid: Customer types that might be disappointed (string)
7. price_fairness: Assessment of current price vs market (string)
8. deal_breakers: Major issues that disqualify the product (string array)

STRICT RULES:
- ALWAYS respond with ONLY valid JSON
- imo_score MUST be a number 0-10
- All other fields must be strings or string arrays
- Be honest about both strengths and weaknesses
- Base verdict on ACTUAL review feedback and pricing data provided
- If reviews are limited, use specs and price to inform verdict

RETURN ONLY THIS JSON (no markdown, no explanation):
{{
    "imo_score": 7.5,
    "summary": "High quality product with good value...",
    "pros": ["pro1", "pro2", "pro3", "pro4", "pro5"],
    "cons": ["con1", "con2", "con3", "con4", "con5"],
    "who_should_buy": "...",
    "who_should_avoid": "...",
    "price_fairness": "...",
    "deal_breakers": ["issue1"]
}}"""
            
            logger.info(f"[AI Verdict] Calling Gemini for {title}")
            response = self.model.generate_content(prompt)
            
            # Parse response
            analysis = self._parse_gemini_response(response.text)
            
            if not analysis:
                logger.error(f"[AI Verdict] Failed to parse Gemini response for {title}")
                return None
            
            # Build verdict with validation
            verdict = {
                "product_id": product_id,
                "imo_score": float(analysis.get("imo_score", 5.0)),
                "summary": str(analysis.get("summary", "")),
                "pros": analysis.get("pros", []),
                "cons": analysis.get("cons", []),
                "who_should_buy": str(analysis.get("who_should_buy", "")),
                "who_should_avoid": str(analysis.get("who_should_avoid", "")),
                "price_fairness": str(analysis.get("price_fairness", "")),
                "deal_breakers": analysis.get("deal_breakers", []),
            }
            
            # Validate IMO score
            if verdict["imo_score"] < 0:
                verdict["imo_score"] = 0.0
            elif verdict["imo_score"] > 10:
                verdict["imo_score"] = 10.0
            
            logger.info(f"[AI Verdict] Generated verdict for {title}: IMO Score {verdict['imo_score']}")
            return verdict
            
        except Exception as e:
            logger.error(f"[AI Verdict] Error generating verdict: {e}", exc_info=True)
            return None

