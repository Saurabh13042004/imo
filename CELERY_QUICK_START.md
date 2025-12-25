# Celery Quick Reference

## Start Everything with Docker (Recommended)

```bash
cd backend
docker-compose up -d
```

This starts:
- ✅ Redis (port 6379)
- ✅ FastAPI API (port 8000)
- ✅ Celery Worker (processes tasks)
- ✅ Celery Beat (optional scheduling)
- ✅ Flower Dashboard (port 5555)

## Start Services Individually (Development)

### Terminal 1 - Redis
```bash
docker run -d -p 6379:6379 redis:7-alpine
# or on Windows with local Redis: redis-server
```

### Terminal 2 - Celery Worker
```bash
cd backend
# Windows
start_celery_worker.bat
# Linux/Mac
./start_celery_worker.sh
```

### Terminal 3 - FastAPI
```bash
cd backend
uvicorn app.main:app --reload
```

### Terminal 4 - Flower (Optional)
```bash
cd backend
celery -A app.celery_app flower --port=5555
```

## API Usage

### Submit Task (Immediate Response)
```bash
curl -X POST http://localhost:8000/api/v1/reviews/community \
  -H "Content-Type: application/json" \
  -d '{"product_name": "iPhone 15 Pro"}'
```

Response:
```json
{
  "success": true,
  "task_id": "abc-123-def-456",
  "status": "PENDING",
  "polling_endpoint": "/api/v1/reviews/community/status/abc-123-def-456"
}
```

### Check Status
```bash
curl http://localhost:8000/api/v1/reviews/community/status/abc-123-def-456
```

Response:
```json
{
  "task_id": "abc-123-def-456",
  "status": "SUCCESS",
  "ready": true,
  "successful": true,
  "result": { /* review data */ }
}
```

## Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/reviews/community` | Submit community reviews task |
| GET | `/api/v1/reviews/community/status/{task_id}` | Check community task status |
| POST | `/api/v1/reviews/store` | Submit store reviews task |
| GET | `/api/v1/reviews/store/status/{task_id}` | Check store task status |
| POST | `/api/v1/reviews/google` | Submit Google Shopping reviews task |
| GET | `/api/v1/reviews/google/status/{task_id}` | Check Google task status |
| GET | `/api/v1/reviews/status/{task_id}` | Check any task status |

## Task Status Values

| Status | Meaning |
|--------|---------|
| PENDING | Task queued, waiting to be processed |
| STARTED | Worker picked up task, processing now |
| SUCCESS | Task completed, result available |
| FAILURE | Task failed, check error field |
| RETRY | Task is being retried after failure |

## Monitoring

### Flower Dashboard
Open: `http://localhost:5555`

### CLI Commands
```bash
cd backend

# View active tasks
celery -A app.celery_app inspect active

# View worker stats
celery -A app.celery_app inspect stats

# View registered tasks
celery -A app.celery_app inspect registered

# Revoke a task
celery -A app.celery_app revoke {task_id}

# Purge all tasks
celery -A app.celery_app purge
```

## Logs

### Docker
```bash
cd backend

# API logs
docker-compose logs -f api

# Worker logs
docker-compose logs -f celery_worker

# Flower logs
docker-compose logs -f flower

# All logs
docker-compose logs -f
```

### Manual (if running separately)
- Worker logs print to console
- Check terminal where you started `start_celery_worker.bat`

## Scaling Workers

### Docker
```bash
cd backend

# Scale to 3 workers
docker-compose up -d --scale celery_worker=3

# View all services
docker-compose ps

# Scale down to 1
docker-compose up -d --scale celery_worker=1
```

### Manual
```bash
# Terminal 1
celery -A app.celery_app worker --hostname=worker1@%h

# Terminal 2
celery -A app.celery_app worker --hostname=worker2@%h

# Terminal 3
celery -A app.celery_app worker --hostname=worker3@%h
```

## Stop Services

```bash
cd backend

# Stop all Docker services
docker-compose down

# Stop specific service
docker-compose stop celery_worker

# Restart specific service
docker-compose restart celery_worker
```

## Environment Variables (.env)

```bash
# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys
SERPAPI_KEY=your_key
GEMINI_API_KEY=your_key
# ... other keys

# Logging
LOG_LEVEL=INFO
DEBUG=False
```

## Common Issues

### "Connection refused"
- Make sure Redis is running: `docker ps` should show redis container
- Check port 6379 is not blocked

### "Task not executing"
- Check worker is running and connected
- View logs: `docker-compose logs celery_worker`
- Check Redis: `redis-cli ping` should return PONG

### "Results not found"
- Results expire after 1 hour (configurable in `app/celery_app.py`)
- Check task_id is correct format (UUID)

### "Worker crash/OOM"
- Reduce concurrency: Edit `docker-compose.yml` `--concurrency=2`
- Increase server memory
- Check logs for specific errors

## Performance Tuning

### Increase Concurrency (More Parallel Tasks)
Edit `docker-compose.yml`:
```yaml
command: celery -A app.celery_app worker --concurrency=8
```

### Increase Task Timeout
Edit `app/celery_app.py`:
```python
task_time_limit = 60 * 60  # 1 hour
```

### Reduce Result Expiration
Edit `app/celery_app.py`:
```python
result_expires = 7200  # 2 hours
```

## Testing Locally

```bash
# Simple test
curl -X POST http://localhost:8000/api/v1/reviews/community \
  -H "Content-Type: application/json" \
  -d '{"product_name": "test product"}'

# Get task ID from response, then poll
curl http://localhost:8000/api/v1/reviews/community/status/{TASK_ID}
```

## Docker Compose Commands

```bash
cd backend

# Start all services
docker-compose up -d

# View running services
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild images
docker-compose build

# Remove volumes (careful - deletes data)
docker-compose down -v
```

## Documentation

Full documentation: See `CELERY_SETUP_GUIDE.md`

Code files:
- Configuration: `app/celery_app.py`
- Tasks: `app/tasks/review_tasks.py`
- Routes: `app/api/routes/reviews.py`
