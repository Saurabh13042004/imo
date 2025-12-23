# Tiered Access Control System

## Overview

The platform implements a multi-tier access control system that manages search limits and product display counts based on user authentication status and subscription tier.

## User Tiers

### 1. Guest User (Unauthenticated)

**Default Behavior:**
- Limited number of free searches (configurable, default: 1)
- Limited products per search results page (configurable, default: 5)
- Can explore all pages without authentication
- Once free searches exhausted, must sign in to continue

**Characteristics:**
- No persistent account
- Resets daily (search count resets each day at midnight)
- Tracked via browser localStorage
- See prominent sign-in prompts

### 2. Free-Tier User (Authenticated)

**Default Behavior:**
- Unlimited searches
- Products per page: 10 (configurable)
- Automatic role assignment: 'user'
- Created when user signs up without premium payment
- Can upgrade to paid tiers

**Characteristics:**
- All guest restrictions removed
- Full search capability
- See premium/upgrade prompts on other features

### 3. Paid-Tier Users (Pro/Premium/Enterprise)

**Default Behavior:**
- Unlimited searches
- Products per page: 50 (configurable)
- Full feature access
- Priority support and advanced features

## Configuration

### Environment Variables

Frontend environment variables (`.env.local`):

```bash
# Number of free searches for guest users
VITE_GUEST_FREE_SEARCHES=1

# Products displayed per search for guests
VITE_GUEST_PRODUCT_DISPLAY_LIMIT=5

# Products displayed per search for free-tier authenticated users
VITE_FREE_TIER_PRODUCT_DISPLAY_LIMIT=10

# Products displayed per search for paid-tier users
VITE_PAID_TIER_PRODUCT_DISPLAY_LIMIT=50
```

### Default Values

| Setting | Guest | Free-Tier | Paid |
|---------|-------|-----------|------|
| Free Searches | 1 | ∞ | ∞ |
| Products/Page | 5 | 10 | 50 |
| Can Search | Yes (limited) | Yes | Yes |
| Can Explore | Yes | Yes | Yes |

## Implementation Details

### Guest Search Tracking

**Storage Location:** Browser localStorage

```javascript
// Keys used
'imo_guest_search_count'  // Number of searches performed today
'imo_guest_search_date'   // Date of first search today
```

**Reset Mechanism:**
- Daily reset at midnight
- Automatically resets when date changes
- Persists across browser tabs/windows (same device)
- Clears on cache clear or localStorage wipe

### Product Display Limiting

**Guest Users:**
```typescript
const displayProducts = products.slice(0, GUEST_PRODUCT_DISPLAY_LIMIT);
// Shows only first 5 products from search results
```

**Free-Tier Users:**
```typescript
// Shows all products returned by backend (up to FREE_TIER_PRODUCT_DISPLAY_LIMIT)
```

**Paid Users:**
```typescript
// Shows all products returned by backend (up to PAID_TIER_PRODUCT_DISPLAY_LIMIT)
```

## Usage Examples

### Check If Guest Can Search

```typescript
import { 
  hasGuestSearchesRemaining,
  getRemainingGuestSearches 
} from '@/utils/accessControl';

if (!user && !hasGuestSearchesRemaining()) {
  // Show sign-in prompt
}

const remaining = getRemainingGuestSearches();
// Returns: 0, 1, 2, 3, etc.
```

### Increment Search Count

```typescript
import { incrementGuestSearchCount } from '@/utils/accessControl';

// After user performs a search
if (!user) {
  incrementGuestSearchCount();
}
```

### Get Product Display Limit

```typescript
import { getProductDisplayLimit } from '@/utils/accessControl';

const limit = getProductDisplayLimit(
  isAuthenticated,
  user?.subscription_tier || 'free'
);

const displayProducts = products.slice(0, limit);
```

### Get Configuration

```typescript
import { getAccessControlConfig } from '@/utils/accessControl';

const config = getAccessControlConfig();
// Returns:
// {
//   guestFreeSearches: 1,
//   guestProductDisplayLimit: 5,
//   freeTierProductDisplayLimit: 10,
//   paidTierProductDisplayLimit: 50
// }
```

## Search Page Flow

### 1. Guest User Landing on Search Page

```
1. Guest opens /search
2. Check: hasGuestSearchesRemaining() → true
3. Display: "1/1 free searches remaining" banner
4. Allow search input
```

### 2. Guest Performs First Search

```
1. Click search button
2. Check: hasGuestSearchesRemaining() → true
3. Execute: incrementGuestSearchCount()
4. Display: First 5 products from results
5. Update banner: "0/1 free searches remaining"
```

### 3. Guest Exhausts Searches

```
1. Try to search again
2. Check: hasGuestSearchesRemaining() → false
3. Show: "Free searches exhausted" message with sign-in button
4. Prevent: Search from executing
5. Offer: Sign-in or view pricing
```

### 4. Guest Signs In

```
1. Navigate to /auth
2. Complete sign-up/sign-in
3. AuthContext stores tokens and user data
4. Redirect to home or last page
5. Guest limits removed
6. Full search access enabled
7. Products per page increased to 10+
```

