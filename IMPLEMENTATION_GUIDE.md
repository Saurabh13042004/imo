# Implementation Guide

## Overview

This document provides detailed implementation guidance for the Product Aggregator & Review System.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   API Routes │  │   Schemas    │  │  Middleware  │       │
│  └──────┬───────┘  └──────────────┘  └──────────────┘       │
├─────────┼────────────────────────────────────────────────────┤
│  ┌──────┴──────────────────────────────────────────────┐    │
│  │              Business Logic (Services)              │    │
│  ├───────────────────────────────────────────────────┤    │
│  │ SearchService │ ReviewService │ VideoService       │    │
│  │ AIService     │ CacheService                        │    │
│  └───────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │    External API Integration (Integrations)          │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Amazon │ Walmart │ Google │ YouTube │ Reddit        │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │   PostgreSQL     │  │     Redis        │               │
│  │     Database     │  │     Cache        │               │
│  └──────────────────┘  └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Search Flow
```
1. User → POST /api/v1/search
2. SearchService → Check Cache
3. If cached → Return cached results
4. If not cached → Parallel API calls to all sources
5. Integration clients → External APIs
6. Results → Database storage
7. Cache → Store results with TTL
8. Response → Return to user
```

### Review Aggregation Flow
```
1. User → POST /api/v1/product/{id}/reviews
2. ReviewService → Check if reviews exist & are fresh
3. ReviewService → Parallel fetch from multiple sources
4. Integration clients → Reddit, YouTube, Amazon APIs
5. Review parsers → Normalize review data
6. Database → Store reviews
7. AIService → Sentiment analysis (optional)
8. Response → Return aggregated reviews
```

## Service Details

### SearchService
**Purpose**: Find products across multiple marketplaces

**Key Methods**:
- `search_all_sources()` - Parallel search across all enabled sources
- `_search_source()` - Search a specific source with caching
- `_save_product()` - Save product to database
- `_apply_filters()` - Filter results by rating, price, etc.

**Caching Strategy**:
- TTL: 1 hour (configurable)
- Key: `query + source`
- Invalidation: Manual or on `force_refresh`

### ReviewService
**Purpose**: Fetch and aggregate product reviews

**Key Methods**:
- `fetch_reviews()` - Parallel fetch from multiple sources
- `_fetch_source_reviews()` - Fetch from specific source
- `_save_review()` - Save/update review in database
- `analyze_sentiment()` - Aggregate sentiment scores

**Review Sources**:
- Amazon: Direct API (ASIN required)
- Reddit: Search public discussions
- YouTube: Comments on review videos
- Forums: Generic forum searches

### VideoService
**Purpose**: Find YouTube product review videos

**Key Methods**:
- `fetch_product_videos()` - Find videos for product
- `_save_video()` - Save video metadata
- `get_product_videos()` - Retrieve stored videos

**Video Metadata**:
- Video ID, title, channel info
- View count, like count, duration
- Published date, description

### AIService
**Purpose**: AI-powered review analysis

**Key Methods**:
- `summarize_reviews()` - Generate review summary using GPT
- `analyze_sentiment()` - Determine review sentiment
- `extract_pros_cons()` - Extract key points
- `generate_title_summary()` - Create concise summary

**Requirements**:
- OpenAI API key configured
- Graceful degradation if API unavailable

### CacheService
**Purpose**: Manage caching layer

**Key Methods**:
- `get_cache()` - Retrieve cached data
- `set_cache()` - Store data with TTL
- `invalidate_cache()` - Clear specific cache
- `cleanup_expired_cache()` - Maintenance task

## Integration Implementation

### Amazon Integration
**Endpoint**: RapidAPI Amazon Data Scraper
**Operations**:
- Search: Query products
- Details: Get product information
- Reviews: Fetch customer reviews

**Data Mapping**:
```
API Field → Model Field
title → title
asin → source_id (+ asin)
price → price
rating → rating
review_count → review_count
```

### Walmart Integration
**Endpoint**: Walmart RapidAPI
**Operations**:
- Search: Query products
- Details: Get product information

**Unique Features**:
- Different pricing structure
- Availability information

### Google Shopping Integration
**Endpoint**: Google SERP API
**Operations**:
- Search: Find products on Google Shopping
- Parse: Extract product information

### YouTube Integration
**Endpoint**: YouTube Data API v3
**Operations**:
- Search: Find product review videos
- Details: Get video metadata
- Stats: View count, like count

**Parsing**:
- ISO 8601 duration conversion
- Channel information extraction
- Thumbnail URL collection

### Reddit Integration
**Endpoint**: Reddit OAuth API
**Flow**:
1. Get OAuth token
2. Search for product discussions
3. Parse comments as reviews

**Considerations**:
- Rate limiting
- Comments vs posts
- Score/upvotes as helpful count

## Database Schema

### Products Table
- Stores product information from all sources
- Unique constraint: (source, source_id)
- Indexes on title for search
- Tracks fetch status and timestamps

