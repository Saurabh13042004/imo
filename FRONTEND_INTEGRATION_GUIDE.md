# Frontend Integration Guide - Async Review Tasks

## Overview

Your review API endpoints now return immediately with a `task_id`. The frontend must poll for results instead of waiting for a blocking response.

## Response Format

### Initial Response (Immediate - ~100ms)
```json
{
  "success": true,
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "PENDING",
  "message": "Task has been queued for processing",
  "polling_endpoint": "/api/v1/reviews/community/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### Polling Response - Task In Progress
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "STARTED",
  "ready": false,
  "successful": null,
  "message": "Task is started"
}
```

### Polling Response - Task Complete
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "SUCCESS",
  "ready": true,
  "successful": true,
  "message": "Task completed successfully",
  "result": {
    "success": true,
    "product_name": "Samsung TV",
    "source": "community",
    "summary": { ... },
    "reviews": [ ... ],
    "total_found": 45
  }
}
```

### Polling Response - Task Failed
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "FAILURE",
  "ready": true,
  "successful": false,
  "message": "Task failed",
  "error": "Network timeout while fetching reviews"
}
```

## Task Status Values

| Status | Meaning | Action |
|--------|---------|--------|
| PENDING | Task queued, waiting | Keep polling |
| STARTED | Task is processing | Keep polling |
| SUCCESS | Task completed | Display results |
| FAILURE | Task failed | Show error |
| RETRY | Task being retried | Keep polling |

## Polling Timeline

- **Community Reviews**: 30-40 seconds
- **Store Reviews**: 10-15 seconds
- **Google Shopping Reviews**: 50-60 seconds

## Implementation Examples

### React Hook
```javascript
import { useState, useEffect } from 'react';

export function useReviewTask() {
  const [taskId, setTaskId] = useState(null);
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Poll for task status
  useEffect(() => {
    if (!taskId) return;

    const poll = async () => {
      try {
        const response = await fetch(
          `/api/v1/reviews/community/status/${taskId}`
        );
        const data = await response.json();
        
        setStatus(data.status);

        if (data.status === 'SUCCESS') {
          setResult(data.result);
          setIsLoading(false);
        } else if (data.status === 'FAILURE') {
          setError(data.error);
          setIsLoading(false);
        } else {
          // Continue polling
          setTimeout(poll, 2000);
        }
      } catch (err) {
        setError(err.message);
        setIsLoading(false);
      }
    };

    const timer = setTimeout(poll, 1000);
    return () => clearTimeout(timer);
  }, [taskId, status]);

  const submitTask = async (productName, brand = '') => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('/api/v1/reviews/community', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_name: productName, brand })
      });

      const data = await response.json();
      
      if (data.task_id) {
        setTaskId(data.task_id);
      } else {
        setError(data.detail);
        setIsLoading(false);
      }
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    }
  };

  return { submitTask, status, result, error, isLoading, taskId };
}

// Usage in component
function ReviewSection() {
  const { submitTask, status, result, error, isLoading } = useReviewTask();

  return (
    <div>
      <button onClick={() => submitTask('iPhone 15 Pro')}>
        Get Reviews
      </button>

      {isLoading && <p>Loading reviews... ({status})</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      
      {result && (
        <div>
          <h3>{result.product_name}</h3>
          <p>Found {result.total_found} reviews</p>
          {result.reviews.map((review, i) => (
            <div key={i}>
              <strong>{review.title}</strong>
              <p>{review.text}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Vue 3 Composition API
```javascript
import { ref, watch, computed } from 'vue';

