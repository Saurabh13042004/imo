# Review Scraping Pipeline - Architecture & Implementation

## Overview

Complete refactoring of the review scraping pipeline to achieve high signal, low noise extraction. Eliminates pollution from cookie banners, JS warnings, navigation text, and duplicate content.

## Architecture Components

### 1. Scraper Decision Layer (`scraper.py`)

**Scrape Strategy Selection:**
- Fetches HTML with httpx first (fast path)
- Detects JS requirement indicators:
  - "enable javascript", "cookies required"
  - Minimal text content (<200 chars after noise removal)
  - Absence of review-related keywords
- Escalates to headless browser rendering only when needed
- Limits JS-rendered pages to 2 per request (performance)

**Key Functions:**
- `needs_js_rendering(html)` - Smart detection
- `fetch_html(url)` - Async httpx fetch
- `extract_text_blocks(html)` - Strict filtering
- `deduplicate_reviews(reviews)` - Exact + near-duplicate removal
- `text_similarity(text1, text2)` - 90% threshold detection

### 2. Store Review Service (`store_review_service.py`)

**Flow:**
```
fetch_store_reviews(urls)
  ↓
_scrape_store(url) [parallel]
  ├─ fetch_html(url) with httpx
  ├─ needs_js_rendering(html)?
  │  ├─ YES → render_with_browser(url)
  │  └─ NO → use existing HTML
  ├─ _extract_reviews_from_html(html, url)
  │  ├─ extract_text_blocks() [opinion keywords + noise filtering]
  │  ├─ extract_rating() [patterns like ★★★, 4.5/5]
  │  └─ clean_text()
  └─ return reviews
  ↓
deduplicate_reviews(all_reviews) [90% similarity]
  ↓
validate_and_normalize_reviews() [AI validation]
  ↓
normalize_store_reviews() [extract trust scores]
```

**Noise Filtering:**
- Cookie banners: Keywords like "cookie", "privacy", "accept"
- JS warnings: "loading", "error", "exception"
- Navigation: "menu", "navigation", "sidebar"
- Marketing: "click here", "subscribe", "newsletter"
- Social UI: "like", "share", "comment"

**Strict Review Containers:**
- Only content containing opinion keywords
- Minimum length: 50 chars
- Maximum length: 3000 chars
- Skips repeated social fragments

### 3. Community Review Service (`community_review_service.py`)

**Search Queries (Forum-Biased):**
```
Reddit queries:
- "{product} review site:reddit.com"
- "{product} worth it reddit"
- "{product} problems site:reddit.com"

Forum queries:
- "{product} review forum"
- "{product} discussion thread"
- "{product} user experience forum"
- "{product} problems site:forum"
- "{product} issues discussion"
```

**Reddit-Specific Extraction:**
- Extract post body (main content)
- Extract top 3 comments only
- Remove: sidebar, related answers, footer, nav
- Skip deleted comments
- Pattern matching for post containers

**Forum-Specific Extraction:**
- Identify discussion threads (repeated comment blocks)
- Extract username + timestamp patterns
- Ignore quoted replies (>> or > prefix)
- Skip signatures (after --- separator)
- Limit to first 10 posts
- Fallback to generic extraction if no forum patterns found

**Deduplication:**
- Exact duplicate removal (MD5 hashing)
- Near-duplicate removal (>90% text similarity)
- Applied before AI processing

### 4. AI Review Service (`ai_review_service.py`)

**Validation Pipeline:**
```
validate_and_normalize_reviews(reviews, context)
  ├─ Batch validate reviews (max 20)
  ├─ AI checks per review:
  │  ├─ Is it a REAL review? (not question/nav/spec)
  │  ├─ Does it contain opinion/experience?
  │  └─ Confidence score (0-1)
  ├─ Filter: only keep confidence >= 0.5
  └─ Return with confidence metadata
```

**Normalization:**
- Community reviews:
  - Overall sentiment (positive/mixed/negative)
  - Common praises (3-5 points)
  - Common complaints (3-5 points)

- Store reviews:
  - Average rating (1-5) normalized
  - Trust score (0-1)
  - Verified positive patterns
  - Verified negative patterns

### 5. Browser Rendering Fallback

**Strategy:**
- Uses Playwright first (async, faster)
- Falls back to Selenium if Playwright unavailable
- Headless mode enabled
- Waits for review elements:
  - Elements with class/data-testid containing "review"
  - Star icons
  - Rating elements
