import { useCallback, useState } from 'react';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/hooks/useAuth';
import { useNavigate } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_URL';

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
      // Both trial and paid subscriptions now use create-checkout-session
      const payload = {
        plan_type: type === 'trial' ? 'trial' : 'premium',
        billing_cycle: billingCycle,
        success_url: `${window.location.origin}/payment-success?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${window.location.origin}/payment-canceled`,
      };

      const response = await fetch(`${API_BASE_URL}/api/v1/payments/create-checkout-session`, {
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

      // Redirect to Stripe checkout for both trial and paid
      if (data.url) {
        window.location.href = data.url;
        return data;
      } else {
        throw new Error('No checkout URL provided');
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

  const handlePaymentSuccess = useCallback(async (
    paymentType?: 'subscription' | 'unlock',
    category?: string,
    sessionId?: string
  ) => {
    toast({
      title: "✅ Payment Successful!",
      description: paymentType === 'subscription' 
        ? "Your subscription is now active. Enjoy unlimited access!"
        : "Payment processed successfully!",
    });
    
    // Log for debugging
    console.log('Payment success:', { paymentType, category, sessionId });
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
    if (!isAuthenticated || !accessToken) {
      toast({
        title: "Sign In Required",
        description: "Please sign in to manage your subscription",
        variant: "destructive",
      });
      navigate('/auth');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/payments/create-portal-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          return_url: window.location.origin + '/subscription-manager',
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to open billing portal');
      }

      const data = await response.json();

      if (data.url) {
        window.location.href = data.url;
      } else {
        throw new Error('No portal URL provided');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to open billing portal';
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, accessToken, toast, navigate]);

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
