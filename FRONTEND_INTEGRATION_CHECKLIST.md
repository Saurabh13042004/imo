# Frontend Integration Checklist

## Quick Start (15 minutes)

### Step 1: Copy Component
```bash
# Already created at: frontend/components/ReviewTaskComponent.jsx
# Import and use in your app
```

### Step 2: Update API Base URL
If your API is not at `localhost:8000`, update the fetch URLs in the component:

```javascript
// In ReviewTaskComponent.jsx, change fetch URLs from:
/api/v1/reviews/community

// To your actual API endpoint:
https://your-api.com/api/v1/reviews/community
```

### Step 3: Test Component
```jsx
import ReviewTaskComponent from './components/ReviewTaskComponent';

function App() {
  return (
    <div>
      <ReviewTaskComponent />
    </div>
  );
}
```

### Step 4: Verify in Browser
1. Open http://localhost:3000 (or your dev server)
2. Enter a product name: "Samsung TV" or "iPhone 15 Pro"
3. Click "Get Reviews"
4. Should show status changing: ⏳ → 🔄 → ✅

---

## Full Integration Steps

### Backend Verification Checklist

- [ ] Celery worker is running
  ```bash
  docker-compose logs celery_worker | grep "ready"
  ```

- [ ] Redis is accessible
  ```bash
  docker-compose logs redis | grep "Ready to accept"
  ```

- [ ] API is running
  ```bash
  curl http://localhost:8000/docs  # Should show Swagger UI
  ```

- [ ] Review endpoints exist
  ```bash
  curl -X POST http://localhost:8000/api/v1/reviews/community \
    -H "Content-Type: application/json" \
    -d '{"product_name":"test"}'
  ```

### Frontend Integration Checklist

#### Option A: React with Component

- [ ] Install component
  ```bash
  cp ReviewTaskComponent.jsx src/components/
  ```

- [ ] Import in your page
  ```jsx
  import ReviewTaskComponent from './components/ReviewTaskComponent';
  ```

- [ ] Use in JSX
  ```jsx
  <ReviewTaskComponent />
  ```

- [ ] Test with sample product

#### Option B: React with Custom Hook

- [ ] Create hook file: `src/hooks/useReviewTask.js`
  ```javascript
  // Copy code from FRONTEND_INTEGRATION_GUIDE.md "React Hook" section
  ```

- [ ] Use in component
  ```jsx
  const { submitTask, status, result, error, isLoading } = useReviewTask();
  ```

#### Option C: Vue 3

- [ ] Create composable: `src/composables/useReviewTask.js`
  ```javascript
  // Copy code from FRONTEND_INTEGRATION_GUIDE.md "Vue 3" section
  ```

- [ ] Use in template
  ```vue
  <script setup>
  import { useReviewTask } from '@/composables/useReviewTask';
  const { submitTask, status, result } = useReviewTask();
  </script>
  ```

#### Option D: Vanilla JavaScript

- [ ] Add to HTML
  ```html
  <script src="js/review-task-poller.js"></script>
  ```

- [ ] Initialize
  ```javascript
  const poller = new ReviewTaskPoller('/api/v1');
  ```

### CORS Configuration (if needed)

If you get CORS errors:

1. Check backend CORS settings:
   ```bash
   # Edit app/main.py
   ```

2. Add your frontend origin:
   ```python
   CORSMiddleware.allow_origins = [
       "http://localhost:3000",
       "http://localhost:8080",
       "https://yourfrontend.com"
   ]
   ```

3. Restart API
   ```bash
   docker-compose restart api
   ```

### Environment Variables

Create `.env` file in frontend:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_VERSION=v1
```

Use in code:
```javascript
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_VERSION = process.env.REACT_APP_API_VERSION || 'v1';