- Timeout: 30 seconds, wait: 5 seconds
- Graceful failure with logging

## Quality Bar

**Output Must NOT Contain:**
- ✓ Cookie banners
- ✓ JavaScript warnings
- ✓ Navigation text
- ✓ Duplicate Reddit posts
- ✓ Marketing copy
- ✓ Quoted replies (forums)
- ✓ Signatures
- ✓ Sidebar content

**Output MUST Contain:**
- ✓ Actual user opinions
- ✓ Product reviews/experiences
- ✓ Genuine ratings and feedback
- ✓ Deduplicated content
- ✓ High confidence scores
- ✓ Opinion-bearing text only

## Performance Characteristics

**Parallel Processing:**
- Store URLs scraped in parallel
- Community searches run in parallel (limited to 6 queries)
- Deduplication runs after parallel scraping

**JS Rendering Limit:**
- Maximum 2 JS-rendered pages per store review request
- Prevents excessive delays
- Selenium/Playwright used only when necessary

**Response Times (Estimated):**
- Simple store scraping: 3-5 seconds
- With JS rendering: 15-30 seconds (per page)
- Community reviews: 10-15 seconds (depends on search results)
- Full normalization: +3-5 seconds (AI calls)

## Configuration & Dependencies

**New Requirements:**
- `playwright==1.40.0` - Async browser automation (primary)
- `selenium==4.15.2` - Fallback browser automation

**Environment:**
- GEMINI_API_KEY required for validation
- SERPAPI_KEY required for community searches
- Both services degrade gracefully if keys missing

## API Integration

### Community Reviews Endpoint
```
POST /api/v1/reviews/community
{
  "product_name": "Dyson Airwrap",
  "brand": "Dyson"
}

Response:
{
  "success": true,
  "product_name": "Dyson Airwrap",
  "source": "community",
  "summary": {
    "overall_sentiment": "positive",
    "common_praises": ["styling power", "versatility"],
    "common_complaints": ["price", "heat damage"]
  },
  "reviews": [
    {
      "source": "reddit",
      "text": "Great styler but expensive...",
      "confidence": 0.95
    }
  ],
  "total_found": 12,
  "raw_count": 45
}
```

### Store Reviews Endpoint
```
POST /api/v1/reviews/store
{
  "product_name": "Dyson Airwrap",
  "store_urls": [
    "https://www.ulta.com/dyson-airwrap",
    "https://www.sephora.com/dyson-airwrap"
  ]
}

Response:
{
  "success": true,
  "product_name": "Dyson Airwrap",
  "source": "store",
  "summary": {
    "average_rating": 4.3,
    "trust_score": 0.87,
    "verified_patterns": {
      "positive": ["long-lasting", "easy to use"],
      "negative": ["pricey", "tangled cord"]
    }
  },
  "reviews": [
    {
      "store": "ulta",
      "text": "Absolutely love this product...",
      "rating": 5.0,
      "confidence": 0.92
    }
  ],
  "total_found": 18,
  "raw_count": 89
}
```

## Error Handling

**Graceful Degradation:**
- Missing API keys → returns sanitized data, logs warning
- Failed page fetches → continues with other URLs
- JS rendering failures → uses original HTML or skips
- AI validation errors → includes all reviews with lower confidence
- Malformed responses → uses fallback parsing with regex

**Logging:**
- All major steps logged with context
- Warnings for skipped content
- Debug info for filtering decisions
- Error traces on critical failures

## Testing Recommendations

1. **Test noisy sources:**
   - E-commerce sites with heavy JS
   - Forums with ads and signatures
   - Reddit with sidebar content

2. **Verify filtering:**
   - Cookie banner text removed
   - Navigation elements excluded
   - Marketing copy filtered
   - Duplicates eliminated

3. **Validate output:**
   - All reviews contain opinion keywords
   - No navigation text in results
   - No exact duplicates
   - Similar content deduplicated

4. **Performance tests:**
   - JS rendering only when needed
   - Parallel requests complete in <10s
   - Browser timeouts handled correctly

## Future Enhancements

- Add response caching (Redis)
- Implement site-specific selectors (optional)
- Add review date extraction
- Implement reviewer credibility scoring
- Add image/video extraction from reviews
- Batch processing with streaming responses
