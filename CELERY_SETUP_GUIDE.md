# Celery Async Task Processing Setup

This document explains the Celery setup for asynchronous processing of review APIs to prevent blocking of other API requests.

## Overview

The three review endpoints that were previously blocking are now asynchronous:
- `POST /reviews/community` - Community reviews from Reddit and forums
- `POST /reviews/store` - Store reviews from retailer websites
- `POST /reviews/google` - Google Shopping reviews

## Architecture

```
FastAPI API
    ↓
Celery Task Queue (Redis)
    ↓
Celery Worker (processes tasks)
    ↓
Results stored in Redis
    ↓
Client polls /reviews/{type}/status/{task_id}
```

## Components

### 1. **Redis** (Message Broker & Result Backend)
- Stores task messages and results
- Enables communication between API and workers
- Default: `redis://localhost:6379/0`

### 2. **FastAPI API**
- Accepts review requests
- Queues tasks immediately
- Returns `task_id` and polling endpoint
- Remains responsive for all other requests

### 3. **Celery Worker**
- Processes review tasks in background
- Can run multiple workers for parallel processing
- Automatically retries failed tasks
- Includes timeouts to prevent hanging

### 4. **Flower** (Optional - Monitoring)
- Web-based Celery monitoring dashboard
- Access at `http://localhost:5555`
- Shows task status, worker stats, and logs

### 5. **Celery Beat** (Optional - Scheduled Tasks)
- Handles periodic background jobs
- Currently configured but with no active schedule

## Setup & Installation

### Prerequisites
- Redis server running
- Python 3.11+
- Dependencies in `requirements.txt` (already includes celery==5.3.4)

### Quick Start with Docker Compose

```bash
cd backend

# Start all services (API, Redis, Celery Worker, Flower, Celery Beat)
docker-compose up -d

# View logs
docker-compose logs -f celery_worker
docker-compose logs -f api
docker-compose logs -f flower

# Stop services
docker-compose down
```

### Manual Setup (Development)

1. **Start Redis**:
   ```bash
   # Windows (if Redis installed locally)
   redis-server
   
   # or Docker
   docker run -d -p 6379:6379 redis:7-alpine
   ```

2. **Start Celery Worker**:
   ```bash
   # Windows
   cd backend
   start_celery_worker.bat
   
   # Linux/Mac
   ./start_celery_worker.sh
   ```

3. **Start FastAPI Server** (in another terminal):
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

4. **Optional - Start Flower** (in another terminal):
   ```bash
   cd backend
   celery -A app.celery_app flower --port=5555
   ```

## API Usage

### Submitting a Task

**Request** (now returns immediately):
```bash
POST /api/v1/reviews/community
Content-Type: application/json

{
  "product_name": "iPhone 15 Pro",
  "brand": "Apple"
}
```

**Response** (immediate):
```json
{
  "success": true,
  "task_id": "a8f4c1b3-7d2a-4e9f-b5c3-2d1a8f4c7b9e",
  "status": "PENDING",
  "message": "Task has been queued for processing. Use task_id to poll results.",
  "polling_endpoint": "/api/v1/reviews/community/status/a8f4c1b3-7d2a-4e9f-b5c3-2d1a8f4c7b9e"
}
```

### Polling for Results

**Poll Status**:
```bash
GET /api/v1/reviews/community/status/{task_id}
```

**Response - Task Processing**:
```json
{
  "task_id": "a8f4c1b3-7d2a-4e9f-b5c3-2d1a8f4c7b9e",
  "status": "STARTED",
  "ready": false,
  "successful": null,
  "message": "Task is started"
}
```

**Response - Task Complete**:
```json
{
  "task_id": "a8f4c1b3-7d2a-4e9f-b5c3-2d1a8f4c7b9e",
  "status": "SUCCESS",
  "ready": true,
  "successful": true,
  "message": "Task completed successfully",
  "result": {
    "success": true,
    "product_name": "iPhone 15 Pro",
    "source": "community",
    "summary": { ... },
    "reviews": [ ... ],
    "total_found": 45,
    "raw_count": 127
  }
}
```

**Response - Task Failed**:
```json
{
  "task_id": "a8f4c1b3-7d2a-4e9f-b5c3-2d1a8f4c7b9e",
  "status": "FAILURE",
  "ready": true,
  "successful": false,
  "message": "Task failed",
  "error": "Failed to fetch community reviews: Network timeout"
}
```

## Task Endpoints

### Community Reviews
- **Queue Task**: `POST /api/v1/reviews/community`
- **Check Status**: `GET /api/v1/reviews/community/status/{task_id}`

### Store Reviews
- **Queue Task**: `POST /api/v1/reviews/store`
- **Check Status**: `GET /api/v1/reviews/store/status/{task_id}`

### Google Shopping Reviews
- **Queue Task**: `POST /api/v1/reviews/google`
- **Check Status**: `GET /api/v1/reviews/google/status/{task_id}`

### Generic Status Endpoint
- **Check Any Task**: `GET /api/v1/reviews/status/{task_id}`

## Client Implementation Example

