# Auto-Location Detection Implementation

## Overview
Users now see their actual location automatically populated on the search page, instead of a hardcoded default zipcode.

## How It Works

### 1. **Initial Page Load**
When a user lands on the search page (`/search`), the system automatically:
1. Checks if a cached zipcode exists from a previous session (24-hour cache)
2. If no cache and no URL parameter, detects user's real location
3. Displays detected zipcode in the search form

### 2. **Detection Methods** (In Order of Preference)

#### Method A: IP-Based Geolocation (Primary)
- **Provider**: ip-api.com (free, no API key needed)
- **Speed**: ~100-500ms
- **Accuracy**: City/zipcode level
- **No User Permission**: Required (unlike browser geolocation)
- **Fallback**: Used if browser geolocation unavailable or denied

#### Method B: Browser Geolocation (Secondary)
- **Provider**: Browser's native Geolocation API
- **Speed**: ~2-5 seconds
- **Accuracy**: High (~10-100 meters)
- **User Permission**: Required
- **Reverse Geocoding**: Uses OpenStreetMap Nominatim API to convert coordinates → zipcode

#### Method C: Cached Location (Fastest)
- **Storage**: localStorage with 24-hour TTL
- **Speed**: Instant
- **Perfect For**: Returning users within 24 hours
- **Cache Key**: `userZipcode` + `userZipcodeTime`

#### Method D: Fallback
- **Default**: "60607" (Chicago) if all detection methods fail
- **User Override**: Users can manually change zipcode anytime via UI

### 3. **UI Behavior**

**Initial Load**:
```
"Search for tools, appliances..." 
[Search input field]  [60607] ← Auto-detected or cached
      [Search button]
```

**User Changes Zipcode**:
1. Click zipcode button → Input field appears
2. Enter new zipcode
3. Click OK → Saved to localStorage + URL params
4. Future sessions auto-load this zipcode

### 4. **Caching Strategy**

```typescript
// 24-hour cache mechanism
localStorage.userZipcode = "60607"
localStorage.userZipcodeTime = 1734873600000  // Timestamp

// Check: if (Date.now() - timestamp > 24 hours) → Refresh
```

### 5. **API Calls**

**IP Geolocation Request** (Fast path):
```
GET https://ip-api.com/json/?fields=zip,city,regionName,lat,lon
Response: { zip: "60607", city: "Chicago", regionName: "Illinois", ... }
```

**Reverse Geocoding** (Only if browser geolocation used):
```
GET https://nominatim.openstreetmap.org/reverse?format=json&lat=41.88&lon=-87.63
Response: { address: { postcode: "60607", ... }, ... }
```

## Code Flow

### File: `src/utils/geolocation.ts`
**Functions**:
- `getUserZipcode()` - Main entry point, tries both methods
- `getLocationFromIP()` - IP-based detection (ip-api.com)
- `getLocationFromBrowser()` - Browser Geolocation API + Nominatim reverse geocoding
- `getCachedZipcode()` - Retrieve cached zipcode with TTL validation
- `cacheZipcode()` - Store zipcode with timestamp

### File: `src/hooks/useSearchUrl.tsx`
**Changes**:
- Added `useEffect` to auto-detect location on component mount
- Added `detectedZipcode` and `isDetectingLocation` state
- Fallback chain: URL param → Detected → Cached → Default ("60607")

### File: `src/components/search/SharedSearchInput.tsx`
**No Changes**: Already supports dynamic zipcode via `urlZipcode` from `useSearchUrl`

## User Experience Flow

### Scenario 1: First-Time User
```
1. User lands on /search
2. System detects IP location → "60607"
3. User sees: [Search] [60607 button]
4. User can search or click to change zipcode
5. Zipcode cached for next visit
```

### Scenario 2: Returning User (Within 24h)
```
1. User lands on /search
2. System loads cached zipcode → "94105"
3. User sees: [Search] [94105 button]
4. Search uses cached location (instant load)
```

### Scenario 3: User Changes Zipcode
```
1. User clicks zipcode button
2. Enters new zipcode: "90210"
3. Clicks OK
4. New zipcode saved to cache + URL params
5. Search results use new zipcode
6. Future visits auto-load "90210"
```

### Scenario 4: Search to ProductDetails
```
1. User searches with zipcode "60607" → URL: /search?q=ps5&zipcode=60607
2. Clicks product → ProductDetails passes zipcode to API
3. Returns to search → Zipcode "60607" persists
```

## Privacy & Security

✅ **No Personal Data Stored**:
- Only zipcode (5-digit code) stored, never full address
- No tracking or analytics on location
- Data cached locally in browser only

✅ **Third-Party APIs**:
- **ip-api.com**: Free tier, no API key required, 45 requests/minute limit
- **nominatim.openstreetmap.org**: Free, open-source, requires User-Agent header
- Both are reputable, widely-used services

✅ **CORS-Friendly**:
- IP geolocation via CORS-enabled endpoint
- Reverse geocoding via public CORS-enabled API
- No authentication required

## Error Handling

**Graceful Degradation**:
```
If IP geolocation fails → Try browser geolocation
If browser geolocation fails → Try cache
If cache expired → Use default "60607"
```

**Timeouts**:
- Browser geolocation: 5-second timeout
- IP geolocation: Network timeout only
- Total detection: <2 seconds in success path

**User Notification**:
- Silent failure (no error toast)
- Falls back to default seamlessly
- User can always override manually

## Testing

### Test IP Geolocation:
```javascript
// In browser console:
const result = await getUserZipcode();
console.log(result); // { zipcode: "60607", city: "Chicago", ... }
```

### Test Cache:
```javascript
// Check cached value:
localStorage.userZipcode // "60607"
localStorage.userZipcodeTime // "1734873600000"

// Clear cache and refresh:
localStorage.removeItem('userZipcode');
localStorage.removeItem('userZipcodeTime');
```

### Test Different Locations:
- Use browser DevTools to override geolocation
- Use VPN to test IP geolocation with different location
- Manually set zipcode and verify persistence

## Browser Support

| Feature | Support |
|---------|---------|
| IP Geolocation (ip-api.com) | All modern browsers |
| Browser Geolocation API | Chrome, Firefox, Safari, Edge |
| localStorage | All modern browsers |
| Fetch API | All modern browsers |

## Performance

- **IP Geolocation**: 100-500ms (mostly network latency)
- **Browser Geolocation**: 2-5s (requires user permission)
- **Cache Lookup**: <1ms (instant)
- **Total Page Load Impact**: <500ms (cached path) or <2s (fresh detection)

## Configuration

To change default zipcode, edit `app/config.py`:
```python
DEFAULT_ZIPCODE: str = os.getenv("DEFAULT_ZIPCODE", "60607")
```

Or set environment variable:
```bash
export DEFAULT_ZIPCODE=94105  # San Francisco
```

## Future Enhancements

1. **Better Accuracy**: Use MaxMind GeoIP2 (free tier available)
2. **Address Autocomplete**: Google Places API integration
3. **Multiple Locations**: Save favorite zipcodes
4. **Location Search**: Click zipcode → view nearby stores
5. **Analytics**: Track most popular search locations
