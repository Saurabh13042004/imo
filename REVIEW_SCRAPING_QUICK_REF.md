# Review Scraping Pipeline - Quick Implementation Reference

## Files Modified

### 1. `backend/app/services/scraper.py`
**Enhanced with:**
- `needs_js_rendering(html)` - Detects pages requiring browser automation
- `extract_text_blocks(html)` - Strict noise filtering with opinion keyword detection
- `deduplicate_reviews(reviews)` - Exact + near-duplicate (90%+ similarity) removal
- `text_similarity(text1, text2)` - Similarity scoring algorithm

**Key Constants Added:**
```python
JS_REQUIRED_INDICATORS = [
    'enable javascript',
    'javascript required',
    'cookies required',
    # ... more patterns
]

NOISE_PATTERNS = [
    'cookie', 'privacy policy', 'terms of service',
    'click here', 'subscribe', 'sidebar', 'navigation',
    # ... more patterns
]

MIN_TEXT_LENGTH = 50
MAX_TEXT_LENGTH = 3000
```

### 2. `backend/app/services/store_review_service.py`
**Complete Rewrite with:**
- `render_with_browser(url)` - Playwright/Selenium fallback
- `needs_js_rendering()` - Smart strategy selection
- `_extract_reviews_from_html()` - Strict extraction with deduplication
- JS render limit: 2 per request (performance)

**Flow:**
```
URL → Fetch (httpx) → Check JS needed? 
  → YES: Render (Playwright/Selenium)
  → Extract reviews (opinion + rating)
  → Deduplicate
  → Return
```

### 3. `backend/app/services/community_review_service.py`
**Enhanced with:**
- `_extract_reddit_content(html)` - Reddit-specific (post + top 3 comments)
- `_extract_forum_content(html)` - Forum-specific (threads + metadata)
- Forum-biased search queries (6 total)
- Deduplication before AI processing

**Reddit Extraction:**
- Post body only
- Top 3 comments
- Removes: sidebar, footer, nav, related
- Skips: deleted comments

**Forum Extraction:**
- Discussion threads (first 10)
- Removes: quoted replies (>>), ads, signatures (---)
- Preserves: usernames, timestamps

### 4. `backend/app/services/ai_review_service.py`
**New Method Added:**
- `validate_and_normalize_reviews(reviews, context)` - AI validation pipeline
  - Checks if each review is real (not question/nav/spec)
  - Scores confidence per review
  - Filters: confidence >= 0.5
  - Returns: reviewed list + filtered count

**Usage in Pipeline:**
```
Raw Reviews → Validate (AI) → Normalize (AI) → Response
```

### 5. `backend/app/api/routes/reviews.py`
**Updated Endpoints:**
- `/api/v1/reviews/community` - Added validation step + raw_count
- `/api/v1/reviews/store` - Added validation step + raw_count

**Response Enhanced:**
```json
{
  "reviews": [...],
  "total_found": 12,
  "raw_count": 45,
  "summary": {...}
}
```
Shows `raw_count` before validation, `total_found` after validation.

### 6. `backend/requirements.txt`
**Dependencies Added:**
```
playwright==1.40.0      # Async browser automation
selenium==4.15.2        # Fallback browser automation
```

## Key Algorithms

### 1. Noise Detection
```python
# In extract_text_blocks():
- Check opinion keywords: yes → keep
- Check noise patterns: yes → skip
- Check length (50-3000): keep only valid range
- Check fragment size: skip if <5 words
- Deduplicate by hash
```

### 2. JS Requirement Detection
```python
needs_js_rendering(html):
  - Check for "enable javascript" / "cookies required"
  - Check text length (if <200 chars → needs JS)
  - Check for review keywords
  - if missing keywords and content large → needs JS
```

### 3. Deduplication
```python
First Pass (Exact):
  - Hash each review text
  - Skip if hash seen

Second Pass (Near-Duplicate):
  - Compare against kept reviews
  - Remove if >90% similarity
  - Uses SequenceMatcher
```

