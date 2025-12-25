"""AI service for normalizing and analyzing extracted reviews."""

import logging
from typing import List, Dict, Any
import json
import re

import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)


class AIReviewService:
    """Service for AI-powered review normalization and analysis using Google Gemini."""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
        self.initialized = bool(self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash') if self.initialized else None
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from Gemini response, handling markdown code blocks.
        
        Args:
            response_text: Raw response from Gemini
        
        Returns:
            Parsed JSON dict
        """
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
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            raise ValueError("Could not parse JSON from response")
    
    async def validate_and_normalize_reviews(self, raw_reviews: List[Dict[str, Any]], context: str = "product") -> Dict[str, Any]:
        """
        Validate that reviews are actual reviews (not questions, specs, nav text, etc.)
        and normalize them.
        
        Args:
            raw_reviews: List of raw extracted reviews
            context: Context (e.g., "product", "store")
        
        Returns:
            Validated and normalized reviews
        """
        if not self.initialized:
            logger.warning("[AIReviewService] Gemini API key not configured")
            return {"reviews": raw_reviews, "valid_count": len(raw_reviews), "filtered_count": 0}
        
        if not raw_reviews:
            return {"reviews": [], "valid_count": 0, "filtered_count": 0}
        
        try:
            # Batch validate reviews
            review_texts = [r.get('text', '')[:300] for r in raw_reviews[:20]]  # First 20, truncated
            reviews_str = "\n\n---\n\n".join([f"{i+1}. {t}" for i, t in enumerate(review_texts)])
            
            prompt = f"""Analyze these potential reviews and for EACH ONE:
1. Is it a REAL review? (not a question, navigation text, spec sheet, etc.)
2. Does it contain opinion/experience?
3. Confidence score (0-1)

Context: {context}

Reviews to analyze:
{reviews_str}

For each review, respond with ONLY a JSON array like:
[
  {{"index": 1, "is_review": true, "has_opinion": true, "confidence": 0.95}},
  {{"index": 2, "is_review": false, "has_opinion": false, "confidence": 0.1}},
  ...
]

NO other text. Just the JSON array."""
            
            logger.info("[AIReviewService] Validating reviews with AI")
            response = self.model.generate_content(prompt)
            validation_results = self._parse_json_response(response.text)
            
            # Filter based on validation
            valid_reviews = []
            filtered_count = 0
            
            for i, review in enumerate(raw_reviews[:20]):
                # Find matching validation result
                matching_val = next((v for v in validation_results if v.get('index') == i + 1), None)
                
                if matching_val and matching_val.get('is_review') and matching_val.get('confidence', 0) >= 0.5:
                    review['validation_confidence'] = matching_val.get('confidence', 0)
                    valid_reviews.append(review)
                else:
                    filtered_count += 1
                    logger.debug(f"Filtered review: {review.get('text', '')[:50]}...")
            
            logger.info(f"[AIReviewService] Validated {len(valid_reviews)} reviews, filtered {filtered_count}")
            
            return {
                "reviews": valid_reviews,
                "valid_count": len(valid_reviews),
                "filtered_count": filtered_count,
            }
            
        except Exception as e:
            logger.error(f"[AIReviewService] Error validating reviews: {e}")
            return {"reviews": raw_reviews, "valid_count": len(raw_reviews), "filtered_count": 0, "error": str(e)}
    
    async def normalize_community_reviews(self, raw_reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Normalize community reviews using AI.
        
        Args:
            raw_reviews: List of raw extracted reviews
        
        Returns:
            Normalized review data
        """
        if not self.initialized:
            logger.warning("[AIReviewService] Gemini API key not configured")
            return {
                "overall_sentiment": "neutral",
                "common_praises": [],
                "common_complaints": [],
            }
        
        if not raw_reviews:
            return {
                "overall_sentiment": "neutral",
                "common_praises": [],
                "common_complaints": [],
            }
        
        try:
            # Prepare text for AI analysis
            reviews_text = "\n\n".join([
                f"Source: {r.get('source', 'unknown')}\nText: {r.get('text', '')}"
                for r in raw_reviews[:20]  # Limit to first 20
            ])
            
            prompt = f"""Analyze these product reviews and provide:
1. Overall sentiment (positive/mixed/negative)
2. Common praises (list of 3-5 main positive points)
3. Common complaints (list of 3-5 main negative points)

Reviews to analyze:
{reviews_text}

Respond in STRICT JSON format ONLY (no markdown, no explanation):
{{
    "overall_sentiment": "positive",
    "common_praises": ["praise1", "praise2", "praise3"],
    "common_complaints": ["complaint1", "complaint2", "complaint3"]
}}"""
            
            logger.info("[AIReviewService] Calling Gemini to normalize community reviews")
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            logger.info(f"[AIReviewService] Successfully normalized {len(raw_reviews)} community reviews")
            return result
            
        except Exception as e:
            logger.error(f"[AIReviewService] Error normalizing community reviews: {e}")
            return {
                "overall_sentiment": "neutral",
                "common_praises": [],
                "common_complaints": [],
                "error": str(e),
            }
    
    async def normalize_store_reviews(self, raw_reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Normalize store reviews using AI.
        
        Args:
            raw_reviews: List of raw extracted reviews
        
        Returns:
            Normalized review data
        """
        if not self.initialized:
            logger.warning("[AIReviewService] Gemini API key not configured")
            return {
                "average_rating": 0,
                "trust_score": 0,
                "verified_patterns": {"positive": [], "negative": []},
            }
        
        if not raw_reviews:
            return {
                "average_rating": 0,
                "trust_score": 0,
                "verified_patterns": {"positive": [], "negative": []},
            }
        
        try:
            # Prepare text for AI analysis
            reviews_text = "\n\n".join([
                f"Store: {r.get('store', 'unknown')}\nRating: {r.get('rating', 'N/A')}\nText: {r.get('text', '')}"
                for r in raw_reviews[:25]  # Limit to first 25
            ])
            
            prompt = f"""Analyze these store product reviews and provide:
1. Average rating (1-5) normalized from the reviews
2. Trust score (0-1) - how trustworthy are these reviews (0=not trustworthy, 1=very trustworthy)
3. Verified positive patterns (common legitimate pros mentioned)
4. Verified negative patterns (common legitimate cons mentioned)

Reviews to analyze:
{reviews_text}

Respond in STRICT JSON format ONLY (no markdown, no explanation):
{{
    "average_rating": 4.2,
    "trust_score": 0.85,
    "verified_patterns": {{
        "positive": ["pattern1", "pattern2", "pattern3"],
        "negative": ["pattern1", "pattern2"]
    }}
}}"""
            
            logger.info("[AIReviewService] Calling Gemini to normalize store reviews")
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            logger.info(f"[AIReviewService] Successfully normalized {len(raw_reviews)} store reviews")
            return result
            
        except Exception as e:
            logger.error(f"[AIReviewService] Error normalizing store reviews: {e}")
    async def normalize_google_reviews(self, raw_reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Normalize Google Shopping reviews using AI.
        
        Args:
            raw_reviews: List of raw extracted reviews from Google Shopping
        
        Returns:
            Normalized review data with patterns and sentiment
        """
        if not self.initialized:
            logger.warning("[AIReviewService] Gemini API key not configured")
            return {
                "average_rating": 0,
                "overall_sentiment": "neutral",
                "common_praises": [],
                "common_complaints": [],
                "verified_patterns": {"positive": [], "negative": []},
            }
        
        if not raw_reviews:
            return {
                "average_rating": 0,
                "overall_sentiment": "neutral",
                "common_praises": [],
                "common_complaints": [],
                "verified_patterns": {"positive": [], "negative": []},
            }
        
        try:
            # Calculate average rating
            ratings = [r.get('rating', 0) for r in raw_reviews if r.get('rating')]
            average_rating = sum(ratings) / len(ratings) if ratings else 0
            
            # Prepare text for AI analysis
            reviews_text = "\n\n".join([
                f"Rating: {r.get('rating', 'N/A')}\nTitle: {r.get('title', '')}\nText: {r.get('text', '')}"
                for r in raw_reviews[:30]  # Limit to first 30
            ])
            
            prompt = f"""Analyze these Google Shopping product reviews and provide:
1. Overall sentiment (positive/mixed/negative)
2. Common praises (list of 3-5 main positive points)
3. Common complaints (list of 3-5 main negative points)
4. Verified positive patterns (recurring benefits)
5. Verified negative patterns (recurring issues)

Reviews to analyze:
{reviews_text}

Respond in STRICT JSON format ONLY (no markdown, no explanation):
{{
    "overall_sentiment": "positive",
    "common_praises": ["praise1", "praise2", "praise3"],
    "common_complaints": ["complaint1", "complaint2"],
    "verified_patterns": {{
        "positive": ["pattern1", "pattern2"],
        "negative": ["pattern1", "pattern2"]
    }}
}}"""
            
            logger.info("[AIReviewService] Calling Gemini to normalize Google reviews")
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            # Add calculated average rating
            result['average_rating'] = round(average_rating, 2)
            
            logger.info(f"[AIReviewService] Successfully normalized {len(raw_reviews)} Google reviews")
            return result
            
        except Exception as e:
            logger.error(f"[AIReviewService] Error normalizing Google reviews: {e}")
            return {
                "average_rating": 0,
                "overall_sentiment": "neutral",
                "common_praises": [],
                "common_complaints": [],
                "verified_patterns": {"positive": [], "negative": []},
                "error": str(e),
            }

    async def format_community_reviews(self, raw_reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format community/forum reviews into structured review format with rating and 1-2 line summary.
        
        Args:
            raw_reviews: List of raw extracted reviews
        
        Returns:
            List of formatted reviews with structure: {rating, title, text, source, reviewer_name}
        """
        if not self.initialized:
            logger.warning("[AIReviewService] Gemini API key not configured")
            # Return raw reviews in best effort format
            return {
                "formatted_reviews": [
                    {
                        "rating": 3,
                        "title": r.get("text", "")[:50],
                        "text": r.get("text", ""),
                        "source": r.get("source", "community"),
                        "reviewer_name": "Community User",
                        "confidence": r.get("validation_confidence", 0.5),
                    }
                    for r in raw_reviews[:20]
                ],
                "total_formatted": len(raw_reviews),
                "fallback": True
            }
        
        if not raw_reviews:
            return {"formatted_reviews": [], "total_formatted": 0}
        
        try:
            # Process reviews in batches of 10 for better accuracy
            formatted_reviews = []
            batch_size = 10
            
            for batch_start in range(0, min(len(raw_reviews), 50), batch_size):
                batch_end = min(batch_start + batch_size, len(raw_reviews), len(raw_reviews))
                batch = raw_reviews[batch_start:batch_end]
                
                # Create prompt for formatting
                reviews_text = "\n\n---\n\n".join([
                    f"Review {i+1}:\n{r.get('text', '')[:400]}"
                    for i, r in enumerate(batch)
                ])
                
                prompt = f"""For each forum/community review below, extract:
1. A sentiment-based rating (1-5 scale)
2. A title (max 8 words)
3. A 1-2 line summary of the main point

Reviews:
{reviews_text}

Respond with ONLY a JSON array, matching review order:
[
  {{"rating": 4, "title": "Great product, highly recommend", "summary": "Works as expected. Excellent quality and fast shipping."}},
  {{"rating": 2, "title": "Disappointing, broke after a week", "summary": "Product stopped working after minimal use. Poor durability."}},
  ...
]

Rules:
- Rating: 5=very positive, 4=positive, 3=neutral, 2=negative, 1=very negative
- Title: Extract key sentiment/opinion in max 8 words
- Summary: Concise 1-2 lines capturing the essence
- NO other text. Just the JSON array."""
                
                logger.info(f"[AIReviewService] Formatting community reviews batch ({batch_start+1}-{batch_end})")
                response = self.model.generate_content(prompt)
                batch_formatted = self._parse_json_response(response.text)
                
                # Validate and enhance response
                if isinstance(batch_formatted, list):
                    for i, formatted in enumerate(batch_formatted):
                        if i < len(batch):
                            original = batch[i]
                            formatted_reviews.append({
                                "rating": formatted.get("rating", 3),
                                "title": formatted.get("title", original.get("text", "")[:50]),
                                "text": formatted.get("summary", original.get("text", "")),
                                "source": original.get("source", "community"),
                                "reviewer_name": original.get("reviewer_name", "Community User"),
                                "confidence": original.get("validation_confidence", 0.7),
                                "original_text": original.get("text", ""),  # Keep for reference
                            })
            
            logger.info(f"[AIReviewService] Successfully formatted {len(formatted_reviews)} community reviews")
            return {
                "formatted_reviews": formatted_reviews,
                "total_formatted": len(formatted_reviews),
                "raw_count": len(raw_reviews)
            }
            
        except Exception as e:
            logger.error(f"[AIReviewService] Error formatting community reviews: {e}")
            # Return best effort formatting
            return {
                "formatted_reviews": [
                    {
                        "rating": 3,
                        "title": r.get("text", "")[:50],
                        "text": r.get("text", "")[:200],
                        "source": r.get("source", "community"),
                        "reviewer_name": "Community User",
                        "confidence": r.get("validation_confidence", 0.5),
                    }
                    for r in raw_reviews[:20]
                ],
                "total_formatted": len(raw_reviews),
                "error": str(e)
            }

    async def summarize_reviews(self, raw_reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Summarize reviews to 1-2 lines with rating for each.
        
        Args:
            raw_reviews: List of raw extracted reviews
        
        Returns:
            List of summarized reviews with 1-2 line summaries and ratings
        """
        if not self.initialized:
            logger.warning("[AIReviewService] Gemini API key not configured")
            return {"reviews": raw_reviews, "summaries": []}
        
        if not raw_reviews:
            return {"reviews": [], "summaries": []}
        
        try:
            # Prepare reviews for summarization (batch process max 15)
            reviews_to_summarize = raw_reviews[:15]
            
            # Create prompt for batch summarization
            reviews_text = "\n\n---\n\n".join([
                f"Review {i+1} (Rating: {r.get('rating', 'N/A')}):\n{r.get('text', '')[:500]}"
                for i, r in enumerate(reviews_to_summarize)
            ])
            
            prompt = f"""Summarize each review to 1-2 lines capturing the main point and sentiment.

Reviews:
{reviews_text}

Respond with ONLY a JSON array, one summary per review in the same order:
[
  {{"rating": 5, "summary": "Excellent product, works perfectly and lasts long."}},
  {{"rating": 4, "summary": "Great quality but slightly expensive for the features."}},
  ...
]

NO other text. Just the JSON array."""
            
            logger.info(f"[AIReviewService] Summarizing {len(reviews_to_summarize)} reviews with AI")
            response = self.model.generate_content(prompt)
            summaries = self._parse_json_response(response.text)
            
            # Ensure summaries are in correct format
            if isinstance(summaries, list):
                logger.info(f"[AIReviewService] Successfully summarized {len(summaries)} reviews")
                return {
                    "reviews": reviews_to_summarize,
                    "summaries": summaries,
                    "total_summarized": len(summaries)
                }
            else:
                logger.warning("[AIReviewService] Unexpected response format for summarization")
                return {"reviews": reviews_to_summarize, "summaries": []}
                
        except Exception as e:
            logger.error(f"[AIReviewService] Error summarizing reviews: {e}")
            return {"reviews": raw_reviews, "summaries": [], "error": str(e)}

