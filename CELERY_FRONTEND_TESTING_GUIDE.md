# Quick Test Guide - Celery Frontend Integration

## ✅ Pre-Test Checklist

Before testing, verify everything is running:

```bash
# Terminal 1: Docker services
docker-compose up

# Verify in new terminal
docker-compose logs redis | grep "Ready to accept"
docker-compose logs celery_worker | grep "ready to accept"
docker-compose logs api | grep "Uvicorn running"
```

## 🧪 Test 1: See Reviews Appear Progressively (Manual)

### Steps

1. **Open ProductDetails Page**
   ```
   Navigate to: http://localhost:3000/product/[any-product-slug]
   Or search for a product and click on it
   ```

2. **Scroll to "Internet Reviews" Section**
   - Watch the reviews container

3. **Observe Reviews Appearing** (Opens DevTools for proof)
   ```
   F12 → Console → Filter: "Review"
   ```

4. **Expected Timeline**
   ```
   T+0s:   Hooks mount, tasks submitted
   T+2s:   First poll
   T+3s:   Store reviews appear (fastest) 🎉
   T+2-4s: More polls
   T+6s:   Community reviews appear 🎉
   T+8-10s: More polls
   T+10s:  Google reviews appear 🎉
   ```

## 🧪 Test 2: Verify Hook State Changes (DevTools)

### Setup

