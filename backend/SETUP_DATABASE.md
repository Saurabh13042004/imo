# Database Schema Setup Script

This script safely creates all database tables and indexes. It's **idempotent** - safe to run multiple times without errors.

## Features

✅ Creates missing tables
✅ Skips existing tables (no errors)
✅ Creates indexes for performance
✅ Handles foreign key constraints
✅ All tables have proper defaults and constraints

## Usage

### Run Standalone

```bash
cd backend
python setup_database_schema.py
```

### Run from Python

```python
import asyncio
from setup_database_schema import SchemaManager
from app.config import settings

async def setup():
    manager = SchemaManager(settings.DATABASE_URL)
    await manager.setup_schema()
    await manager.close()

asyncio.run(setup())
```

### Run on Docker Container

```bash
docker compose exec imo_api python setup_database_schema.py
```

## Tables Created

1. **profiles** - User accounts and authentication
2. **subscriptions** - User subscription plans
3. **payment_transactions** - Payment history
4. **products** - Product information
5. **reviews** - Product reviews from external sources
6. **user_reviews** - User-submitted reviews
7. **product_reviews** - Individual product reviews
8. **price_alerts** - Price tracking alerts
9. **price_comparisons** - Price comparison data
10. **search_unlocks** - Search query unlocks
11. **analytics_events** - User analytics
12. **user_interactions** - User interaction tracking
13. **subscription_events** - Subscription event logs
14. **affiliate_clicks** - Affiliate tracking
15. **error_logs** - Error logging
16. **usage_logs** - Usage tracking
17. **videos** - YouTube videos
18. **short_video_reviews** - TikTok/Instagram reviews
19. **likes** - Review likes
20. **comments** - Review comments
21. **product_likes** - Product likes
22. **user_roles** - User role assignments
23. **search_cache** - Search results cache
24. **contacts** - Contact form submissions
25. **app_config** - Application configuration
26. **background_analysis_tasks** - Background job tracking
27. **daily_search_usage** - Daily search usage stats
28. **ai_verdicts** - AI product analysis results

## Safe to Run

- ✅ Won't drop existing tables
- ✅ Won't lose data
- ✅ Can be run multiple times
- ✅ Handles missing dependencies gracefully
- ✅ Provides clear success/warning messages

## Logging

The script provides detailed logging:
- `✓` = Successfully created/exists
- `⚠` = Warning (e.g., constraint already exists)
- `ERROR` = Critical issue that needs attention

## Database Requirements

- PostgreSQL 12+
- Async-compatible connection
- Proper environment variables configured

## Integration

This script is automatically called in `app/database.py` during application startup via `init_db()`.
