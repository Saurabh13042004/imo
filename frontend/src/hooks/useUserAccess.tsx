import { useEffect, useState, useCallback } from 'react';
import { useAuth } from './useAuth';

interface PaymentMethod {
  brand: string;
  last4: string;
  exp_month?: number;
  exp_year?: number;
}

interface SubscriptionData {
  plan_type: string;
  is_active: boolean;
  is_trial: boolean;
  billing_cycle?: string;
  subscription_start?: string;
  subscription_end?: string;
  trial_start?: string;
  trial_end?: string;
  current_period_end?: string;
  days_remaining?: number;
  cancel_at_period_end?: boolean;
  status?: string;
  payment_method?: PaymentMethod;
}

const API_BASE_URL = import.meta.env.VITE_API_URL';

export function useUserAccess() {
  const { isAuthenticated, user, accessToken } = useAuth();
  const [subscription, setSubscription] = useState<SubscriptionData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch subscription from backend
  const fetchSubscription = useCallback(async () => {
    console.log('fetchSubscription called', { isAuthenticated, hasAccessToken: !!accessToken, user });
    
    if (!isAuthenticated || !accessToken) {
      console.log('fetchSubscription: Not authenticated or no token, skipping');
      setSubscription(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log('fetchSubscription: Making API call to', `${API_BASE_URL}/api/v1/payments/subscription`);
      
      const response = await fetch(`${API_BASE_URL}/api/v1/payments/subscription`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      console.log('Subscription API Response:', {
        status: response.status,
        ok: response.ok,
        url: response.url
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Subscription API Error:', errorText);
        throw new Error('Failed to fetch subscription');
      }

      const data: SubscriptionData = await response.json();
      console.log('Subscription API Data:', data);
      setSubscription(data);
      
      // Cache subscription in localStorage
      localStorage.setItem('user_subscription', JSON.stringify(data));
    } catch (err) {
      console.error('Error fetching subscription:', err);
      // Fallback to cached subscription
      const cached = localStorage.getItem('user_subscription');
      if (cached) {
        setSubscription(JSON.parse(cached));
      }
      setError(err instanceof Error ? err.message : 'Failed to fetch subscription');
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, accessToken]);

  // Fetch on mount and when auth changes
  useEffect(() => {
    fetchSubscription();
  }, [fetchSubscription]);

  // Determine access level based on subscription
  const accessLevel = subscription?.plan_type === 'free' || !subscription?.is_active 
    ? ('free' as const)
    : ('premium' as const);

  const hasActiveSubscription = subscription?.is_active === true && (
    subscription.plan_type === 'premium' || subscription.plan_type === 'trial'
  );

  return {
    hasActiveSubscription,
    subscription,
    accessLevel,
    loading,
    error,
    unlockedSearches: [],
    unlockedCategories: [],
    canAccessSearch: () => hasActiveSubscription,
    canAccessCategory: () => hasActiveSubscription,
    canAccessPremiumFeatures: () => hasActiveSubscription,
    canViewAllProducts: () => hasActiveSubscription,
    getMaxProductCount: () => hasActiveSubscription ? Infinity : 10,
    refreshAccess: () => fetchSubscription(),
    refetchAccess: () => fetchSubscription(),
  };
}