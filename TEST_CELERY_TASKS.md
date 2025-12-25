# Testing Celery Async Tasks

## Quick Test Commands

### 1. Submit Community Reviews Task
```bash
curl -X POST http://localhost:8000/api/v1/reviews/community \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "iPhone 15 Pro",
    "brand": "Apple"
  }'
```

Response:
```json
{
  "success": true,
  "task_id": "abc-123-def-456",
  "status": "PENDING",
  "message": "Task has been queued for processing. Use task_id to poll results.",
  "polling_endpoint": "/api/v1/reviews/community/status/abc-123-def-456"
}
```

### 2. Check Task Status
```bash
curl http://localhost:8000/api/v1/reviews/community/status/abc-123-def-456
```

Response (processing):
```json
{
  "task_id": "abc-123-def-456",
  "status": "STARTED",
  "ready": false,
  "successful": null,
  "message": "Task is started"
}
```

Response (complete):
```json
{
  "task_id": "abc-123-def-456",
  "status": "SUCCESS",
  "ready": true,
  "successful": true,
  "message": "Task completed successfully",
  "result": {
    "success": true,
    "product_name": "iPhone 15 Pro",
    "source": "community",
    "summary": {
      "overall_sentiment": "positive",
      "common_praises": ["Camera quality", "Performance"],
      "common_complaints": ["Battery life"]
    },
    "reviews": [...],
    "total_found": 42,
    "raw_count": 127
  }
}
```

### 3. Submit Store Reviews Task
```bash
curl -X POST http://localhost:8000/api/v1/reviews/store \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Samsung TV",
    "store_urls": [
      "https://www.amazon.com/Samsung-TV/...",
      "https://www.flipkart.com/Samsung-TV/...",
      "https://www.croma.com/Samsung-TV/..."
    ]
  }'
```

### 4. Submit Google Shopping Task
```bash
curl -X POST http://localhost:8000/api/v1/reviews/google \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Samsung TV",
    "google_shopping_url": "https://www.google.com/shopping/..."
  }'
```

## Python Test Script

```python
import requests
import time
import json

BASE_URL = "http://localhost:8000/api/v1"

def submit_community_reviews(product_name, brand=""):
    """Submit community reviews task"""
    response = requests.post(
        f"{BASE_URL}/reviews/community",
        json={"product_name": product_name, "brand": brand}
    )
    return response.json()

def check_task_status(task_id, task_type="community"):
    """Check task status"""
    response = requests.get(
        f"{BASE_URL}/reviews/{task_type}/status/{task_id}"
    )
    return response.json()

def wait_for_results(task_id, task_type="community", max_wait_seconds=300):
    """Poll until task completes"""
    start_time = time.time()
    poll_interval = 2  # seconds
    
    while time.time() - start_time < max_wait_seconds:
        status = check_task_status(task_id, task_type)
        print(f"Task status: {status['status']}")
        
        if status['status'] == 'SUCCESS':
            return status['result']
        elif status['status'] == 'FAILURE':
            raise Exception(f"Task failed: {status.get('error', 'Unknown error')}")
        
        time.sleep(poll_interval)
    
    raise TimeoutError("Task did not complete within timeout")

# Main test
if __name__ == "__main__":
    print("Submitting community reviews task...")
    task_data = submit_community_reviews("iPhone 15 Pro", "Apple")
    task_id = task_data['task_id']
    print(f"Task submitted with ID: {task_id}")
    print(f"Status: {task_data['status']}")
    
    print("\nWaiting for results...")
    try:
        results = wait_for_results(task_id)
        print(f"\n✅ Task completed!")
        print(f"Product: {results['product_name']}")
        print(f"Source: {results['source']}")
        print(f"Total reviews found: {results['total_found']}")
        print(f"Overall sentiment: {results['summary']['overall_sentiment']}")
        print(f"\nReviews sample:")
        for i, review in enumerate(results['reviews'][:3], 1):
            print(f"  {i}. {review['text'][:100]}...")
    except TimeoutError:
        print("❌ Task timeout")
    except Exception as e:
        print(f"❌ Error: {e}")
```

## JavaScript Test

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

async function submitCommunityReviews(productName, brand = "") {
  const response = await fetch(`${BASE_URL}/reviews/community`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_name: productName, brand })
  });
  return response.json();
}

async function checkTaskStatus(taskId, taskType = "community") {
  const response = await fetch(`${BASE_URL}/reviews/${taskType}/status/${taskId}`);
  return response.json();
}