export function useReviewTask() {
  const taskId = ref(null);
  const status = ref(null);
  const result = ref(null);
  const error = ref(null);
  const isLoading = ref(false);

  const statusMessage = computed(() => {
    switch (status.value) {
      case 'PENDING': return '⏳ Waiting to start...';
      case 'STARTED': return '🔄 Processing...';
      case 'SUCCESS': return '✅ Complete!';
      case 'FAILURE': return '❌ Failed';
      default: return 'Not started';
    }
  });

  // Poll for results
  watch(taskId, async (newTaskId) => {
    if (!newTaskId) return;

    const poll = async () => {
      try {
        const response = await fetch(
          `/api/v1/reviews/community/status/${newTaskId}`
        );
        const data = await response.json();
        
        status.value = data.status;

        if (data.status === 'SUCCESS') {
          result.value = data.result;
          isLoading.value = false;
        } else if (data.status === 'FAILURE') {
          error.value = data.error;
          isLoading.value = false;
        } else {
          // Continue polling
          setTimeout(poll, 2000);
        }
      } catch (err) {
        error.value = err.message;
        isLoading.value = false;
      }
    };

    setTimeout(poll, 1000);
  });

  const submitTask = async (productName, brand = '') => {
    isLoading.value = true;
    error.value = null;
    result.value = null;

    try {
      const response = await fetch('/api/v1/reviews/community', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_name: productName, brand })
      });

      const data = await response.json();
      
      if (data.task_id) {
        taskId.value = data.task_id;
      } else {
        error.value = data.detail;
        isLoading.value = false;
      }
    } catch (err) {
      error.value = err.message;
      isLoading.value = false;
    }
  };

  return { 
    submitTask, 
    status, 
    result, 
    error, 
    isLoading, 
    taskId,
    statusMessage
  };
}
```

### JavaScript (Vanilla)
```javascript
class ReviewTaskPoller {
  constructor(apiBase = '/api/v1') {
    this.apiBase = apiBase;
    this.tasks = {};
  }