## Mobile Responsiveness

All banners and messages are responsive:

```typescript
// On mobile: Stack vertically
<div className="flex flex-col sm:flex-row gap-4">
  <Banner />
  <Actions />
</div>

// Guest banner adapts to screen size
// Exhausted message centers on mobile
// All buttons remain tappable (48px+ minimum)
```

## Analytics & Tracking

### What Gets Tracked

- ✅ Search performed (with query)
- ✅ Product count displayed
- ✅ User tier (guest/free/paid)
- ✅ Search exhaustion event

### What Doesn't Get Tracked

- ❌ Individual localStorage access
- ❌ Search count increments (internal only)
- ❌ Product limiting (internal only)

## Security Considerations

### Client-Side Limiting

**Important:** Product limiting is client-side only. This is appropriate for UX but should NOT be relied upon for security-sensitive features.

### Token-Based Access

- Search API calls include JWT token (if authenticated)
- Backend can verify user tier independently
- Backend enforces stricter limits if needed

### Best Practices

1. ✅ Use this for user experience
2. ✅ Show helpful limitations
3. ⚠️ Don't rely on this for security
4. ⚠️ Always verify on backend

## Testing

### Test Guest Search Limits

```javascript
// Open browser console on /search
import { getRemainingGuestSearches, incrementGuestSearchCount } from '@/utils/accessControl';

// Check initial
getRemainingGuestSearches(); // 1

// Simulate search
incrementGuestSearchCount();
getRemainingGuestSearches(); // 0

// Reset for testing
localStorage.clear();
```

### Test Product Display Limits

```javascript
import { getProductDisplayLimit } from '@/utils/accessControl';

// Guest: 5
getProductDisplayLimit(false);

// Free-tier: 10
getProductDisplayLimit(true, 'free');

// Paid: 50
getProductDisplayLimit(true, 'pro');
```

### Reset Guest Searches

```javascript
import { resetGuestSearchCount } from '@/utils/accessControl';

resetGuestSearchCount();
// Clears localStorage entries
// Guest gets fresh 1 free search
```

## Customization

### Change Guest Free Searches

Edit `.env.local`:

```bash
# Allow 3 free searches instead of 1
VITE_GUEST_FREE_SEARCHES=3
```

### Change Product Display Limits

Edit `.env.local`:

```bash
# Guest: 10 products
VITE_GUEST_PRODUCT_DISPLAY_LIMIT=10

# Free-tier: 20 products
VITE_FREE_TIER_PRODUCT_DISPLAY_LIMIT=20

# Paid: 100 products
VITE_PAID_TIER_PRODUCT_DISPLAY_LIMIT=100
```

## API Integration

### Sign-In API Call

```typescript
// After successful sign-in
const response = await authAPI.signIn({
  email: 'user@example.com',
  password: 'password'
});

// Response includes subscription_tier
// {
//   user: {
//     id: '...',
//     subscription_tier: 'free',  // or 'pro', 'enterprise'
//     roles: ['user'],
//     ...
//   },
//   access_token: '...',
//   refresh_token: '...'
// }

// AuthContext stores this and provides via useAuth()
```

### Backend Search Endpoint

Consider implementing server-side validation:

```python
# Backend: app/api/routes/search.py

@router.get("/search")
async def search(
    query: str,
    page: int = 1,
    current_user: Optional[Profile] = Depends(get_optional_user),
    session: AsyncSession = Depends(get_db)
):
    # Get user's display limit
    limit = get_product_display_limit(
        is_authenticated=current_user is not None,
        subscription_tier=current_user.subscription_tier if current_user else 'free'
    )
    
    # Apply limit to results
    results = products[:limit]
    return results
```

## Migration Guide

### From Old Access Control

If migrating from previous access control system:

```typescript
// Old way (if using old functions)
const limit = getMaxProductViewLimit(hasActiveSubscription);

// New way (recommended)
const limit = getProductDisplayLimit(
  isAuthenticated,
  subscriptionTier
);
```

## Troubleshooting

### Guest Still Seeing Exhausted Message

**Solution:**
```javascript
// Check localStorage
localStorage.getItem('imo_guest_search_count');
localStorage.getItem('imo_guest_search_date');

// Reset if needed
localStorage.removeItem('imo_guest_search_count');
localStorage.removeItem('imo_guest_search_date');
```

### Products Not Limited for Guest

**Solution:**
1. Verify `.env.local` has `VITE_GUEST_PRODUCT_DISPLAY_LIMIT`
2. Check if user is actually authenticated
3. Verify `useAuth()` returns `user: null` for guests

### Search Works After Sign-In

**Expected behavior.** Sign-in resets exhaustion flag and removes product limits.

## Future Enhancements

- [ ] Gradual rollout (increase limits before upgrade)
- [ ] A/B testing different limits
- [ ] Premium features previews for guests
- [ ] Time-limited free trial increases
- [ ] Referral program with bonus searches
- [ ] Regional variations of limits
- [ ] Seasonal promotional limits
