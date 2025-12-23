import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle, Crown, Home, Search, Loader2 } from 'lucide-react';
import { useUserAccess } from '@/hooks/useUserAccess';
import { useSubscriptionFlow } from '@/hooks/useSubscriptionFlow';
import { useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import { API_BASE_URL } from '@/config/api';

export default function PaymentSuccess() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { refreshAccess, loading, subscription } = useUserAccess();
  const { handlePaymentSuccess } = useSubscriptionFlow();
  const { accessToken } = useAuth();
  const [isRefreshing, setIsRefreshing] = useState(true);
  const [pollingCount, setPollingCount] = useState(0);
  const [subscriptionStatus, setSubscriptionStatus] = useState<string>('free');
  const [checkoutCompleted, setCheckoutCompleted] = useState(false);

  const sessionId = searchParams.get('session_id');

  // Call manual checkout completion endpoint (for localhost where webhooks don't work)
  useEffect(() => {
    const completeCheckout = async () => {
      if (sessionId && accessToken && !checkoutCompleted) {
        try {
          console.log('Calling manual checkout completion for session:', sessionId);
          const response = await fetch(`${API_BASE_URL}/api/v1/payments/checkout-complete`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${accessToken}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_id: sessionId })
          });
          
          if (response.ok) {
            console.log('Manual checkout completion successful');
            setCheckoutCompleted(true);
            // Immediately refresh access to get updated subscription
            await refreshAccess();
          } else {
            const errorData = await response.json();
            console.error('Manual checkout completion failed:', errorData);
          }
        } catch (error) {
          console.error('Error calling manual checkout completion:', error);
        }
      }
    };
    
    completeCheckout();
  }, [sessionId, accessToken, checkoutCompleted, refreshAccess]);

  // Poll subscription status until webhook processes
  useEffect(() => {
    const pollSubscription = async () => {
      if (!isRefreshing || pollingCount >= 20) return; // Stop after 20 attempts (40 seconds)

      await refreshAccess();
      setPollingCount(prev => prev + 1);
    };

    if (isRefreshing) {
      const interval = setInterval(pollSubscription, 2000); // Poll every 2 seconds
      return () => clearInterval(interval);
    }
  }, [isRefreshing, pollingCount, refreshAccess]);

  // Update subscription status when data changes
  useEffect(() => {
    if (subscription?.is_active && (subscription.plan_type === 'trial' || subscription.plan_type === 'premium')) {
      setSubscriptionStatus(subscription.plan_type);
      setIsRefreshing(false);
    }
  }, [subscription]);

  useEffect(() => {
    const handleSuccess = async () => {
      setIsRefreshing(true);

      // Get payment type and category from URL params
      const paymentType = searchParams.get('type') as 'subscription' | 'unlock' | null;
      const category = searchParams.get('category');

      // Initial wait for Stripe webhook to process
      await new Promise(resolve => setTimeout(resolve, 3000));

      if (paymentType) {
        await handlePaymentSuccess(paymentType, category || undefined, sessionId || undefined);
      }

      // Start polling for subscription updates
      await refreshAccess();

      // Invalidate all product search queries to ensure fresh access permissions
      queryClient.invalidateQueries({
        queryKey: ['productSearch']
      });

      // Also invalidate search access queries
      queryClient.invalidateQueries({
        queryKey: ['search-access']
      });
    };

    handleSuccess();
  }, [searchParams, refreshAccess, handlePaymentSuccess, queryClient, sessionId]);

  if (isRefreshing || loading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-6 py-16 max-w-2xl">
          <Card className="text-center">
            <CardContent className="pt-8 pb-8">
              <div className="flex justify-center mb-6">
                <Loader2 className="h-12 w-12 animate-spin text-primary" />
              </div>
              <h1 className="text-2xl font-bold mb-4">Processing Payment...</h1>
              <p className="text-muted-foreground mb-4">
                We're updating your account with the new subscription. This may take a moment.
              </p>
              {pollingCount > 0 && (
                <div className="mt-4 space-y-2">
                  <p className="text-sm text-muted-foreground">Waiting for confirmation from Stripe...</p>
                  <div className="flex justify-center gap-1">
                    {[...Array(3)].map((_, i) => (
                      <div
                        key={i}
                        className="w-2 h-2 bg-primary rounded-full animate-bounce"
                        style={{ animationDelay: `${i * 0.15}s` }}
                      />
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-6 py-16 max-w-2xl">
        <Card className="text-center border-green-200 bg-green-50">
          <CardHeader>
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-green-100 rounded-full">
                <CheckCircle className="h-12 w-12 text-green-600" />
              </div>
            </div>
            <CardTitle className="text-2xl text-green-900">Payment Successful!</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-green-800">
              <p className="text-lg mb-2">
                🎉 Welcome to {subscriptionStatus === 'trial' ? 'your 7-day free trial' : 'IMO Premium'}!
              </p>
              <p className="text-sm opacity-90">
                Your payment has been processed successfully. You now have {subscriptionStatus === 'trial' ? 'trial' : 'premium'} access to all features.
              </p>
              {subscription && (
                <div className="mt-4 p-3 bg-green-100 rounded-lg">
                  <p className="text-sm font-semibold text-green-700">
                    Status: {subscription.plan_type.toUpperCase()}
                  </p>
                  {subscription.trial_end && (
                    <p className="text-xs text-green-600 mt-1">
                      Trial ends: {new Date(subscription.trial_end).toLocaleDateString()}
                    </p>
                  )}
                  {subscription.days_remaining && (
                    <p className="text-xs text-green-600 mt-1">
                      {subscription.days_remaining} days remaining
                    </p>
                  )}
                </div>
              )}
            </div>

            {sessionId && (
              <div className="bg-green-100 p-4 rounded-lg">
                <p className="text-xs text-green-600 font-mono">
                  Session ID: {sessionId}
                </p>
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <Button
                onClick={() => {
                  // Navigate back to search with current query if available
                  // Add forceRefresh parameter to ensure fresh data after payment
                  const lastQuery = searchParams.get('category') || searchParams.get('query') || '';
                  const searchUrl = lastQuery
                    ? `/search?query=${encodeURIComponent(lastQuery)}&forceRefresh=true`
                    : '/search?forceRefresh=true';
                  navigate(searchUrl);
                }}
                className="flex items-center justify-center"
              >
                <Search className="mr-2 h-4 w-4" />
                Continue Searching
              </Button>
              <Button
                variant="outline"
                onClick={() => navigate('/profile')}
                className="flex items-center justify-center"
              >
                <Crown className="mr-2 h-4 w-4" />
                View Subscription
              </Button>
            </div>

            <Button
              variant="ghost"
              onClick={() => navigate('/')}
              className="w-full"
            >
              <Home className="mr-2 h-4 w-4" />
              Return Home
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}