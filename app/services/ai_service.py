"""AI service for review summarization and sentiment analysis using Google Gemini."""

import logging
from typing import List, Optional, Dict, Any
import json

import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered review analysis using Google Gemini."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
        self.initialized = bool(self.api_key)
        self.model = genai.GenerativeModel('gemini-pro') if self.initialized else None

    async def summarize_reviews(
        self,
        reviews: List[str],
        product_name: str
    ) -> Optional[str]:
        """Generate comprehensive review summary using Google Gemini."""
        if not self.initialized:
            logger.warning("Gemini API key not configured")
            return None

        if not reviews:
            return None

        try:
            # Prepare review text
            review_text = "\n\n".join(reviews[:10])  # Limit to 10 reviews

            prompt = f"""Analyze the following customer reviews for "{product_name}" and provide:
1. A concise summary (2-3 sentences)
2. Key pros (3-5 points)
3. Key cons (3-5 points)
4. Overall recommendation

Reviews:
{review_text}

Please format the response as JSON."""

            response = self.model.generate_content(prompt)
            
            summary = response.text
            logger.info(f"Generated review summary for product: {product_name}")
            return summary

        except Exception as e:
            logger.error(f"Error summarizing reviews: {e}")
            return None

    async def analyze_sentiment(self, review_text: str) -> Optional[str]:
        """Determine review sentiment using Gemini."""
        if not self.initialized:
            logger.warning("Gemini API key not configured")
            return None

        try:
            prompt = f"""Analyze the sentiment of this review and respond with only one word: positive, negative, or neutral.

Review: {review_text[:500]}"""

            response = self.model.generate_content(prompt)
            
            sentiment = response.text.strip().lower()

            if sentiment in ["positive", "negative", "neutral"]:
                return sentiment
            return "neutral"

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return None

    async def extract_pros_cons(self, reviews: List[str]) -> Optional[Dict[str, Any]]:
        """Extract key pros and cons from reviews using Gemini."""
        if not self.initialized:
            logger.warning("Gemini API key not configured")
            return None

        if not reviews:
            return None

        try:
            review_text = "\n\n".join(reviews[:10])

            prompt = f"""Extract the main pros and cons from these customer reviews.

Reviews:
{review_text}

Please respond in JSON format with 'pros' and 'cons' as arrays of strings."""

            response = self.model.generate_content(prompt)
            
            content = response.text
            # Try to parse as JSON
            result = json.loads(content)
            logger.info("Extracted pros and cons from reviews")
            return result

        except json.JSONDecodeError:
            logger.error("Failed to parse AI response as JSON")
            return None
        except Exception as e:
            logger.error(f"Error extracting pros and cons: {e}")
            return None

    async def generate_title_summary(self, product_title: str, reviews: List[str]) -> Optional[str]:
        """Generate a concise summary for product title using Gemini."""
        if not self.initialized:
            return None

        if not reviews:
            return None

        try:
            review_text = " ".join(reviews[:5])

            prompt = f"""Summarize the main topic of these reviews in one short sentence (max 10 words).
Product: {product_title}
Reviews: {review_text[:300]}"""

            response = self.model.generate_content(prompt)
            
            summary = response.text.strip()
            return summary

        except Exception as e:
            logger.error(f"Error generating title summary: {e}")
            return None
