import { Check, Crown, Sparkles, Star } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useUserAccess } from '@/hooks/useUserAccess';
import { useSubscriptionFlow } from '@/hooks/useSubscriptionFlow';
import { useAuth } from '@/hooks/useAuth';
import { useState } from 'react';

export function HighConversionPricing() {
  const { hasActiveSubscription, refetchAccess } = useUserAccess();
  const { createCheckoutSession, loading } = useSubscriptionFlow();
  const { user, isAuthenticated } = useAuth();
  const [loadingType, setLoadingType] = useState<'trial' | 'subscription' | null>(null);
  const [billingPeriod, setBillingPeriod] = useState<'yearly' | 'monthly'>('yearly');

  const monthlyPrice = 9.99;
  const yearlyPrice = 6.99;
  const displayPrice = billingPeriod === 'yearly' ? yearlyPrice : monthlyPrice;

  const handleStartTrial = async () => {
    setLoadingType('trial');
    try {
      // Trial now goes through Stripe checkout, so it will redirect
      await createCheckoutSession('trial', 'monthly');
    } finally {
      setLoadingType(null);
    }
  };

  const handleSubscribe = async () => {
    setLoadingType('subscription');
    try {
      await createCheckoutSession('subscription', billingPeriod);
    } finally {
      setLoadingType(null);
    }
  };

  return (
    <section className="py-24 bg-gradient-to-br from-muted/30 via-background to-muted/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <Badge variant="outline" className="mb-6 px-4 py-2">
            <Sparkles className="mr-2 h-4 w-4" />
            Plans & Pricing
          </Badge>
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">
            Choose Your Plan
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            Flexible pricing for every budget. 7-day free trial, cancel anytime, no card needed.
          </p>
        </div>

        {/* Billing Period Toggle */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <span className={`text-sm font-medium cursor-pointer transition-colors ${billingPeriod === 'monthly' ? 'text-foreground' : 'text-muted-foreground'}`} onClick={() => setBillingPeriod('monthly')}>
            Monthly
          </span>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              className="sr-only peer"
              checked={billingPeriod === 'yearly'}
              onChange={(e) => setBillingPeriod(e.target.checked ? 'yearly' : 'monthly')}
            />
            <div className="w-11 h-6 bg-muted rounded-full peer peer-checked:bg-primary transition-colors"></div>
            <div className="absolute left-1 top-1 bg-background w-4 h-4 rounded-full transition-transform peer-checked:translate-x-5"></div>
          </label>
          <span className={`text-sm font-medium cursor-pointer transition-colors ${billingPeriod === 'yearly' ? 'text-foreground' : 'text-muted-foreground'}`} onClick={() => setBillingPeriod('yearly')}>
            Yearly
          </span>
          {billingPeriod === 'yearly' && (
            <Badge className="bg-green-100 text-green-700 border-green-200">
              Save 30%
            </Badge>
          )}
        </div>

        {/* Two-Tier Pricing */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl mx-auto mb-16">
          {/* Free Tier */}
          <Card className="relative border-2 hover:shadow-lg transition-all duration-300">
            <CardHeader className="text-center pb-8">
              <div className="mx-auto mb-4 p-3 bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center">
                <Star className="h-8 w-8 text-blue-600" />
              </div>
              <CardTitle className="text-2xl mb-2">Free Forever</CardTitle>
              <div className="flex items-center justify-center gap-1">
                <span className="text-4xl font-bold">$0</span>
                <span className="text-muted-foreground">always</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Trust Score (Filtered Fake Reviews)</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Review Summaries</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Cross Platform Text, Short Form, Long Form Reviews</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Price Comparison (Limited)</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-muted-foreground">❌ Price Drop Alerts</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-muted-foreground">❌ AI Powered Sentiment Analysis</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-muted-foreground">❌ Cross Site Inventory Analysis</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-muted-foreground">❌ AI chatbot + review interaction</span>
                </li>
              </ul>
              
              {user && !hasActiveSubscription ? (
                <Button variant="outline" className="w-full" disabled>
                  <Star className="mr-2 h-4 w-4" />
                  Current Plan
                </Button>
              ) : !user ? (
                <Button variant="outline" className="w-full" disabled>
                  <Star className="mr-2 h-4 w-4" />
                  Free Plan
                </Button>
              ) : (
                <Button variant="outline" className="w-full" disabled>
                  <Star className="mr-2 h-4 w-4" />
                  Free Plan
                </Button>
              )}
              
              <p className="text-sm text-center text-muted-foreground">
                Perfect for casual browsing
              </p>
            </CardContent>
          </Card>

          {/* Premium Subscription */}
          <Card className="relative border-2 border-yellow-300 bg-gradient-to-br from-yellow-50/50 via-orange-50/30 to-background hover:shadow-xl transition-all duration-300">
            <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
              <Badge className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-4 py-1.5 text-sm font-medium">
                <Crown className="mr-1 h-4 w-4" />
                Most Popular
              </Badge>
            </div>
            
            <CardHeader className="text-center pb-8 pt-8">
              <div className="mx-auto mb-4 p-3 bg-gradient-to-br from-yellow-100 to-orange-100 rounded-full w-16 h-16 flex items-center justify-center">
                <Crown className="h-8 w-8 text-orange-600" />
              </div>
              <CardTitle className="text-2xl mb-2">Premium Unlimited</CardTitle>
              <div className="flex items-baseline justify-center gap-1 mb-1">
                <span className="text-4xl font-bold">${displayPrice.toFixed(2)}</span>
                <span className="text-muted-foreground">/month</span>
              </div>
              {billingPeriod === 'yearly' ? (
                <p className="text-sm text-muted-foreground">Billed annually at $83.88/year</p>
              ) : (
                <p className="text-sm text-muted-foreground">Billed monthly at $9.99/month</p>
              )}
              {billingPeriod === 'monthly' && (
                <p className="text-xs text-green-600 font-medium mt-1">✨ 7-day free trial included</p>
              )}
            </CardHeader>
            
            <CardContent className="space-y-6">
              <ul className="space-y-4">
                {billingPeriod === 'monthly' && (
                  <li className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="font-medium">7-day free trial included</span>
                  </li>
                )}
                {billingPeriod === 'yearly' && (
                  <li className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="font-medium">Save 30% with annual billing</span>
                  </li>
                )}
                <li className="flex items-start gap-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Trust Score (Filtered Fake Reviews)</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Review Summaries</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Cross Platform Text, Short Form, Long Form Reviews</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Price Comparison (Unlimited)</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Price Drop Alerts (Unlimited)</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>AI Powered Sentiment Analysis</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Cross Site Inventory Analysis</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>AI chatbot + review interaction</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="font-medium">Cancel anytime, no commitment</span>
                </li>
              </ul>
              
              {hasActiveSubscription ? (
                <Button disabled className="w-full bg-gradient-to-r from-yellow-500 to-orange-500">
                  <Crown className="mr-2 h-4 w-4" />
                  Current Plan
                </Button>
              ) : billingPeriod === 'monthly' ? (
                // Monthly: Show trial button only
                <div className="space-y-3">
                  <Button 
                    className="w-full bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white font-medium shadow-lg hover:shadow-xl transition-all"
                    onClick={handleStartTrial}
                    disabled={loadingType !== null || loading}
                  >
                    <Crown className="mr-2 h-4 w-4" />
                    {loadingType === 'trial' ? 'Starting Trial...' : 'Start 7-Day Free Trial'}
                  </Button>
                  <p className="text-xs text-center text-muted-foreground">
                    Then $9.99/month after trial ends
                  </p>
                </div>
              ) : (
                // Yearly: Show subscribe button only (no trial)
                <div className="space-y-3">
                  <Button 
                    className="w-full bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white font-medium shadow-lg hover:shadow-xl transition-all"
                    onClick={handleSubscribe}
                    disabled={loadingType !== null || loading}
                  >
                    <Crown className="mr-2 h-4 w-4" />
                    {loadingType === 'subscription' ? 'Processing...' : 'Subscribe Now'}
                  </Button>
                  <p className="text-xs text-center text-muted-foreground">
                    Billed $83.88 annually • Save 30%
                  </p>
                </div>
              )}
              
              <p className="text-sm text-center text-muted-foreground">
                Best value for power users
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Value Proposition */}
        <div className="text-center space-y-8">
          <h3 className="text-2xl font-semibold">Why Choose IMO?</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="flex flex-col items-center space-y-4 p-6">
              <div className="p-4 bg-blue-100 rounded-full">
                <Sparkles className="h-8 w-8 text-blue-600" />
              </div>
              <h4 className="text-lg font-semibold">AI-Powered Insights</h4>
              <p className="text-muted-foreground text-center leading-relaxed">
                Get intelligent product analysis and comparisons powered by advanced AI
              </p>
            </div>
            <div className="flex flex-col items-center space-y-4 p-6">
              <div className="p-4 bg-green-100 rounded-full">
                <Check className="h-8 w-8 text-green-600" />
              </div>
              <h4 className="text-lg font-semibold">No Hidden Fees</h4>
              <p className="text-muted-foreground text-center leading-relaxed">
                Transparent pricing with no surprise charges. Pay only for what you need
              </p>
            </div>
            <div className="flex flex-col items-center space-y-4 p-6">
              <div className="p-4 bg-purple-100 rounded-full">
                <Crown className="h-8 w-8 text-purple-600" />
              </div>
              <h4 className="text-lg font-semibold">Instant Access</h4>
              <p className="text-muted-foreground text-center leading-relaxed">
                Unlock content immediately after purchase. Start exploring right away
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