### Reviews Table
- Links to products via product_id
- Unique constraint: (product_id, source, source_review_id)
- Stores sentiment analysis results
- Tracks image URLs (array)

### Videos Table
- Links to products via product_id
- Stores YouTube video metadata
- Unique constraint: (product_id, video_id)
- Includes view/like counts

### SearchCache Table
- Caches search results (JSON)
- TTL via expires_at timestamp
- Unique constraint: (query, source)
- Automatic cleanup of expired entries

## API Endpoints Reference

### POST /api/v1/search
**Purpose**: Search products
**Params**: query, sources, limit, min_rating, max_price
**Returns**: SearchResponse with product list

### GET /api/v1/product/{product_id}
**Purpose**: Get product details
**Returns**: ProductDetailResponse with reviews & videos

### POST /api/v1/product/details
**Purpose**: Get product by source
**Params**: product_id OR (source + source_id)
**Returns**: ProductDetailResponse

### POST /api/v1/product/{product_id}/reviews
**Purpose**: Fetch product reviews
**Params**: sources, force_refresh
**Returns**: ReviewsResponse

### POST /api/v1/product/{product_id}/videos
**Purpose**: Fetch product videos
**Params**: force_refresh, min_views
**Returns**: VideosResponse

## Configuration Management

### Environment Variables
```
DATABASE_URL          - PostgreSQL connection
API Keys             - RapidAPI, OpenAI, YouTube, Reddit
CACHE_TTL values     - Separate TTL for different data types
RATE_LIMIT settings  - Requests per time period
TIMEOUT values       - HTTP and API timeouts
LOG_LEVEL            - Logging verbosity
```

### Configuration Hierarchy
1. Environment variables
2. `.env` file
3. Default values in `config.py`

## Error Handling Strategy

### API Errors
- **Validation**: Return 422 with details
- **Not Found**: Return 404
- **Rate Limit**: Return 429 with retry info
- **Server Error**: Return 500 with error context

### Integration Errors
- **API Unavailable**: Log error, return cached data if available
- **Invalid Response**: Log and skip that source
- **Timeout**: Use configured retry logic
- **Auth Error**: Check credentials, log, skip source

### Database Errors
- **Connection**: Retry with backoff
- **Constraint Violation**: Log and handle gracefully
- **Query Error**: Log and return user-friendly error

## Performance Optimization

### Parallel Processing
```python
tasks = [search_amazon(), search_walmart(), search_google()]
results = await asyncio.gather(*tasks, return_exceptions=True)
```

### Caching Strategy
- Cache search results: 1 hour
- Cache product details: 24 hours
- Cache reviews: 7 days
- Configurable via environment

### Database Optimization
- Indexes on frequently queried columns
- Connection pooling
- Batch operations where possible
- Query result limiting

### API Rate Limiting
- Implement exponential backoff
- Respect API rate limits
- Queue requests if needed
- Cache responses aggressively

## Security Considerations

### API Key Management
- Store in environment variables
- Never commit to version control
- Use `.env` file (in .gitignore)
- Rotate regularly

### Input Validation
- Sanitize search queries
- Validate URLs and emails
- Check price ranges
- Validate enum values

### Database Security
- Use parameterized queries (SQLAlchemy)
- Connection string encryption
- User permissions by role
- Regular backups

### API Security
- CORS configuration
- Rate limiting per IP
- Input size limits
- SQL injection prevention

## Monitoring & Logging

### Logging Levels
- DEBUG: Detailed information
- INFO: General flow
- WARNING: Potentially harmful situations
- ERROR: Error conditions
- CRITICAL: Critical failures

### Metrics to Track
- API response times
- Cache hit/miss rates
- Error rates by source
- Database query times
- API quota usage

## Testing Strategy

### Unit Tests
- Test individual services
- Mock external APIs
- Test validators and helpers

### Integration Tests
- Test service interactions
- Use test database
- Test caching layer

### End-to-End Tests
- Test full API flows
- Verify database persistence
- Test error handling

## Deployment

### Local Deployment
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker Deployment
```bash
docker-compose up -d
```

### Production Considerations
- Use Gunicorn/Uvicorn
- Enable HTTPS/SSL
- Set DEBUG=False
- Configure proper logging
- Set up monitoring
- Use strong database passwords
- Implement authentication
- Set up API key rotation

## Maintenance Tasks

### Daily
- Monitor error logs
- Check API quotas
- Verify database connectivity

### Weekly
- Clean up expired cache entries
- Review performance metrics
- Check for API updates

### Monthly
- Rotate API keys
- Review and optimize queries
- Update dependencies
- Backup database

## Future Enhancements

### Short Term
- Add filtering/sorting
- Implement pagination
- Add product image gallery
- Implement trending products

### Medium Term
- WebSocket support
- GraphQL endpoint
- User accounts
- Review filtering

### Long Term
- ML-based recommendations
- Price tracking
- Competitor analysis
- Mobile app

---

**Last Updated**: November 2025