async function waitForResults(taskId, taskType = "community", maxWaitMs = 300000) {
  const startTime = Date.now();
  const pollInterval = 2000; // 2 seconds
  
  while (Date.now() - startTime < maxWaitMs) {
    const status = await checkTaskStatus(taskId, taskType);
    console.log(`Task status: ${status.status}`);
    
    if (status.status === 'SUCCESS') {
      return status.result;
    } else if (status.status === 'FAILURE') {
      throw new Error(`Task failed: ${status.error || 'Unknown error'}`);
    }
    
    await new Promise(resolve => setTimeout(resolve, pollInterval));
  }
  
  throw new Error('Task timeout');
}

// Main test
(async () => {
  try {
    console.log("Submitting community reviews task...");
    const taskData = await submitCommunityReviews("iPhone 15 Pro", "Apple");
    const taskId = taskData.task_id;
    console.log(`Task submitted with ID: ${taskId}`);
    console.log(`Status: ${taskData.status}`);
    
    console.log("\nWaiting for results...");
    const results = await waitForResults(taskId);
    
    console.log("\n✅ Task completed!");
    console.log(`Product: ${results.product_name}`);
    console.log(`Source: ${results.source}`);
    console.log(`Total reviews found: ${results.total_found}`);
    console.log(`Overall sentiment: ${results.summary.overall_sentiment}`);
    console.log("\nReviews sample:");
    results.reviews.slice(0, 3).forEach((review, i) => {
      console.log(`  ${i + 1}. ${review.text.substring(0, 100)}...`);
    });
  } catch (error) {
    console.error(`❌ Error: ${error.message}`);
  }
})();
```

## React Hook for Task Polling

```javascript
import { useState, useEffect, useCallback } from 'react';

function useTaskPolling(taskId, taskType = 'community') {
  const [status, setStatus] = useState('PENDING');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const checkStatus = useCallback(async () => {
    try {
      const response = await fetch(
        `/api/v1/reviews/${taskType}/status/${taskId}`
      );
      const data = await response.json();
      
      setStatus(data.status);
      
      if (data.status === 'SUCCESS') {
        setResult(data.result);
        setIsLoading(false);
      } else if (data.status === 'FAILURE') {
        setError(data.error);
        setIsLoading(false);
      }
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    }
  }, [taskId, taskType]);
  
  useEffect(() => {
    checkStatus();
    
    if (status !== 'SUCCESS' && status !== 'FAILURE') {
      const interval = setInterval(checkStatus, 2000);
      return () => clearInterval(interval);
    }
  }, [status, checkStatus]);
  
  return { status, result, error, isLoading };
}

// Usage in component
function ReviewsComponent() {
  const [taskId, setTaskId] = useState(null);
  
  const submitTask = async (productName) => {
    const res = await fetch('/api/v1/reviews/community', {
      method: 'POST',
      body: JSON.stringify({ product_name: productName })
    });
    const data = await res.json();
    setTaskId(data.task_id);
  };
  
  const { status, result, error, isLoading } = useTaskPolling(taskId);
  
  if (!taskId) {
    return (
      <button onClick={() => submitTask('iPhone 15 Pro')}>
        Get Reviews
      </button>
    );
  }
  
  if (isLoading) {
    return <div>Loading... ({status})</div>;
  }
  
  if (error) {
    return <div>Error: {error}</div>;
  }
  
  return (
    <div>
      <h2>{result?.product_name}</h2>
      <p>Found: {result?.total_found} reviews</p>
      <p>Sentiment: {result?.summary?.overall_sentiment}</p>
      {/* Display reviews... */}
    </div>
  );
}

export default ReviewsComponent;
```

## Monitoring with Flower

### Via Browser
Open: `http://localhost:5555`

### Via CLI
```bash
cd backend

# View active tasks
celery -A app.celery_app inspect active

# View worker stats
celery -A app.celery_app inspect stats

# View all registered tasks
celery -A app.celery_app inspect registered

# Revoke a task
celery -A app.celery_app revoke abc-123-def-456
```

## Troubleshooting

### Task not executing
1. Check worker is running: `docker-compose ps celery_worker`
2. Check worker logs: `docker-compose logs celery_worker`
3. Verify Redis connection: `redis-cli ping`

### Task timeout
1. Check task time limits in `app/celery_app.py`
2. Increase if needed: `task_time_limit = 3600  # 1 hour`
3. Restart worker

### Results not found
1. Results expire after 1 hour (configurable)
2. Check Redis: `redis-cli get celery-task-meta-{task_id}`
3. Increase expiration: `result_expires = 7200  # 2 hours`

### High memory usage
1. Reduce worker concurrency in docker-compose.yml
2. Lower `worker_max_tasks_per_child` in celery_app.py
3. Monitor with: `docker stats`