  async submitReviewTask(type, payload) {
    try {
      const response = await fetch(`${this.apiBase}/reviews/${type}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      
      if (data.task_id) {
        this.tasks[data.task_id] = {
          type,
          status: 'PENDING',
          result: null
        };
        this.poll(data.task_id);
        return data.task_id;
      } else {
        throw new Error(data.detail);
      }
    } catch (error) {
      console.error('Failed to submit task:', error);
      throw error;
    }
  }

  poll(taskId, onUpdate) {
    const task = this.tasks[taskId];
    if (!task) return;

    fetch(`${this.apiBase}/reviews/status/${taskId}`)
      .then(r => r.json())
      .then(data => {
        task.status = data.status;

        if (onUpdate) {
          onUpdate(data);
        }

        if (data.status === 'SUCCESS') {
          task.result = data.result;
          console.log('Task completed:', data.result);
        } else if (data.status === 'FAILURE') {
          console.error('Task failed:', data.error);
        } else {
          // Continue polling in 2 seconds
          setTimeout(() => this.poll(taskId, onUpdate), 2000);
        }
      })
      .catch(error => {
        console.error('Polling error:', error);
        setTimeout(() => this.poll(taskId, onUpdate), 5000);
      });
  }
}

// Usage
const poller = new ReviewTaskPoller('/api/v1');

const taskId = await poller.submitReviewTask('community', {
  product_name: 'iPhone 15 Pro',
  brand: 'Apple'
});

poller.poll(taskId, (status) => {
  console.log('Status update:', status.status);
  if (status.status === 'SUCCESS') {
    console.log('Reviews:', status.result.reviews);
  }
});
```

### Angular Service
```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, interval, Observable } from 'rxjs';
import { switchMap, takeUntil, tap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class ReviewTaskService {
  private apiBase = '/api/v1';
  private taskStatus$ = new BehaviorSubject(null);

  constructor(private http: HttpClient) {}

  submitReviewTask(type: string, payload: any): Observable<any> {
    return this.http.post(`${this.apiBase}/reviews/${type}`, payload)
      .pipe(
        tap(data => {
          if (data.task_id) {
            this.pollTask(data.task_id);
          }
        })
      );
  }

  private pollTask(taskId: string): void {
    interval(2000)
      .pipe(
        switchMap(() => 
          this.http.get(`${this.apiBase}/reviews/status/${taskId}`)
        ),
        tap(data => {
          this.taskStatus$.next(data);
          
          if (data.status === 'SUCCESS' || data.status === 'FAILURE') {
            // Stop polling
          }
        }),
        takeUntil(
          this.taskStatus$.pipe(
            // Continue until completion
          )
        )
      )
      .subscribe();
  }

  getTaskStatus(): Observable<any> {
    return this.taskStatus$.asObservable();
  }
}

// Usage in component
export class ReviewComponent implements OnInit {
  taskStatus$ = this.reviewService.getTaskStatus();

  constructor(private reviewService: ReviewTaskService) {}

  submitReview() {
    this.reviewService.submitReviewTask('community', {
      product_name: 'iPhone 15 Pro',
      brand: 'Apple'
    }).subscribe();
  }
}
```

## Error Handling

```javascript
async function getReviewsWithErrorHandling(productName) {
  try {
    // Step 1: Submit task
    const submitResponse = await fetch('/api/v1/reviews/community', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_name: productName })
    });

    if (!submitResponse.ok) {
      throw new Error(`HTTP ${submitResponse.status}`);
    }

    const { task_id } = await submitResponse.json();

    // Step 2: Poll with timeout
    const maxWaitTime = 120000; // 2 minutes
    const pollInterval = 2000;
    const startTime = Date.now();

    while (Date.now() - startTime < maxWaitTime) {
      const statusResponse = await fetch(
        `/api/v1/reviews/community/status/${task_id}`
      );

      if (!statusResponse.ok) {
        throw new Error(`HTTP ${statusResponse.status}`);
      }

      const status = await statusResponse.json();

      if (status.status === 'SUCCESS') {
        return status.result;
      } else if (status.status === 'FAILURE') {
        throw new Error(status.error);
      }

      // Wait before next poll
      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }

    throw new Error('Task timeout');
  } catch (error) {
    console.error('Review fetch error:', error);
    // Show user-friendly error message
    return {
      error: true,
      message: error.message
    };
  }
}
```

## Displaying Results

```javascript
function displayReviews(reviewData) {
  if (reviewData.error) {
    return `<div class="error">Error: ${reviewData.message}</div>`;
  }

  return `
    <div class="reviews-container">
      <h2>${reviewData.product_name}</h2>
      
      <div class="summary">
        <p><strong>Total Reviews Found:</strong> ${reviewData.total_found}</p>
        <p><strong>Average Rating:</strong> ${reviewData.summary.average_rating?.toFixed(1) || 'N/A'}</p>
        <p><strong>Overall Sentiment:</strong> ${reviewData.summary.overall_sentiment}</p>
      </div>

      <div class="reviews-list">
        ${reviewData.reviews.map(review => `
          <div class="review-item">
            <div class="review-header">
              <span class="reviewer">${review.reviewer_name || 'Anonymous'}</span>
              <span class="rating">${review.rating ? '⭐'.repeat(review.rating) : 'N/A'}</span>
            </div>
            <p class="review-text">${review.text}</p>
            <small>${review.date || 'Date unknown'}</small>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}
```

## Best Practices

1. **Show loading state** while polling
2. **Set polling timeout** (usually 2-3 minutes max)
3. **Handle network errors** gracefully
4. **Cache results** to avoid re-fetching
5. **Show estimated time** based on task type
6. **Allow cancellation** if needed
7. **Log task IDs** for debugging

## Testing

Use the included `test_celery_polling.html` file:
1. Open in browser: `file:///d:/imo-backend/test_celery_polling.html`
2. Make sure API is running on `localhost:8000`
3. Submit tasks and observe polling behavior
4. Check network tab to see request/response timing

## Troubleshooting

### Task never completes
- Check Celery worker logs: `docker-compose logs celery_worker`
- Check if worker has required dependencies
- Check Redis connection: `docker-compose logs redis`

### CORS errors
- Add origin to FastAPI CORS configuration
- Check `app/main.py` CORS settings

### Timeout errors
- Increase polling timeout for slow networks
- Reduce poll frequency if hitting rate limits

### Results not found after SUCCESS
- Results expire after 1 hour (configured in `celery_app.py`)
- Check if Redis is persisting data

## Next Steps

- Integrate polling into your existing UI components
- Add progress indicators based on task type
- Implement result caching
- Add WebSocket support for real-time updates (optional)
