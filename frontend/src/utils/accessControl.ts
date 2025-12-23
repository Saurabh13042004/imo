// Utility functions for access control logic

/**
 * Configuration keys (loaded from environment or defaults)
 * Environment variables:
 * - VITE_GUEST_FREE_SEARCHES: Number of free searches for guests (default: 1)
 * - VITE_GUEST_PRODUCT_DISPLAY_LIMIT: Products shown per search for guests (default: 5)
 * - VITE_FREE_TIER_PRODUCT_DISPLAY_LIMIT: Products shown for free-tier users (default: 10)
 * - VITE_PAID_TIER_PRODUCT_DISPLAY_LIMIT: Products shown for paid users (default: 50)
 */
const GUEST_FREE_SEARCHES = parseInt(
  import.meta.env.VITE_GUEST_FREE_SEARCHES || '1'
);
const GUEST_PRODUCT_DISPLAY_LIMIT = parseInt(
  import.meta.env.VITE_GUEST_PRODUCT_DISPLAY_LIMIT || '5'
);
const FREE_TIER_PRODUCT_DISPLAY_LIMIT = parseInt(
  import.meta.env.VITE_FREE_TIER_PRODUCT_DISPLAY_LIMIT || '10'
);
const PAID_TIER_PRODUCT_DISPLAY_LIMIT = parseInt(
  import.meta.env.VITE_PAID_TIER_PRODUCT_DISPLAY_LIMIT || '50'
);

const GUEST_SEARCH_COUNT_KEY = 'imo_guest_search_count';
const GUEST_SEARCH_DATE_KEY = 'imo_guest_search_date';
const GUEST_FREE_SEARCHES_KEY = 'freeseearches';

// Initialize localStorage for new users
if (typeof window !== 'undefined') {
  if (localStorage.getItem(GUEST_FREE_SEARCHES_KEY) === null) {
    localStorage.setItem(GUEST_FREE_SEARCHES_KEY, '0');
  }
}

// ============================================================================
// GUEST SEARCH MANAGEMENT
// ============================================================================

/**
 * Get the number of free searches remaining for guest users
 */
export function getRemainingGuestSearches(): number {
  if (typeof window === 'undefined') return GUEST_FREE_SEARCHES;

  const count = parseInt(
    localStorage.getItem(GUEST_SEARCH_COUNT_KEY) || '0',
    10
  );
  return Math.max(0, GUEST_FREE_SEARCHES - count);
}

/**
 * Get the current guest search count
 */
export function getGuestSearchCount(): number {
  if (typeof window === 'undefined') return 0;

  return parseInt(
    localStorage.getItem(GUEST_SEARCH_COUNT_KEY) || '0',
    10
  );
}

/**
 * Check if guest user has searches remaining
 */
export function hasGuestSearchesRemaining(): boolean {
  return getRemainingGuestSearches() > 0;
}

/**
 * Increment the guest search counter
 */
export function incrementGuestSearchCount(): void {
  if (typeof window === 'undefined') return;

  const currentCount = getGuestSearchCount();
  const today = new Date().toDateString();
  const lastDate = localStorage.getItem(GUEST_SEARCH_DATE_KEY);

  // Reset counter if it's a new day
  if (lastDate !== today) {
    localStorage.setItem(GUEST_SEARCH_COUNT_KEY, '1');
    localStorage.setItem(GUEST_SEARCH_DATE_KEY, today);
  } else {
    localStorage.setItem(
      GUEST_SEARCH_COUNT_KEY,
      String(Math.min(currentCount + 1, GUEST_FREE_SEARCHES))
    );
  }
}

/**
 * Reset guest search counter (useful for testing or manual reset)
 */
export function resetGuestSearchCount(): void {
  if (typeof window === 'undefined') return;

  localStorage.removeItem(GUEST_SEARCH_COUNT_KEY);
  localStorage.removeItem(GUEST_SEARCH_DATE_KEY);
}

/**
 * Get the number of free searches a guest user gets
 */
export function getGuestFreeSearchCount(): number {
  return GUEST_FREE_SEARCHES;
}

/**
 * Check if user can perform a search action
 */