// Usage
fetch(`${API_BASE}/api/${API_VERSION}/reviews/community`, ...)
```

---

## Task Submission Flow

### 1. User Submits Form
```javascript
handleSubmit = async (productName) => {
  // Call API
  const response = await fetch('/api/v1/reviews/community', {
    method: 'POST',
    body: JSON.stringify({ product_name: productName })
  });
  const { task_id } = await response.json();
  // Store task_id for polling
};
```

### 2. API Returns Task ID
```json
{
  "success": true,
  "task_id": "abc-123-def-456",
  "status": "PENDING",
  "message": "Task queued"
}
```

### 3. Frontend Polls for Status
```javascript
const pollStatus = async (taskId) => {
  const response = await fetch(`/api/v1/reviews/status/${taskId}`);
  const status = await response.json();
  
  if (status.status === 'SUCCESS') {
    // Display results
  } else if (status.status === 'FAILURE') {
    // Show error
  } else {
    // Poll again after 2 seconds
  }
};
```

### 4. Backend Processes Async
- Celery worker receives task
- Fetches reviews from multiple sources (30-60 seconds)
- Stores results in Redis
- Returns via GET status endpoint

### 5. Frontend Displays Results
```javascript
if (result.reviews) {
  result.reviews.forEach(review => {
    // Display review: title, rating, text, date
  });
}
```

---

## Testing Checklist

### Unit Tests

```javascript
// ReviewTaskComponent.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import ReviewTaskComponent from './ReviewTaskComponent';

test('renders form on mount', () => {
  render(<ReviewTaskComponent />);
  expect(screen.getByText('Get Reviews')).toBeInTheDocument();
});

test('submits product name', async () => {
  render(<ReviewTaskComponent />);
  
  fireEvent.change(screen.getByPlaceholderText(/product name/i), {
    target: { value: 'iPhone 15 Pro' }
  });
  
  fireEvent.click(screen.getByText('Get Reviews'));
  
  // Check if loading state appears
  expect(screen.getByText(/Processing reviews/i)).toBeInTheDocument();
});
```

### Integration Tests

```bash
# Test 1: Verify API returns task_id
curl -X POST http://localhost:8000/api/v1/reviews/community \
  -H "Content-Type: application/json" \
  -d '{"product_name":"Samsung TV"}'

# Expected response:
# {
#   "task_id": "xxx-xxx-xxx",
#   "status": "PENDING",
#   "success": true
# }

# Test 2: Poll for results
TASK_ID="xxx-xxx-xxx"
curl http://localhost:8000/api/v1/reviews/status/$TASK_ID

# Test 3: Monitor Celery worker
docker-compose logs -f celery_worker | grep "SUCCEEDED"
```

### E2E Tests

```javascript
// cypress/e2e/reviews.cy.js
describe('Review Task Flow', () => {
  it('fetches reviews from submission to display', () => {
    cy.visit('/');
    
    // Submit form
    cy.get('input[placeholder*="product"]').type('iPhone 15 Pro');
    cy.get('button').contains('Get Reviews').click();
    
    // Wait for loading
    cy.contains('Processing reviews', { timeout: 10000 }).should('exist');
    
    // Wait for results (max 2 minutes)
    cy.contains('Reviews loaded', { timeout: 120000 }).should('exist');
    
    // Verify results displayed
    cy.contains('Total Reviews').should('exist');
    cy.get('[data-testid="review-item"]').should('have.length.greaterThan', 0);
  });
});
```

---

## Performance Optimization

### 1. Results Caching
```javascript
const resultsCache = new Map();

async function getReviews(productName) {
  if (resultsCache.has(productName)) {
    return resultsCache.get(productName);
  }
  
  const result = await submitAndPollTask(productName);
  resultsCache.set(productName, result);
  
  // Cache for 1 hour
  setTimeout(() => resultsCache.delete(productName), 3600000);
  
  return result;
}
```

### 2. Concurrent Task Tracking
```javascript
const activeTasks = new Map();

function addTask(taskId, productName) {
  activeTasks.set(taskId, {
    productName,
    status: 'PENDING',
    createdAt: Date.now()
  });
}

