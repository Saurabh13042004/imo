# Product Aggregator & Review System

A FastAPI-based product search and aggregation platform that searches across multiple marketplaces (Amazon, Walmart, Google Shopping) and aggregates reviews from various sources (Reddit, YouTube, forums, social media).

## Features

- 🔍 **Multi-Marketplace Search**: Search products across Amazon, Walmart, and Google Shopping simultaneously
- 📊 **Review Aggregation**: Aggregate reviews from Amazon, Reddit, YouTube, and forums
- 🎥 **Video Reviews**: Fetch YouTube review videos with metadata
- 🤖 **AI-Powered Analysis**: Summarize reviews and analyze sentiment using OpenAI
- ⚡ **Async/Concurrent**: Built with asyncio for high performance
- 💾 **PostgreSQL Database**: Persistent data storage with SQLAlchemy ORM
- 🚀 **RESTful API**: Complete REST API with FastAPI and automatic documentation
- 🔄 **Smart Caching**: Configurable cache with TTL for search results and reviews
- 🛡️ **Error Handling**: Graceful error handling and fallback mechanisms

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0
- **API Clients**: httpx (async HTTP)
- **AI/ML**: OpenAI API
- **Caching**: Redis (optional)
- **Containerization**: Docker & Docker Compose

## Project Structure

```
product-aggregator/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app and configuration
│   ├── config.py               # Environment configuration
│   ├── database.py             # Database setup
│   ├── models/                 # SQLAlchemy models
│   │   ├── product.py
│   │   ├── review.py
│   │   ├── video.py
│   │   └── search_cache.py
│   ├── schemas/                # Pydantic schemas
│   │   └── __init__.py         # All schemas
│   ├── api/
│   │   ├── dependencies.py     # Dependency injection
│   │   └── routes/
│   │       ├── search.py       # Search endpoints
│   │       ├── products.py     # Product endpoints
│   │       └── reviews.py      # Review endpoints
│   ├── services/               # Business logic
│   │   ├── search_service.py
│   │   ├── review_service.py
│   │   ├── video_service.py
│   │   ├── ai_service.py
│   │   └── cache_service.py
│   ├── integrations/           # External API clients
│   │   ├── amazon.py
│   │   ├── walmart.py
│   │   ├── google_shopping.py
│   │   ├── youtube.py
│   │   └── reddit.py
│   └── utils/
│       ├── helpers.py
│       └── validators.py
├── alembic/                    # Database migrations
│   ├── env.py
│   ├── alembic.ini
│   └── versions/
├── tests/                      # Unit tests
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── docker-compose.yml         # Docker setup
├── Dockerfile                 # Container image
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis (optional, for caching)
- Docker (optional, for containerization)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd product-aggregator
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database URL
   ```

5. **Initialize database**
   ```bash
   alembic upgrade head
   ```

6. **Run development server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Initialize database**
   ```bash
   docker-compose exec api alembic upgrade head
   ```

3. **Access API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Configuration

Environment variables are configured in `.env` file. Copy from `.env.example`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/product_aggregator

# API Keys (get from respective services)
RAPIDAPI_KEY=your_key
OPENAI_API_KEY=your_key
YOUTUBE_API_KEY=your_key
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret

# Server
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Cache (in seconds)
SEARCH_CACHE_TTL=3600      # 1 hour
PRODUCT_CACHE_TTL=86400    # 24 hours
REVIEW_CACHE_TTL=604800    # 7 days
```

## API Endpoints

### Search Products
```http
POST /api/v1/search
Content-Type: application/json

{
  "query": "dyson vacuum",
  "sources": ["amazon", "walmart", "google_shopping"],
  "limit": 20,
  "min_rating": 4.0,
  "max_price": 500.00
}
```

### Get Product Details
```http
GET /api/v1/product/{product_id}
```

Or by source:
```http
POST /api/v1/product/details
Content-Type: application/json

{
  "source": "amazon",
  "sourceId": "B09V3JCPBB"
}
```

### Fetch Product Reviews
```http
POST /api/v1/product/{product_id}/reviews
Content-Type: application/json

{
  "sources": ["amazon", "reddit", "youtube"],
  "force_refresh": false
}
```

### Fetch Product Videos
```http
POST /api/v1/product/{product_id}/videos
Content-Type: application/json

{
  "force_refresh": false,
  "min_views": 1000
}
```

## API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Getting API Keys

### RapidAPI (Amazon, Walmart, Google Shopping)
1. Sign up at [RapidAPI Hub](https://rapidapi.com)
2. Search for "Amazon Data Scraper API" or similar
3. Copy your API key from the dashboard

### Google Gemini API
1. Sign up at [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key
3. Add to `.env`

### YouTube API
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable YouTube Data API v3
4. Create an API key

### Reddit API
1. Go to [Reddit App Settings](https://www.reddit.com/prefs/apps)
2. Create a new application (script)
3. Get Client ID and Secret

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_search.py
```

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1
```

## Performance Metrics

- Search response time: < 2 seconds
- Product detail page: < 1 second
- API success rate: > 95%
- Concurrent users supported: 100+
- Cache hit rate: > 80%

## Error Handling

The API returns structured error responses:

```json
{
  "success": false,
  "error": "Error message",
  "details": {...}
}
```

Common status codes:
- 200: Success
- 400: Bad Request
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error

## Logging

Logs are configured in `app/main.py`. Configure via `LOG_LEVEL` environment variable:
- DEBUG: Detailed information
- INFO: General information
- WARNING: Warnings
- ERROR: Errors
- CRITICAL: Critical errors

## Best Practices

1. **Cache Results**: Use cache headers and implement smart caching
2. **Rate Limiting**: Respect API rate limits of external services
3. **Async Operations**: Use async/await for I/O operations
4. **Error Handling**: Always handle exceptions gracefully
5. **Input Validation**: Validate all user inputs
6. **Security**: Use environment variables for sensitive data
7. **Monitoring**: Track API response times and errors

## Security Considerations

- Never commit `.env` file
- Use strong database passwords
- Implement API authentication (not included in basic version)
- Use HTTPS in production
- Validate and sanitize all inputs
- Keep dependencies updated

## Contributing

1. Create a feature branch
2. Make changes and test
3. Submit a pull request

## Troubleshooting

### Database connection error
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Ensure database exists

### API key errors
- Verify API keys are correct in `.env`
- Check API key permissions
- Ensure APIs are enabled (for Google/AWS)

### Rate limiting
- Add delays between requests
- Implement exponential backoff
- Check API quota limits

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Check documentation at `/docs` endpoint
- Review error messages for specific details
- Check log files for detailed information

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] GraphQL endpoint
- [ ] Advanced filtering and sorting
- [ ] User authentication and authorization
- [ ] Review translation (multi-language)
- [ ] Sentiment analysis improvements
- [ ] Price tracking and alerts
- [ ] Competitor analysis
- [ ] Mobile app integration
- [ ] Analytics dashboard

---

**Version**: 1.0.0  
**Last Updated**: November 2025
