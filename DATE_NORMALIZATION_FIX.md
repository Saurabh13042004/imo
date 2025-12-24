# Date Normalization Fix for SerpAPI Review Dates

## Problem
The `/api/v1/product/enriched/{product_id}` endpoint was returning reviews with invalid or relative date formats from SerpAPI, such as:
- `"a year ago"`
- `"7 months ago"`
- `"2 weeks ago"`
- `"3 days ago"`
- Mixed text like `"TL; DR - Legit Global ROM..."`

This caused issues on the frontend when dates needed to be in ISO format (YYYY-MM-DDTHH:MM:SSZ).

## Solution

### 1. **New Date Parsing Utility** (`backend/app/utils/helpers.py`)
Added `parse_relative_date()` function that:
- Converts relative dates ("a year ago", "7 months ago", etc.) to ISO format
- Parses absolute date formats (Dec 25, 2024, 2024-12-25, etc.)
- Gracefully handles unparseable strings by returning None
- Uses today's date as reference point for relative calculations

**Supported formats:**
- Relative: `"a year ago"`, `"1 year ago"`, `"7 months ago"`, `"2 weeks ago"`, `"3 days ago"`, `"an hour ago"`
- Absolute: `"Dec 25, 2024"`, `"2024-12-25"`, `"25/12/2024"`, `"25 December 2024"`, etc.
- Returns None for unparseable strings (no error, no blocking)

### 2. **Date Normalization Function** (`backend/app/api/routes/products.py`)
Added `normalize_review_dates()` function that:
- Deep copies the API response to avoid modifying originals
- Recursively processes all review dates in:
  - `user_reviews[]` arrays
  - `reviews[]` arrays
  - `product_results.user_reviews[]` arrays
  - `product_results.reviews[]` arrays
- Applies `parse_relative_date()` to each date field

### 3. **Integration Points**

#### Endpoint: `/api/v1/product/enriched/{product_id}` (POST)
```python
# After fetching from SerpAPI
immersive_data = response.json()

# Normalize all review dates
logger.info("[Enriched] Normalizing review dates...")
immersive_data = normalize_review_dates(immersive_data)

return {
    "product_id": product_id,
    "immersive_data": immersive_data
}
```

#### Endpoint: `/api/v1/product/{product_id}/ai-verdict` (POST)
```python
# After receiving enriched_data from frontend
enriched_data = request.enriched_data

# Normalize all review dates
logger.info("[AI Verdict] Normalizing review dates...")
enriched_data = normalize_review_dates(enriched_data)

# Continue with AI verdict generation
```

## Key Features

✅ **Non-blocking**: Returns None for unparseable dates, doesn't throw errors  
✅ **Backward compatible**: ISO dates pass through unchanged  
✅ **Deep copy**: Original data structures never modified  
✅ **Recursive**: Handles nested review arrays at multiple levels  
✅ **Comprehensive**: Covers all known review date field locations  

## Testing

The solution has been tested with:
- Relative date formats: `"a year ago"`, `"7 months ago"`, `"2 weeks ago"`, `"3 days ago"`, `"an hour ago"`
- Absolute date formats: `"Dec 25, 2024"`, `"2024-12-25"`, `"Dec 25, 2024"`, etc.
- Mixed text: `"TL; DR - Legit Global ROM..."` → Returns None (graceful handling)
- None/empty values: Returns None without errors

## Example

**Before (Relative dates from SerpAPI):**
```json
{
  "user_reviews": [
    {
      "text": "Great product!",
      "date": "a year ago",
      "rating": 5
    },
    {
      "text": "Not bad",
      "date": "7 months ago",
      "rating": 4
    }
  ]
}
```

**After (ISO format dates):**
```json
{
  "user_reviews": [
    {
      "text": "Great product!",
      "date": "2024-12-24T22:01:30.618625Z",
      "rating": 5
    },
    {
      "text": "Not bad",
      "date": "2025-05-28T22:01:30.618872Z",
      "rating": 4
    }
  ]
}
```

## Files Modified

1. **`backend/app/utils/helpers.py`**
   - Added `parse_relative_date()` function
   - Added imports: `datetime`, `timedelta`, `logging`

2. **`backend/app/api/routes/products.py`**
   - Added `import copy`
   - Added `from app.utils.helpers import parse_relative_date`
   - Added `normalize_review_dates()` function
   - Modified `/product/enriched/{product_id}` endpoint to normalize dates
   - Modified `/product/{product_id}/ai-verdict` endpoint to normalize dates

## Impact

- **Frontend**: Now receives dates in consistent ISO format for all products
- **Backend**: No change to business logic, purely a data normalization layer
- **Performance**: Minimal overhead (simple string parsing and deep copy)
- **Reliability**: Graceful handling of any unparseable date formats