function getTasks() {
  return Array.from(activeTasks.values());
}
```

### 3. Optimistic Updates
```javascript
// Show results immediately, update if changed
async function submitWithOptimistic(productName) {
  // Show cached results immediately
  if (cache[productName]) {
    setResult(cache[productName]);
  }
  
  // Fetch fresh data in background
  const fresh = await pollTask(taskId);
  
  // Update if different
  if (JSON.stringify(fresh) !== JSON.stringify(cache[productName])) {
    setResult(fresh);
  }
}
```

---

## Troubleshooting

### Symptom: "Task failed with no message"
**Check:**
1. Celery worker logs: `docker-compose logs celery_worker | tail -50`
2. API logs: `docker-compose logs api | tail -50`
3. Redis connection: `docker exec imo_redis redis-cli ping`

### Symptom: "Responses not coming in UI"
**Solution:**
This is expected with async processing. UI must poll for results:
1. Verify backend API works: `curl http://localhost:8000/api/v1/reviews/status/{task_id}`
2. Check console errors in browser (F12)
3. Add debugging to component:
   ```javascript
   console.log('Polling:', taskId);
   console.log('Status:', status);
   console.log('Result:', result);
   ```

### Symptom: CORS errors in browser console
**Fix:**
1. Check backend CORS middleware in `app/main.py`
2. Add frontend URL to `allow_origins`
3. Restart API: `docker-compose restart api`

### Symptom: Task timeout after 2 minutes
**Issue:** Long-running tasks
**Fix:** Increase polling timeout in component:
```javascript
const MAX_WAIT_TIME = 300000; // 5 minutes instead of 2
```

### Symptom: Results showing old data
**Fix:** Clear Redis cache:
```bash
docker exec imo_redis redis-cli FLUSHDB
```

### Symptom: "WebSocket connection failed"
**Info:** Not needed for basic polling - only if you upgrade to WebSockets
**For now:** Stick with HTTP polling

---

## Production Deployment

### 1. Update API URLs
```javascript
// Development
const API_URL = 'http://localhost:8000/api/v1';

// Production
const API_URL = process.env.REACT_APP_API_URL || 'https://api.yoursite.com/api/v1';
```

### 2. Add Error Tracking
```javascript
// Report polling errors to Sentry, LogRocket, etc.
if (error) {
  trackError({
    message: error.message,
    taskId: taskId,
    timestamp: new Date()
  });
}
```

### 3. Monitor Performance
```javascript
// Track polling duration
const pollStart = Date.now();
const duration = Date.now() - pollStart;
analytics.track('review_task_completed', {
  duration,
  reviewCount: result.reviews.length
});
```

### 4. Rate Limiting
```javascript
// Prevent user from submitting too many tasks
const lastSubmit = useRef(0);
const MIN_INTERVAL = 5000; // 5 seconds between submissions

const handleSubmit = (e) => {
  if (Date.now() - lastSubmit.current < MIN_INTERVAL) {
    setError('Please wait before submitting again');
    return;
  }
  lastSubmit.current = Date.now();
  // Submit task
};
```

### 5. Session Storage for Task History
```javascript
// Save task history in sessionStorage
function saveTaskHistory(taskId, productName, result) {
  const history = JSON.parse(sessionStorage.getItem('reviewTasks') || '[]');
  history.push({ taskId, productName, result, timestamp: Date.now() });
  sessionStorage.setItem('reviewTasks', JSON.stringify(history));
}

// Retrieve on page reload
function getTaskHistory() {
  return JSON.parse(sessionStorage.getItem('reviewTasks') || '[]');
}
```

---

## Next Steps

1. **Choose integration method** (React component, Vue, Vanilla JS)
2. **Copy component/hook** to your frontend
3. **Update API URL** if not localhost:8000
4. **Test locally** with `docker-compose up`
5. **Run browser tests** to verify polling works
6. **Deploy to production**

---

## Support & Debugging

### Get Backend Status
```bash
docker-compose ps
```

### View Celery Task Queue
```bash
open http://localhost:5555  # Flower UI
```

### Check Redis Data
```bash
docker exec imo_redis redis-cli
> KEYS *  # Show all keys
> GET task_id_here  # Get specific result
```

### Debug Frontend
```javascript
// Add to ReviewTaskComponent.jsx for logging
useEffect(() => {
  console.log('Task ID:', taskId);
  console.log('Status:', status);
  console.log('Result:', result);
  console.log('Error:', error);
}, [taskId, status, result, error]);
```

### Test API Directly
```bash
# Submit task
curl -X POST http://localhost:8000/api/v1/reviews/community \
  -H "Content-Type: application/json" \
  -d '{"product_name":"test product"}'

# Get status (replace XXX with task_id from above)
curl http://localhost:8000/api/v1/reviews/status/XXX
```

