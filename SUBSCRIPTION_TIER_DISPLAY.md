# Subscription Tier Display in Header

## Overview
The header now displays the user's subscription status dynamically based on their authentication state and subscription tier in the database.

## Implementation

### Changes Made

#### File: `frontend/src/components/subscription/SubscriptionStatusIndicator.tsx`

**Updated Logic:**
- Changed from using `useUserAccess()` hook to `useAuth()` hook
- Now directly checks `user.subscription_tier` from the authenticated user object
- Simple logic: if user is logged in and has `subscription_tier === 'premium'`, show "Premium", otherwise show "Free"

**Key Changes:**
```tsx
// Before
const { hasActiveSubscription, accessLevel, subscription } = useUserAccess();

// After
const { user } = useAuth();
const hasActiveSubscription = user && user.subscription_tier === 'premium';
```

### Display Logic

The header now displays:

1. **For Unauthenticated Users (not logged in)**
   - No subscription indicator shown (only appears when user is logged in)

2. **For Authenticated Free Users**
   - Badge: `✨ Free` (with Sparkles icon, muted foreground color)
   - Default badge variant with neutral styling

3. **For Authenticated Premium Users** (subscription_tier === 'premium')
   - Badge: `👑 Premium` (with Crown icon, yellow/orange gradient)
   - Gradient background: `from-yellow-500 to-orange-500`
   - White text on gradient background

### SearchHeader Usage

In `frontend/src/components/search/SearchHeader.tsx`:
```tsx
<SubscriptionStatusIndicator variant="badge" size="sm" />
```

This displays the subscription badge in the header, right next to the theme toggle and user menu.

### Data Flow

1. User logs in → `AuthContext` stores `user.subscription_tier` from backend
2. `useAuth()` provides the user object with subscription tier
3. `SubscriptionStatusIndicator` checks the tier and displays appropriate badge
4. Backend sets `subscription_tier` to either:
   - `'free'` (default for new users)
   - `'premium'` (for paid subscribers)
   - Or other tiers as defined in your system

### Variants Supported

The component still supports all three display variants:

1. **Badge** (default)
   ```tsx
   <SubscriptionStatusIndicator variant="badge" size="md" />
   // Shows: 👑 Premium or ✨ Free
   ```

2. **Text**
   ```tsx
   <SubscriptionStatusIndicator variant="text" size="sm" />
   // Shows: Crown icon + "Premium" text or Sparkles icon + "Free" text
   ```

3. **Icon Only**
   ```tsx
   <SubscriptionStatusIndicator variant="icon" size="lg" />
   // Shows: Just the crown or sparkles icon
   ```

### Database Schema

The backend uses `subscription_tier` field in the `profiles` table:
- **Column**: `subscription_tier` (String, default: 'free')
- **Values**: 'free', 'premium' (or custom tiers as needed)
- **Set During**: User signup (default 'free') or subscription creation

### Next Steps

To use this implementation:

1. Ensure your backend's `/auth/signin` and `/auth/me` endpoints return `subscription_tier` in the user response
2. When users upgrade to premium, update their `subscription_tier` to `'premium'` in the database
3. The header will automatically show the correct status based on the user's tier

### Example Backend Response

```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "subscription_tier": "free",  // ← This field determines the display
    "roles": ["user"]
  },
  "access_token": "...",
  "refresh_token": "..."
}
```

### Testing

1. **Test Free User**:
   - Create a user with `subscription_tier = 'free'`
   - Log in and check header shows `✨ Free`

2. **Test Premium User**:
   - Update user's `subscription_tier = 'premium'`
   - Refresh and verify header shows `👑 Premium` with gradient background

3. **Test Unauthenticated**:
   - Log out and verify no subscription indicator appears (user menu shows Sign In/Sign Up buttons instead)
