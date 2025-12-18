"""
Example API Requests for Reddit + Forum Review Integration

This file contains example curl commands and code snippets for testing
the new Reddit and Forum review fetching integration.
"""

# ============================================================================
# cURL Examples
# ============================================================================

# 1. Fetch reviews from all sources (Amazon + Reddit + Forum)
curl -X POST http://localhost:8000/api/v1/product/prod_12345/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["amazon", "reddit", "forum"],
    "force_refresh": false
  }'

# 2. Fetch only Reddit reviews
curl -X POST http://localhost:8000/api/v1/product/prod_12345/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["reddit"],
    "force_refresh": false
  }'

# 3. Force refresh (ignore cache)
curl -X POST http://localhost:8000/api/v1/product/prod_12345/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["amazon", "reddit", "forum"],
    "force_refresh": true
  }'

# 4. Fetch forum reviews only (currently returns empty - needs SerpAPI)
curl -X POST http://localhost:8000/api/v1/product/prod_12345/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["forum"],
    "force_refresh": false
  }'


# ============================================================================
# Python Examples
# ============================================================================

# Example 1: Direct client usage
import asyncio
from app.integrations.reddit import RedditClient
from app.integrations.forums import ForumClient

async def test_clients():
    reddit = RedditClient()
    forum = ForumClient()
    
    # Search Reddit
    reddit_reviews = await reddit.search_product("Sony WH-1000XM5")
    print(f"Found {len(reddit_reviews)} Reddit reviews")
    for review in reddit_reviews:
        print(f"  - {review['author']}: {review['review_text'][:50]}...")
    
    # Search Forums
    forum_reviews = await forum.search_product("Sony WH-1000XM5")
    print(f"Found {len(forum_reviews)} forum reviews")

# Run it
asyncio.run(test_clients())


# Example 2: Via ReviewService
import asyncio
from app.services.review_service import ReviewService
from app.database import AsyncSessionLocal
from app.models import Product

async def test_review_service():
    service = ReviewService()
    
    async with AsyncSessionLocal() as db:
        # Get a product
        product = await db.get(Product, "prod_12345")
        
        # Fetch reviews from multiple sources
        reviews = await service.fetch_reviews(
            db=db,
            product=product,
            sources=["amazon", "reddit", "forum"],
            force_refresh=False
        )
        
        # Print results
        print(f"\nTotal reviews: {len(reviews)}")
        for review in reviews:
            print(f"\n[{review.source.upper()}] {review.author}")
            print(f"  Title: {review.title}")
            print(f"  Content: {review.content[:100]}...")
            if review.url:
                print(f"  URL: {review.url}")

asyncio.run(test_review_service())


# Example 3: Test normalization
from app.services.review_service import ReviewService

service = ReviewService()

# Simulate Reddit data
reddit_data = [
    {
        "source_review_id": "reddit_abc123",
        "author": "audiofilenerd",
        "review_text": "These headphones have amazing sound quality...",
        "review_title": "Best headphones I've owned",
        "url": "https://reddit.com/r/headphones/comments/abc123/",
        "helpful_count": 145
    }
]

# Normalize
normalized = service._normalize_reviews(reddit_data, "reddit")
print(f"Normalized review:")
print(f"  source_review_id: {normalized[0]['source_review_id']}")
print(f"  author: {normalized[0]['author']}")
print(f"  title: {normalized[0]['title']}")
print(f"  content: {normalized[0]['content'][:50]}...")
print(f"  rating: {normalized[0]['rating']}")  # None for Reddit
print(f"  url: {normalized[0]['url']}")


# ============================================================================
# JavaScript/TypeScript Examples (Frontend)
# ============================================================================

// Example 1: Fetch reviews in React component
async function fetchProductReviews(productId: string) {
  try {
    const response = await fetch(
      `/api/v1/product/${productId}/reviews`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sources: ['amazon', 'reddit', 'forum'],
          force_refresh: false
        })
      }
    );
    
    const data = await response.json();
    return data.reviews;
  } catch (error) {
    console.error('Failed to fetch reviews:', error);
    return [];
  }
}

// Example 2: In ProductDetails component
import { useEffect, useState } from 'react';

export function ProductDetails({ productId }: { productId: string }) {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadReviews() {
      setLoading(true);
      const data = await fetchProductReviews(productId);
      setReviews(data);
      setLoading(false);
    }
    
    loadReviews();
  }, [productId]);

  if (loading) return <div>Loading reviews...</div>;

  // Group reviews by source
  const reviewsBySource = reviews.reduce((acc, review) => {
    acc[review.source] = (acc[review.source] || []).concat(review);
    return acc;
  }, {} as Record<string, Review[]>);

  return (
    <div className="reviews-container">
      {Object.entries(reviewsBySource).map(([source, sourceReviews]) => (
        <div key={source} className="reviews-section">
          <h3>{source.toUpperCase()} Reviews ({sourceReviews.length})</h3>
          {sourceReviews.map(review => (
            <ReviewCard key={review.id} review={review} />
          ))}
        </div>
      ))}
    </div>
  );
}

