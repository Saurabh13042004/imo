# Reddit + Forum Review Integration

## Overview

This implementation adds Reddit and forum review fetching capabilities to the IMO backend review service. Reviews from these sources are enriched/non-canonical data that supplements Amazon reviews.

## Architecture

### Components

#### 1. **RedditClient** (`app/integrations/reddit.py`)
- **Primary Method**: `async search_product(product_name: str) -> List[Dict]`
- **Dual Strategy**:
  - OAuth API (if credentials available): More reliable, rate-limited
  - Public JSON API (fallback): No auth required, public endpoints
  
**Search Strategy**:
- Generates 3 search queries:
  - `"{product_title}" review`
  - `"{product_title}" worth it`
  - `"{product_title}" problems`
- Filters threads to relevant product discussions
- Fetches top-level comments from each thread
- Returns normalized review objects

**Validation Rules**:
- URL must contain `/comments/`
- Excludes "deal", "meme", "buying guide" posts
- Requires ≥5 comments on thread
- Comments must be ≥10 words
- Ignores bot comments

#### 2. **ForumClient** (`app/integrations/forums.py`)
- **Primary Method**: `async search_product(product_title: str) -> List[Dict]`
- **Supported Forums**:
  - head-fi.org (headphone discussions)
  - avforums.com (AV equipment)
  - quora.com (general Q&A)
  - gearslutz.com (audio gear)
  - telephony.gearspace.com (gear discussions)

**Validation Rules**:
- Page content must be ≥3000 characters
- Product mentioned ≥3 times
- Extracts readable text (removes scripts, styles, nav, footer)

#### 3. **ReviewService Updates** (`app/services/review_service.py`)
- Added `_normalize_reviews()` method for cross-source field mapping
- Updated `_fetch_source_reviews()` to handle "reddit" and "forum" sources
- Handles field name variations across sources

### Data Flow

```
Product Detail Request
         ↓
ReviewService.fetch_reviews()
         ↓
    Parallel Fetch Tasks:
    ├─ Amazon (canonical)
    ├─ Reddit (enrichment)
    ├─ Forum (enrichment)
    └─ YouTube (enrichment)
         ↓
_normalize_reviews() - Map source fields to standard Review schema
         ↓
_save_review() - Deduplicate by source_review_id and store
         ↓
Database - Cached for 7 days
         ↓
API Response - Combined reviews list
```

## API Integration

### Endpoint
```
POST /api/v1/product/{product_id}/reviews
```

### Request Body
```json
{
  "sources": ["amazon", "reddit", "forum"],
  "force_refresh": false
}
```

### Response (Example)
```json
{
  "reviews": [
    {
      "id": "uuid",
      "source": "reddit",
      "source_review_id": "abc123xyz",
      "author": "username",
      "rating": null,
      "title": "Thread Title",
      "content": "Comment body text...",
      "url": "https://reddit.com/r/...",
      "fetched_at": "2025-12-14T10:30:00Z"
    },
    {
      "id": "uuid",
      "source": "forum",
      "source_review_id": "def456uvw",
      "author": "Forum User",
      "rating": null,
      "title": "Page Title",
      "content": "Extracted forum discussion...",
      "url": "https://head-fi.org/...",
      "fetched_at": "2025-12-14T10:30:00Z"
    }
  ],
  "total": 2
}
```

## Field Normalization Mapping

| Reddit Field | Forum Field | Review Model | Notes |
|---|---|---|---|
| `review_text` | `review_text` | `content` | Main review text |
| `review_title` | `review_title` | `title` | Optional title |
| `author` | `author` | `author` | Username or "Forum User" |
| `source_review_id` | `source_review_id` | `source_review_id` | Unique identifier |
| `url` | `url` | `url` | Link to original |
| N/A | N/A | `rating` | Set to null (not available) |
| `helpful_count` | `helpful_count` | N/A | Not stored in main model |

## Performance & Safety

### Rate Limiting
- Reddit: Uses public API (no strict rate limit) or OAuth (limited)
- Forums: Uses HTTP timeouts, respects robots.txt
- Default timeout: 10 seconds per request

### Error Handling
- Failures in Reddit/Forum do NOT affect Amazon reviews
- All exceptions caught and logged
- Returns empty list on source failure
- Continues processing other sources

### Caching
- Reviews cached in database for 7 days
- Deduplication by `(product_id, source, source_review_id)`
- Force refresh available via `force_refresh=True`

