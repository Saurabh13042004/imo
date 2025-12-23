import { useCallback, useState } from 'react';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/hooks/useAuth';
import { useNavigate } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function useSubscriptionFlow() {
  const { toast } = useToast();
  const { isAuthenticated, accessToken } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createCheckoutSession = useCallback(async (
    type: 'subscription' | 'trial' = 'subscription',
    billingCycle: 'monthly' | 'yearly' = 'monthly'
  ) => {
    // Redirect to login if not authenticated
    if (!isAuthenticated || !accessToken) {
      toast({
        title: "Sign In Required",
        description: "Please sign in to start your subscription",
        variant: "destructive",
      });
      navigate('/auth');
      return null;
    }

    setLoading(true);
    setError(null);

    try {
      const endpoint = type === 'trial' ? '/payments/start-trial' : '/payments/create-checkout-session';
      
      const payload = type === 'trial' 
        ? {}
        : {
            plan_type: 'premium',
            billing_cycle: billingCycle,
            success_url: `${window.location.origin}/dashboard?payment=success`,
            cancel_url: `${window.location.origin}/pricing?payment=cancelled`,
          };

      const response = await fetch(`${API_BASE_URL}/api/v1${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to create session');
      }

      const data = await response.json();

      if (type === 'trial') {
        toast({
          title: "🎉 Trial Started!",
          description: data.message || "Your 7-day free trial is now active",
        });
        // Refresh user data to update subscription status
        window.location.reload();
        return null;
      } else {
        // Redirect to Stripe checkout
        if (data.url) {
          window.location.href = data.url;
          return data;
        } else {
          throw new Error('No checkout URL provided');
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create checkout session';
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
      return null;
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, toast, navigate]);

  const handlePaymentSuccess = useCallback(async () => {
    toast({
      title: "✅ Payment Successful!",
      description: "Your subscription is now active. Enjoy unlimited access!",
    });
    // Refresh user subscription status
    setTimeout(() => window.location.href = '/dashboard', 2000);
  }, [toast]);

  const handlePaymentCancelled = useCallback(async () => {
    toast({
      title: "Payment Cancelled",
      description: "You can try again anytime. Your free trial is always available!",
      variant: "destructive",
    });
  }, [toast]);

  const getSubscriptionStatus = useCallback(async () => {
    if (!isAuthenticated) {
      return null;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/payments/subscription`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch subscription');
      }

      return await response.json();
    } catch (err) {
      console.error('Error fetching subscription:', err);
      return null;
    }
  }, [isAuthenticated]);

  const manageSubscription = useCallback(async () => {
    toast({
      title: "Coming Soon",
      description: "Subscription management portal is coming soon",
    });
  }, [toast]);

  return {
    loading,
    error,
    checkoutUrl: null,
    createCheckoutSession,
    handlePaymentSuccess,
    handlePaymentCancelled,
    manageSubscription,
    getSubscriptionStatus,
    clearError: () => setError(null),
  };
}
