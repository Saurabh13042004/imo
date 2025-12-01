# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Setup Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
- `RAPIDAPI_KEY` - Get from [RapidAPI Hub](https://rapidapi.com)
- `GEMINI_API_KEY` - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- `YOUTUBE_API_KEY` - Get from [Google Cloud Console](https://console.cloud.google.com)
- `REDDIT_CLIENT_ID` & `REDDIT_CLIENT_SECRET` - Get from [Reddit App Settings](https://www.reddit.com/prefs/apps)

### Step 3: Setup Database

For **local PostgreSQL**:
```bash
# Create database
createdb product_aggregator

# Run migrations
alembic upgrade head
```

For **Docker**:
```bash
docker-compose up -d postgres
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE product_aggregator"
alembic upgrade head
```

### Step 4: Start Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at: **http://localhost:8000**

### Step 5: Test API

Visit **http://localhost:8000/docs** for interactive API documentation

Try the search endpoint:
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "dyson vacuum",
    "sources": ["amazon"],
    "limit": 10
  }'
```

## 🐳 Using Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## 📚 API Examples

### Search Products
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "laptop",
    "sources": ["amazon", "walmart"],
    "limit": 20,
    "min_rating": 4.0,
    "max_price": 1500
  }'
```

### Get Product Details
```bash
curl "http://localhost:8000/api/v1/product/YOUR_PRODUCT_ID"
```

### Fetch Reviews
```bash
curl -X POST "http://localhost:8000/api/v1/product/YOUR_PRODUCT_ID/reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["amazon", "reddit"],
    "force_refresh": false
  }'
```

### Fetch Videos
```bash
curl -X POST "http://localhost:8000/api/v1/product/YOUR_PRODUCT_ID/videos" \
  -H "Content-Type: application/json" \
  -d '{
    "force_refresh": false,
    "min_views": 1000
  }'
```

## 🔧 Development

### Run Tests
```bash
pytest
pytest --cov=app
```

### Format Code
```bash
black app/
```

### Lint Code
```bash
flake8 app/
```

### Type Checking
```bash
mypy app/
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📝 Common Issues

### Database Connection Error
```
Check DATABASE_URL in .env
Ensure PostgreSQL is running
```

### API Key Errors
```
Verify API keys in .env
Check API key permissions
Enable required APIs (Google Cloud, etc.)
```

### Port Already in Use
```bash
# Change port in command or .env
uvicorn app.main:app --port 8001
```

## 📖 Documentation

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **README**: See README.md
- **Architecture**: Check project structure in README.md

## 🆘 Need Help?

1. Check logs: `docker-compose logs api`
2. Review `.env.example` for required variables
3. Verify API keys are correct
4. Check database connection
5. Review error response details

## 🎯 Next Steps

- [ ] Add your API keys to `.env`
- [ ] Test search functionality
- [ ] Configure cache settings
- [ ] Set up monitoring
- [ ] Deploy to production
- [ ] Add authentication
- [ ] Set up CI/CD pipeline

---

**Tip**: Start with searching a single source (e.g., just "amazon") to verify basic functionality works before adding more sources.