### 4. AI Validation
```python
For each review:
  - Ask AI: "Is this a real review?"
  - Ask AI: "Does it have opinion?"
  - Get confidence score
  - Keep if confidence >= 0.5
```

## Testing Checklist

- [ ] Store scraping works without JS rendering
- [ ] JS rendering triggers on cookie-heavy pages
- [ ] Cookie banner text NOT in results
- [ ] Navigation text NOT in results
- [ ] Opinion-containing text IS in results
- [ ] Duplicate reviews removed
- [ ] Near-duplicates removed (>90% similarity)
- [ ] Reddit extraction gets post + comments
- [ ] Reddit sidebar NOT in results
- [ ] Forum extraction gets discussion threads
- [ ] Forum signatures NOT in results
- [ ] AI validation filters non-reviews
- [ ] Confidence scores present in response
- [ ] raw_count > total_found (showing filtering)

## Performance Notes

**Typical Times:**
- Simple store scrape: 3-5 sec
- With 1 JS render: 15-20 sec
- With 2 JS renders: 25-35 sec
- Community reviews: 10-15 sec
- AI validation: +2-3 sec
- AI normalization: +3-5 sec

**Optimization Strategies:**
- Parallel URL scraping (asyncio.gather)
- JS render limit (2 per request)
- Batch validation (max 20 per AI call)
- Early filtering (before AI processing)

## Troubleshooting

**Issue: Getting cookie banners in results**
- Check: NOISE_PATTERNS has "cookie" keyword
- Solution: Verify extract_text_blocks() is filtering properly
- Debug: Add logging to see filtered items

**Issue: JS rendering not triggering**
- Check: needs_js_rendering() detecting correctly
- Solution: Verify JS_REQUIRED_INDICATORS covers page
- Debug: Log HTML snippet to see what's happening

**Issue: Duplicate reviews in results**
- Check: deduplicate_reviews() is being called
- Solution: Verify similarity threshold (0.90) is appropriate
- Debug: Log similarity scores to see what's kept

**Issue: Too many non-review results**
- Check: validate_and_normalize_reviews() is working
- Solution: Lower confidence threshold if too strict
- Debug: Check AI response to see what's filtered

## API Examples

### Test Community Reviews
```bash
curl -X POST http://localhost:8000/api/v1/reviews/community \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Dyson Airwrap", "brand": "Dyson"}'
```

### Test Store Reviews
```bash
curl -X POST http://localhost:8000/api/v1/reviews/store \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Dyson Airwrap",
    "store_urls": [
      "https://www.ulta.com/dyson-airwrap",
      "https://www.amazon.com/Dyson-Airwrap"
    ]
  }'
```

## Logging Output Expected

```
INFO: Fetching community reviews for: Dyson Airwrap
INFO: Raw reviews fetched: 45
INFO: [AIReviewService] Validating reviews with AI
INFO: After exact dedup: 38 from 45
INFO: After similarity dedup: 25 from 38
INFO: [AIReviewService] Validated 12 reviews, filtered 13
INFO: [AIReviewService] Calling Gemini to normalize community reviews
INFO: [AIReviewService] Successfully normalized 12 community reviews
```

## Performance Optimizations

1. **Async Scraping**: All HTTP requests are async (httpx.AsyncClient)
2. **Parallel Processing**: Multiple URLs scraped simultaneously
3. **Early Filtering**: Noise removal before AI processing
4. **Batch Processing**: AI validation in batches (max 20 items)
5. **Smart JS Rendering**: Only when necessary, limited to 2 per request
6. **Stream Processing**: Results returned as soon as ready

## Non-Goals (What NOT Implemented)

- ✗ Site-specific scrapers (generic for all sites)
- ✗ Amazon-specific logic (uses generic approach)
- ✗ Firecrawl (uses httpx + Playwright)
- ✗ Caching (for now - future enhancement)
- ✗ Video extraction (text-only focus)
- ✗ Machine learning models (uses Gemini AI)
