# Reddit + Forum Review Integration - Quick Reference

## What Was Implemented

### ✅ Completed Features

1. **RedditClient** (`app/integrations/reddit.py`)
   - Dual-mode search: OAuth (if credentials) → Fallback to public API
   - Multi-query search strategy (review, worth it, problems)
   - Thread filtering (relevance, comment count, content quality)
   - Comment extraction with validation (minimum length, anti-spam)
   - Normalized output compatible with Review model

2. **ForumClient** (`app/integrations/forums.py`)
   - Support for 5+ forum sites (Head-Fi, AVForums, Quora, etc.)
   - HTML parsing with BeautifulSoup (content extraction)
   - Content validation (length, mention frequency)
   - Duplicate detection (URL hashing)
   - Normalized output compatible with Review model

3. **ReviewService Integration** (`app/services/review_service.py`)
   - Added `_normalize_reviews()` method for cross-source field mapping
   - Updated `_fetch_source_reviews()` to handle "reddit" and "forum"
   - Parallel fetching with error isolation (Reddit/Forum failures don't break Amazon reviews)
   - Database caching (7-day TTL)

4. **Dependencies**
   - Added `beautifulsoup4==4.12.2` to requirements.txt

### 📦 Files Modified/Created

```
backend/
├── app/
│   ├── integrations/
│   │   ├── reddit.py          [MODIFIED: Enhanced with dual-mode search]
│   │   ├── forums.py          [CREATED: New forum fetching client]
│   │   └── __init__.py        [MODIFIED: Added ForumClient export]
│   ├── services/
│   │   └── review_service.py  [MODIFIED: Added normalization & integration]
├── tests/
│   └── test_reddit_forum_integration.py [CREATED: Test suite]
├── requirements.txt           [MODIFIED: Added beautifulsoup4]
└── REDDIT_FORUM_INTEGRATION.md [CREATED: Full documentation]
```

## How It Works

### API Endpoint
```bash
POST /api/v1/product/{product_id}/reviews
Content-Type: application/json

{
  "sources": ["amazon", "reddit", "forum"],
  "force_refresh": false
}
```

### Response
Reviews combined from all sources with source attribution:
```json
{
  "reviews": [
    {
      "source": "reddit",
      "source_review_id": "abc123",
      "author": "username",
      "content": "Comment text...",
      "url": "https://reddit.com/r/.../abc123"
    },
    {
      "source": "forum",
      "source_review_id": "def456",
      "author": "Forum User",
      "content": "Forum discussion...",
      "url": "https://head-fi.org/..."
    }
  ]
}
```

## Key Features

### Error Isolation
- ✅ Reddit fails → Amazon still works
- ✅ Forum fails → Other sources unaffected
- ✅ All failures logged with context

### Deduplication
- ✅ By `(product_id, source, source_review_id)`
- ✅ No duplicate reviews in same source
- ✅ Same URL different source = kept

### Content Filtering
- ✅ Reddit: ≥10 word comments, no bots, no "[deleted]"
- ✅ Forums: ≥3000 char pages, product ≥3 mentions
- ✅ Both: product title keyword matching

### Performance
- ✅ Async/parallel fetching
- ✅ 10-second timeouts per request
- ✅ 7-day database cache
- ✅ Handles rate limiting gracefully

## Usage Examples

### In Python Code
```python
from app.services.review_service import ReviewService
from app.database import AsyncSessionLocal

service = ReviewService()

async with AsyncSessionLocal() as db:
    product = await db.get(Product, "prod_123")
    
    # Get reviews from multiple sources
    reviews = await service.fetch_reviews(
        db=db,
        product=product,
        sources=["amazon", "reddit", "forum"],
        force_refresh=False
    )
    
    # reviews now contains data from all sources
    for review in reviews:
        print(f"{review.source}: {review.content[:100]}")
```

### In Frontend
```typescript
// ProductDetails.tsx already handles this!
// Reviews fetched server-side and returned in /reviews endpoint

const response = await fetch(`/api/v1/product/${productId}/reviews`, {
  method: 'POST',
  body: JSON.stringify({ sources: ['amazon', 'reddit', 'forum'] })
});

const { reviews } = await response.json();
// Use existing ProductReviews component - no UI changes needed!
```

## Configuration

### Optional Environment Variables
```env
# Reddit OAuth (improves rate limits)
REDDIT_CLIENT_ID=xxx
REDDIT_CLIENT_SECRET=yyy

# Request timeouts (seconds)
HTTP_TIMEOUT=10
API_TIMEOUT=10
```

### No External API Keys Required (By Default)
- ✅ Reddit public API (works without credentials)
- ✅ Forum HTML fetching (works with httpx)
- ⚠️ Forum discovery currently placeholder (requires SerpAPI/Google API)

## Testing

### Run Unit Tests
```bash
cd backend
pytest tests/test_reddit_forum_integration.py -v
```

### Test Normalization
```python
from app.services.review_service import ReviewService

service = ReviewService()

# Test Reddit review normalization
reddit_data = [
    {
        "source_review_id": "reddit_123",
        "author": "user",
        "review_text": "Great!",
        "review_title": "My Review"
    }
]
normalized = service._normalize_reviews(reddit_data, "reddit")
assert normalized[0]["content"] == "Great!"
assert normalized[0]["title"] == "My Review"
```

## Monitoring

### Logs to Check
```
INFO: Found X Reddit reviews for '<product>'
INFO: Found Y forum reviews for '<product>'
WARNING: Reddit credentials not configured (using public API)
ERROR: Error fetching reviews from reddit: <error>
```

### Debugging
```python
import logging
logging.getLogger("app.integrations.reddit").setLevel(logging.DEBUG)
logging.getLogger("app.integrations.forums").setLevel(logging.DEBUG)
```

## Limitations & TODOs

### Current Limitations
1. ❌ Forum discovery not fully implemented (needs SerpAPI)
2. ❌ No sentiment analysis yet
3. ❌ No duplicate detection across sources
4. ❌ Reddit ratings always null (not available)

### Future Enhancements
- [ ] Integrate SerpAPI for forum search
- [ ] Add sentiment analysis (positive/negative/neutral)
- [ ] Similarity scoring to detect duplicates
- [ ] Webhook for real-time new reviews
- [ ] Thread ranking algorithm
- [ ] Spam/moderation scoring

## Troubleshooting

### No Reddit reviews returned
1. Check product title is descriptive: `"Sony WH-1000XM5"` works, `"headphones"` might not
2. Verify Reddit accessibility from your network
3. Enable debug logging
4. Check logs for specific errors

### Forum reviews always empty
- Expected! Forum discovery not yet implemented
- TODO: Add SerpAPI integration

### Database errors on save
1. Check database connection
2. Verify Review model schema
3. Check for constraint violations
4. Review logs for constraint errors

### Performance issues
- Reduce sources: use `["amazon"]` first
- Implement background job queue (Celery)
- Increase timeout values if needed
- Check database slow queries

## Architecture Decisions

### Why Dual-Mode Reddit Search?
- OAuth mode: Better rate limits, more reliable
- Public API: Works without configuration, simplest deployment
- Fallback: Ensures functionality even if OAuth config missing

### Why Field Normalization?
- Different sources have different field names
- Central mapping allows flexible source addition
- Easy to add YouTube, Twitter, etc. later
- No UI changes needed

### Why Error Isolation?
- Core product data (Amazon) is critical
- Enrichment sources (Reddit/Forums) are optional
- One source failure shouldn't break entire flow
- Better user experience with partial data

### Why 7-Day Cache?
- Reviews don't change frequently
- Reduces API calls (cost & rate limits)
- Still relatively fresh
- Force refresh available for critical updates

## Next Steps for Full Integration

1. **Search Enhancement**
   - Integrate SerpAPI for forum discovery
   - Add Google Custom Search API

2. **Quality Scoring**
   - Implement review relevance ranking
   - Add sentiment analysis
   - Spam detection

3. **Performance**
   - Background job queue (Celery)
   - Caching layer (Redis)
   - Database optimization

4. **Analytics**
   - Track review source distribution
   - Monitor API latencies
   - Alert on source failures

5. **UI Enhancements**
   - Source badges/filters
   - Relevance sorting
   - Spam reporting

## Support

For issues or questions:
1. Check `REDDIT_FORUM_INTEGRATION.md` for detailed docs
2. Review test cases in `test_reddit_forum_integration.py`
3. Check backend logs: `app/logs/`
4. Verify configuration in `.env`