1. **Install Redux DevTools Extension**
   - Chrome: [Redux DevTools](https://chrome.google.com/webstore/detail/redux-devtools/)
   - Firefox: [Redux DevTools](https://addons.mozilla.org/en-US/firefox/addon/reduxdevtools/)

2. **Open Developer Tools**
   ```
   F12 → Navigate to Redux tab (if installed)
   Or → Console tab (no Redux extension needed)
   ```

### Console Logging Test

1. **Navigate to Product Page**
2. **Open Console** (F12 → Console)
3. **Filter by hook name**
   ```
   [useCommunityReviews]
   [useStoreReviews]
   [useGoogleReviews]
   ```

4. **Expected Console Output**
   ```
   [useCommunityReviews] Submitting task for: iPhone 15 Pro
   [useCommunityReviews] Task submitted, ID: abc-123-def-456
   [useCommunityReviews] Task status: STARTED
   [useCommunityReviews] Task status: STARTED
   [useCommunityReviews] Task status: STARTED
   [useCommunityReviews] Task completed! Reviews: 11
   ```

## 🧪 Test 3: Monitor API Calls (Network Tab)

### Steps

1. **Open DevTools → Network Tab**
   ```
   F12 → Network → Filter: "XHR"
   ```

2. **Navigate to Product Page**

3. **Watch Network Requests**
   ```
   POST /api/v1/reviews/community
     ├─ Response: {"task_id": "...", "status": "PENDING"}
     ├─ Time: ~50ms
     └─ Status: 200

   GET /api/v1/reviews/status/{task_id}
     ├─ Response: {"status": "STARTED", "ready": false}
     ├─ Time: ~30ms
     ├─ Repeats every 2 seconds
     └─ Status: 200
   
   GET /api/v1/reviews/status/{task_id}
     ├─ Response: {"status": "SUCCESS", "ready": true, "result": {...}}
     ├─ Time: ~40ms
     └─ Status: 200
   ```

## 🧪 Test 4: Verify Toast Notifications

### Steps

1. **Navigate to Product Page**
2. **Watch bottom-left corner for toasts**

### Expected Toasts
```
🎉 Added 8 store reviews!
(appears after 3-10 seconds)

🎉 Added 11 community reviews!
(appears after 30-40 seconds)

🎉 Added 71 Google Shopping reviews!
(appears after 50-60 seconds)
```

### If Not Showing
- Check if toast component is in layout
- Check browser console for errors
- Verify `react-hot-toast` is installed: `npm list react-hot-toast`

## 🧪 Test 5: Monitor Celery Worker (Terminal)

### In New Terminal

```bash
# Watch Celery worker logs
docker-compose logs -f celery_worker
```

### Filter Specific Tasks

```bash
# Just show task lifecycle
docker-compose logs celery_worker | grep -E "RECEIVED|STARTED|SUCCESS|FAILURE"
```

### Expected Output
```
[tasks] Received task: app.tasks.review_tasks.fetch_community_reviews[xxx]
[tasks] Task app.tasks.review_tasks.fetch_community_reviews[xxx] STARTED
[tasks] Task app.tasks.review_tasks.fetch_community_reviews[xxx] succeeded
```

## 🧪 Test 6: Check Redis Storage (Backend)

### Access Redis CLI

```bash
# Connect to Redis
docker exec -it imo_redis redis-cli

# In Redis CLI:
> KEYS *  # Show all keys
> GET celery-task-meta-abc123  # View specific task result
> FLUSHDB # Clear all (for testing only!)
```

### Expected Redis Data
```
Task metadata stored with structure:
{
  "status": "SUCCESS",
  "result": {...},
  "traceback": null
}
```

## 🧪 Test 7: Error Handling

### Test Network Error

1. **Stop Redis**
   ```bash
   docker-compose stop redis
   ```

2. **Navigate to Product Page**

3. **Expected**: 
   - Hook status: "error"
   - Error message in console
   - No reviews displayed

4. **Restart Redis**
   ```bash
   docker-compose start redis
   ```

### Test Celery Worker Down

1. **Stop Celery Worker**
   ```bash
   docker-compose stop celery_worker
   ```

2. **Navigate to Product Page**

3. **Expected**:
   - Task submitted successfully (returns task_id)
   - Polling continues but never completes
   - Eventually times out or shows error

4. **Restart Worker**
   ```bash
   docker-compose start celery_worker
   ```

## 🧪 Test 8: Verify Reviews Display Correctly

### Steps

1. **Navigate to Product with Reviews**
2. **Scroll to "Internet Reviews" Section**
3. **Verify Reviews Show:**
   - ✅ Review author/reviewer name
   - ✅ Star rating
   - ✅ Review date
   - ✅ Review text
   - ✅ Source (Google Shopping, Store, Community, etc.)

4. **Verify Sorting Works**
   - Filter by source
   - Sort by latest
   - Sort by rating
   - Sort by relevance

5. **Verify Pagination Works**
   - Multiple reviews shown
   - Pagination controls appear if 5+ reviews
   - Can navigate pages

## 🧪 Test 9: Multiple Products (No Duplicates)

### Steps

1. **Navigate to Product A**
   - Hooks trigger, tasks submitted
   - Reviews appear

2. **Wait 5 seconds**

3. **Navigate to Product B** (Different product)
   - New hooks mount
   - New tasks submitted for Product B
   - Product A reviews don't appear here (deduplication working)

4. **Go back to Product A**
   - Reviews already cached
   - No new tasks submitted
   - Reviews appear immediately from memory

## 🧪 Test 10: Performance Baseline

### Measure Load Time

1. **Open DevTools → Performance Tab**
   ```
   F12 → Performance
   ```

2. **Record Page Load**
   - Click "Record"
   - Navigate to product page
   - Wait for reviews to appear
   - Stop recording

3. **Analyze Timeline**
   - Task submissions: ~50-100ms each
   - Polling: ~30-50ms each request
   - UI updates: <100ms when reviews arrive
   - Total: Reviews appear within 60 seconds

### Expected Performance Metrics
```
✅ Task submission: <100ms
✅ Polling request: <50ms
✅ UI update: <100ms
✅ Total time to first review: <10 seconds
✅ Total time to all reviews: <60 seconds
✅ Page interactive: Immediately (not blocking)
```

## 📋 Automated Test Checklist

```
[ ] Reviews appear progressively (not all at once)
[ ] Toast notifications show for each source
[ ] Console logs show task IDs and status updates
[ ] Network tab shows polling pattern
[ ] Celery worker logs show task execution
[ ] Redis stores task results
[ ] Different products don't interfere
[ ] Error handling works gracefully
[ ] Performance is acceptable
[ ] UI remains responsive during fetch
```

## 🐛 Debugging Checklist

If something doesn't work:

### Check 1: Backend Running
```bash
curl http://localhost:8000/docs
# Should see Swagger UI
```

### Check 2: Redis Running
```bash
docker exec imo_redis redis-cli ping
# Should return: PONG
```

### Check 3: Celery Worker Running
```bash
docker-compose logs celery_worker | tail -20
# Should show: "[*] ready to accept tasks"
```

### Check 4: API Endpoint Works
```bash
curl -X POST http://localhost:8000/api/v1/reviews/community \
  -H "Content-Type: application/json" \
  -d '{"product_name":"test","brand":"test"}'
# Should return: {"task_id": "...", "status": "PENDING"}
```

### Check 5: Polling Endpoint Works
```bash
curl http://localhost:8000/api/v1/reviews/status/[TASK_ID]
# Should return: {"task_id": "...", "status": "..."}
```

### Check 6: Frontend Console
```
F12 → Console
Look for errors or warnings
Filter by: [use...Reviews]
```

## 📊 Expected Results Summary

| Component | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Task submission | <100ms | | |
| First poll response | <50ms | | |
| Store reviews appear | 10-15s | | |
| Community reviews appear | 30-40s | | |
| Google reviews appear | 50-60s | | |
| Toast notifications | 3/3 shown | | |
| No UI blocking | ✅ | | |
| Reviews combine correctly | ✅ | | |
| Deduplication works | ✅ | | |

## 🎓 Understanding the Logs

### What you should NOT see
```
❌ "Unregistered task" error
❌ Redis connection failed
❌ Task timeout
❌ Worker not found
```

### What you SHOULD see
```
✅ Task submitted with task_id
✅ Polling starts
✅ Status changes: STARTED → SUCCESS
✅ Task result returned with reviews
✅ Toast notification shown
✅ Reviews appear in UI
```

## 🚀 Quick Start Testing

**Quickest way to verify everything works:**

```bash
# Terminal 1
docker-compose up

# Terminal 2
# Wait 30 seconds for services to start
docker-compose logs celery_worker | grep ready

# Browser
# Open http://localhost:3000
# Search for product, click to view
# Scroll to Internet Reviews
# Watch reviews appear with toasts
```

That's it! If you see:
1. ✅ Reviews appearing progressively
2. ✅ Toast notifications
3. ✅ Console logs showing status updates

Then the Celery frontend integration is working perfectly! 🎉