### JavaScript/React
```javascript
// 1. Submit task
const submitReviewTask = async (productName) => {
  const response = await fetch('/api/v1/reviews/community', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_name: productName })
  });
  return response.json();
};

// 2. Poll for results
const pollTaskStatus = async (taskId, maxWaitMs = 300000) => {
  const startTime = Date.now();
  const pollInterval = 2000; // 2 seconds
  
  while (Date.now() - startTime < maxWaitMs) {
    const response = await fetch(`/api/v1/reviews/community/status/${taskId}`);
    const data = await response.json();
    
    if (data.status === 'SUCCESS') {
      return data.result;
    } else if (data.status === 'FAILURE') {
      throw new Error(data.error);
    }
    
    // Wait before polling again
    await new Promise(resolve => setTimeout(resolve, pollInterval));
  }
  
  throw new Error('Task timeout');
};

// 3. Usage
const taskData = await submitReviewTask('iPhone 15 Pro');
const results = await pollTaskStatus(taskData.task_id);
console.log('Reviews:', results);
```

### Python
```python
import requests
import time

def submit_review_task(product_name):
    response = requests.post(
        'http://localhost:8000/api/v1/reviews/community',
        json={'product_name': product_name}
    )
    return response.json()

def poll_task_status(task_id, max_wait_seconds=300):
    start_time = time.time()
    poll_interval = 2  # seconds
    
    while time.time() - start_time < max_wait_seconds:
        response = requests.get(
            f'http://localhost:8000/api/v1/reviews/community/status/{task_id}'
        )
        data = response.json()
        
        if data['status'] == 'SUCCESS':
            return data['result']
        elif data['status'] == 'FAILURE':
            raise Exception(data['error'])
        
        print(f"Task status: {data['status']}")
        time.sleep(poll_interval)
    
    raise TimeoutError('Task did not complete within timeout period')

# Usage
task = submit_review_task('iPhone 15 Pro')
results = poll_task_status(task['task_id'])
print('Reviews:', results)
```

## Celery Configuration

Located in `app/celery_app.py`:

```python
# Task configuration
task_serializer = "json"
accept_content = ["json"]
result_serializer = "json"
timezone = "UTC"
enable_utc = True

# Task execution
task_track_started = True
task_time_limit = 30 * 60  # 30 minutes hard limit
task_soft_time_limit = 25 * 60  # 25 minutes soft limit

# Worker configuration
worker_prefetch_multiplier = 1  # One task at a time
worker_max_tasks_per_child = 1000

# Result backend
result_expires = 3600  # Results available for 1 hour
```

## Task Configuration

Located in `app/tasks/review_tasks.py`:

- **Community Reviews Task**: Max 3 retries, 60s retry delay
- **Store Reviews Task**: Max 3 retries, 60s retry delay
- **Google Reviews Task**: Max 2 retries, 90s retry delay (takes longer)

Each task runs in its own asyncio event loop to handle async operations.

## Scaling

### Run Multiple Workers
```bash
# Worker 1
celery -A app.celery_app worker --hostname=worker1@%h

# Worker 2 (different terminal)
celery -A app.celery_app worker --hostname=worker2@%h

# Worker 3 (different terminal)
celery -A app.celery_app worker --hostname=worker3@%h
```

### Docker Scaling
```bash
cd backend

# Start 3 workers
docker-compose up -d --scale celery_worker=3

# View all containers
docker-compose ps
```

## Monitoring

### Using Flower Dashboard
Open browser: `http://localhost:5555`

Features:
- Real-time task status
- Worker monitoring
- Task history
- Performance metrics
- Revoke/retry tasks

### Command Line Monitoring
```bash
# Inspect active tasks
celery -A app.celery_app inspect active

# Get worker statistics
celery -A app.celery_app inspect stats

# View task registry
celery -A app.celery_app inspect registered

# Revoke a task
celery -A app.celery_app revoke {task_id}
```

## Troubleshooting

### Task Not Processing
1. Check Redis is running: `redis-cli ping`
2. Check worker logs: `docker-compose logs celery_worker`
3. Verify `REDIS_URL` in `.env`

### Worker Crash
1. Check system resources: `docker stats`
2. Review worker logs for errors
3. Check if task execution timeout is too short

### Results Not Retrieved
1. Check result expiration: Default 1 hour
2. Redis persistence may be disabled
3. Check task_id format is correct

### High Memory Usage
1. Reduce `worker_max_tasks_per_child` to restart worker frequently
2. Monitor with `docker stats`
3. Limit concurrent tasks with `--concurrency`

## Environment Variables

Add to `.env`:
```bash
# Redis configuration
REDIS_URL=redis://localhost:6379/0

# Celery settings
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Task timeouts
CELERY_TASK_TIME_LIMIT=1800  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT=1500  # 25 minutes
```

## Performance Benefits

### Before (Blocking)
- Request blocks until all reviews fetched (~2-5 minutes per request)
- Other API requests delayed or timeout
- Max ~1-2 concurrent review requests

### After (Async)
- Request returns immediately (~100ms)
- Other API requests unaffected
- Process 10+ concurrent review requests
- Parallel processing with multiple workers
- Better user experience with polling

## Files Added/Modified

### New Files
- `app/celery_app.py` - Celery configuration
- `app/tasks/__init__.py` - Tasks package
- `app/tasks/review_tasks.py` - Review task implementations
- `backend/Dockerfile.celery` - Celery Docker image
- `start_celery_worker.sh` - Linux/Mac startup script
- `start_celery_worker.bat` - Windows startup script

### Modified Files
- `backend/docker-compose.yml` - Added Celery services
- `backend/app/api/routes/reviews.py` - Updated endpoints to use Celery
- `requirements.txt` - Already has celery==5.3.4

## Next Steps

1. Update frontend to poll for results instead of waiting for blocking requests
2. Add WebSocket support for real-time task updates (optional)
3. Implement result caching to avoid re-processing same requests
4. Add task priority levels for VIP users
5. Monitor performance and adjust concurrency/timeouts as needed