// Example 3: Filter reviews by source
function filterReviewsBySource(reviews: Review[], source: string): Review[] {
  return reviews.filter(r => r.source === source);
}


# ============================================================================
# Testing Scenarios
# ============================================================================

"""
Test Scenario 1: Valid Product with Reviews
- Product: "Sony WH-1000XM5"
- Expected: 10-50+ reviews from Reddit
- Expected: 0-5 reviews from forums (needs SerpAPI)
- Expected: 50-200+ reviews from Amazon

Test Scenario 2: Niche Product
- Product: "Focal Elear Headphones"
- Expected: 2-10 reviews from Reddit
- Expected: 0-2 reviews from forums
- Expected: 5-20 reviews from Amazon

Test Scenario 3: Generic Product (Low Specificity)
- Product: "headphones"
- Expected: 100+ Reddit reviews (but mostly irrelevant)
- Expected: Low relevance scores
- Note: Should filter out non-specific results

Test Scenario 4: Non-Existent Product
- Product: "zzzzabc12345xyz_fake"
- Expected: 0 reviews from all sources
- Expected: Graceful handling, no errors
- Expected: Logs show no results found

Test Scenario 5: Reddit OAuth Disabled
- Set: REDDIT_CLIENT_ID="" (empty)
- Expected: Falls back to public API
- Expected: Still returns results
- Expected: Log shows fallback to public API

Test Scenario 6: Network Timeout
- Simulate: Network delay > 10 seconds
- Expected: Timeout caught, logged as warning
- Expected: Other sources continue processing
- Expected: Partial results returned
"""


# ============================================================================
# Monitoring & Debugging
# ============================================================================

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('app.integrations.reddit').setLevel(logging.DEBUG)
logging.getLogger('app.integrations.forums').setLevel(logging.DEBUG)
logging.getLogger('app.services.review_service').setLevel(logging.DEBUG)

# Check logs for:
# - INFO: Found X Reddit reviews for 'product'
# - WARNING: Reddit credentials not configured
# - ERROR: Error fetching reviews from reddit: <error>
# - DEBUG: Error searching query '<query>': <error>


# ============================================================================
# Performance Benchmarks
# ============================================================================

"""
Expected Performance:
- Single product reviews (all sources): 2-5 seconds
- Reddit search: 0.5-1.5 seconds
- Forums search: 1-2 seconds (depending on page load)
- Database save: <100ms per review
- Total for 50 reviews: ~3-5 seconds

Bottlenecks:
- Network I/O (external APIs)
- HTML parsing for forums (BeautifulSoup)
- Database inserts
- Deduplication logic

Optimization opportunities:
- Batch database inserts
- Use connection pooling
- Cache parsing results
- Parallel processing within source
"""


# ============================================================================
# Error Scenarios
# ============================================================================

"""
Error Handling Tests:

1. Reddit API Down
   - Status: ✅ Caught as httpx.HTTPError
   - Logging: ERROR logged
   - Result: Empty list, other sources continue

2. Invalid Product Title
   - Input: Empty string or None
   - Status: ✅ Handled gracefully
   - Result: Returns empty list

3. Database Connection Lost
   - Status: ✅ Caught in _save_review()
   - Logging: ERROR logged, rollback called
   - Result: Review not saved, but search continues

4. Timeout on Forum Fetch
   - Status: ✅ Caught as httpx.TimeoutException
   - Logging: DEBUG logged
   - Result: Continues to next forum

5. Malformed HTML in Forum
   - Status: ✅ BeautifulSoup handles gracefully
   - Logging: DEBUG logged if parse fails
   - Result: Returns empty for that page

6. Missing ASIN for Amazon (not applicable)
   - But for completeness in review service
   - Status: ✅ Checked and skipped

7. Concurrent requests to same product
   - Status: ✅ Database deduplication handles it
   - Result: First write wins, others update

8. Rate limiting from Reddit
   - Status: ✅ Respects HTTP 429, retries with backoff
   - Result: Waits and retries (default httpx behavior)
"""


# ============================================================================
# Integration Verification Checklist
# ============================================================================

"""
After deploying, verify:

☐ Backend starts without import errors
☐ beautifulsoup4 installed: pip show beautifulsoup4
☐ POST /api/v1/product/{id}/reviews endpoint works
☐ Can fetch Amazon reviews (existing functionality)
☐ Can fetch Reddit reviews
☐ Forum reviews return empty (expected, needs SerpAPI)
☐ Reviews are deduplicated
☐ Database caching works (7-day TTL)
☐ Force refresh bypasses cache
☐ Errors in Redis don't break retrieval
☐ Logs show source attribution
☐ Frontend displays source badges
☐ Mobile UI renders reviews correctly
☐ Search doesn't break on special characters
☐ Very long reviews truncate gracefully
☐ URL links work in review content
"""