### Safeguards
- Content filtering (minimum length checks)
- Relevance validation (product mention frequency)
- Bot comment detection
- Deleted content filtering
- Non-canonical source marking

## Configuration

No additional environment variables required. Optional settings in `.env`:

```env
# Optional: Reddit OAuth (for better rate limits)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret

# API timeouts (seconds)
HTTP_TIMEOUT=10
API_TIMEOUT=10
```

## Database Schema

Reviews stored in `Review` table with columns:
- `id` (UUID)
- `product_id` (FK to Product)
- `source` (Enum: "amazon", "reddit", "forum", "youtube")
- `source_review_id` (String, unique per source)
- `author` (String)
- `rating` (Optional[Float])
- `title` (String)
- `content` (Text)
- `url` (String)
- `fetched_at` (DateTime)

## UI Compatibility

All reviews normalize to fields compatible with existing `ProductReviews` component:
- ✅ `reviewer_name` (from `author`)
- ✅ `source` (from source enum)
- ✅ `review_text` (from `content`)
- ✅ `review_date` (from `fetched_at`)
- ✅ `rating` (from `rating`, may be null)
- ✅ `source_url` (from `url`)

**No breaking changes to existing UI.**

## Example Usage

### Python Backend
```python
from app.services.review_service import ReviewService
from app.database import AsyncSessionLocal

service = ReviewService()

async with AsyncSessionLocal() as db:
    # Fetch product
    product = await db.get(Product, product_id)
    
    # Fetch reviews from all sources
    reviews = await service.fetch_reviews(
        db=db,
        product=product,
        sources=["amazon", "reddit", "forum"],
        force_refresh=False
    )
    
    # Return to client
    return [ReviewResponse.from_orm(r) for r in reviews]
```

### API Call
```bash
curl -X POST http://localhost:8000/api/v1/product/12345/reviews \
  -H "Content-Type: application/json" \
  -d '{"sources": ["amazon", "reddit", "forum"], "force_refresh": false}'
```

## Monitoring & Logging

All integration activities logged at different levels:

```python
logger.info(f"Found {len(results)} Reddit reviews for: {product_name}")
logger.warning(f"Reddit credentials not configured")
logger.debug(f"Error searching query '{query}': {e}")
logger.error(f"Error fetching Reddit thread: {e}")
```

Check logs in: `app/logs/` or stdout (depends on logging config)

## Future Enhancements

- [ ] Add SerpAPI integration for better forum search
- [ ] Sentiment analysis for Reddit/forum comments
- [ ] Thread ranking by relevance
- [ ] Duplicate detection across sources
- [ ] Review freshness scoring
- [ ] Automated moderation for spam/off-topic
- [ ] Caching strategy optimization
- [ ] Webhook support for real-time updates

## Troubleshooting

### Reddit returns empty results
1. Check if `product.title` is descriptive enough
2. Verify network connectivity
3. Check Reddit API status
4. Enable debug logging: `logger.setLevel(logging.DEBUG)`

### Forums returning no reviews
1. Forum discovery requires Google API integration (not yet implemented)
2. Currently searches by generate search URLs (empty by default)
3. TODO: Add SerpAPI integration for forum discovery

### Reviews not caching
1. Check database connection
2. Verify `fetched_at` timestamp is recent
3. Check 7-day cache window

### Performance issues
1. Consider limiting `sources` to ["amazon"] for critical paths
2. Implement background job for non-critical review fetching
3. Increase timeout values if needed

## Testing

```python
# Test Reddit client
from app.integrations.reddit import RedditClient

client = RedditClient()
reviews = await client.search_product("Sony WH-1000XM5")
assert len(reviews) > 0
assert reviews[0]["source_review_id"]
assert reviews[0]["author"]

# Test Forum client
from app.integrations.forums import ForumClient

forum_client = ForumClient()
reviews = await forum_client.search_product("Sony WH-1000XM5")
# Will return empty until search URLs implemented

# Test ReviewService integration
reviews = await service.fetch_reviews(
    db=db,
    product=product,
    sources=["reddit", "forum"]
)
```

## References

- Reddit API Docs: https://www.reddit.com/dev/api
- BeautifulSoup4: https://www.crummy.com/software/BeautifulSoup/
- HTTPX: https://www.python-httpx.org/
- SQLAlchemy: https://docs.sqlalchemy.org/