export function canUserSearch(
  isAuthenticated: boolean,
  remainingSearches: number = GUEST_FREE_SEARCHES
): boolean {
  if (isAuthenticated) return true;
  return remainingSearches > 0;
}

// ============================================================================
// PRODUCT DISPLAY LIMITS
// ============================================================================

/**
 * Get product display limit based on user tier
 * @param isAuthenticated - Whether user is authenticated
 * @param subscriptionTier - User's subscription tier ('free', 'pro', 'enterprise')
 */
export function getProductDisplayLimit(
  isAuthenticated: boolean,
  subscriptionTier: string = 'free'
): number {
  if (!isAuthenticated) {
    return GUEST_PRODUCT_DISPLAY_LIMIT;
  }

  switch (subscriptionTier) {
    case 'free':
      return FREE_TIER_PRODUCT_DISPLAY_LIMIT;
    case 'pro':
    case 'premium':
      return PAID_TIER_PRODUCT_DISPLAY_LIMIT;
    case 'enterprise':
      return PAID_TIER_PRODUCT_DISPLAY_LIMIT;
    default:
      return FREE_TIER_PRODUCT_DISPLAY_LIMIT;
  }
}

/**
 * Check if user should see search limit warnings
 */
export function shouldShowSearchLimitWarning(
  isAuthenticated: boolean,
  remainingSearches: number
): boolean {
  if (isAuthenticated) return false;
  return remainingSearches > 0 && remainingSearches <= 1;
}

/**
 * Get access control configuration for the app
 */
export function getAccessControlConfig() {
  return {
    guestFreeSearches: GUEST_FREE_SEARCHES,
    guestProductDisplayLimit: GUEST_PRODUCT_DISPLAY_LIMIT,
    freeTierProductDisplayLimit: FREE_TIER_PRODUCT_DISPLAY_LIMIT,
    paidTierProductDisplayLimit: PAID_TIER_PRODUCT_DISPLAY_LIMIT,
  };
}

// ============================================================================
// LEGACY FUNCTIONS (kept for backward compatibility)
// ============================================================================

/**
 * Determines if a user has access to a specific category
 */
export function hasAccessToCategory(
  category: string,
  hasActiveSubscription: boolean,
  unlockedCategories: string[]
): boolean {
  if (hasActiveSubscription) return true;
  return unlockedCategories.includes(category);
}

/**
 * Determines if a user can view all products (no limit)
 */
export function canViewAllProducts(hasActiveSubscription: boolean): boolean {
  return hasActiveSubscription;
}

/**
 * Gets the maximum number of products a user can view
 */
export function getMaxProductViewLimit(hasActiveSubscription: boolean): number {
  return hasActiveSubscription ? Infinity : 10;
}

/**
 * Filters products based on user access level
 */
export function filterProductsByAccess<T>(
  products: T[],
  hasActiveSubscription: boolean,
  maxProducts: number = 10
): T[] {
  if (hasActiveSubscription) return products;
  return products.slice(0, maxProducts);
}

/**
 * Determines if content should be blurred/locked
 */
export function shouldRestrictContent(
  requiresSubscription: boolean,
  requiredCategory: string | undefined,
  hasActiveSubscription: boolean,
  unlockedCategories: string[]
): boolean {
  if (requiresSubscription && !hasActiveSubscription) return true;
  if (requiredCategory && !hasAccessToCategory(requiredCategory, hasActiveSubscription, unlockedCategories)) return true;
  return false;
}

/**
 * Gets subscription tier display name
 */
export function getSubscriptionTierLabel(hasActiveSubscription: boolean): string {
  return hasActiveSubscription ? 'Premium' : 'Free';
}

/**
 * Categories that require unlocking (can be expanded)
 */
export const UNLOCKABLE_CATEGORIES = [
  'Electronics',
  'Home & Garden',
  'Sports & Outdoors',
  'Beauty & Personal Care',
  'Automotive',
  'Books',
  'Toys & Games',
  'Health & Wellness',
  'Fashion',
  'Tools & Hardware'
] as const;

export type UnlockableCategory = typeof UNLOCKABLE_CATEGORIES[number];