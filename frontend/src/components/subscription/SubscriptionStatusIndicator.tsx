import { Badge } from '@/components/ui/badge';
import { Crown, Sparkles, CheckCircle, Clock } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useUserAccess } from '@/hooks/useUserAccess';
import { useEffect, useState } from 'react';

interface SubscriptionStatusIndicatorProps {
  variant?: 'badge' | 'text' | 'icon';
  size?: 'sm' | 'md' | 'lg';
  showDetails?: boolean;
  className?: string;
}

export function SubscriptionStatusIndicator({
  variant = 'badge',
  size = 'md',
  showDetails = false,
  className = ''
}: SubscriptionStatusIndicatorProps) {
  const { user } = useAuth();
  const { subscription, hasActiveSubscription } = useUserAccess();
  const [forceUpdate, setForceUpdate] = useState(0);
  
  // DIRECT READ from sessionStorage as fallback
  const getDirectSubscriptionTier = () => {
    try {
      const storedUser = sessionStorage.getItem('auth_user');
      if (storedUser) {
        const userData = JSON.parse(storedUser);
        return userData.subscription_tier;
      }
    } catch (e) {
      console.error('Failed to read from sessionStorage:', e);
    }
    return null;
  };
  
  const directTier = getDirectSubscriptionTier();
  
  // Force re-render when user changes
  useEffect(() => {
    setForceUpdate(prev => prev + 1);
  }, [user?.subscription_tier, subscription?.plan_type, directTier]);
  
  // Debug logging - check what we're actually getting
  console.log('SubscriptionStatusIndicator [render]:', {
    user_subscription_tier: user?.subscription_tier,
    directTier_from_sessionStorage: directTier,
    subscription_plan_type: subscription?.plan_type,
    subscription_is_active: subscription?.is_active,
    forceUpdate
  });
  
  // Check subscription status - prioritize direct sessionStorage read, then user.subscription_tier, then subscription API
  const isTrial = (directTier === 'trial') || (user?.subscription_tier === 'trial') || (subscription?.plan_type === 'trial' && subscription?.is_active);
  const isPremium = (directTier === 'premium') || (user?.subscription_tier === 'premium') || (subscription?.plan_type === 'premium' && subscription?.is_active);

  const sizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  const iconSizes = {
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
    lg: 'h-5 w-5'
  };

  if (variant === 'icon') {
    return (
      <div className={`flex items-center ${className}`}>
        {isPremium ? (
          <Crown className={`${iconSizes[size]} text-yellow-500`} />
        ) : isTrial ? (
          <Clock className={`${iconSizes[size]} text-blue-500`} />
        ) : (
          <Sparkles className={`${iconSizes[size]} text-muted-foreground`} />
        )}
      </div>
    );
  }

  if (variant === 'text') {
    return (
      <div className={`flex items-center space-x-1 ${sizeClasses[size]} ${className}`}>
        {isPremium ? (
          <>
            <Crown className={iconSizes[size]} />
            <span className="font-medium text-yellow-600">Premium</span>
          </>
        ) : isTrial ? (
          <>
            <Clock className={iconSizes[size]} />
            <span className="font-medium text-blue-600">Trial</span>
          </>
        ) : (
          <>
            <Sparkles className={iconSizes[size]} />
            <span className="text-muted-foreground">Free</span>
          </>
        )}
      </div>
    );
  }

  // Default badge variant
  return (
    <Badge 
      variant={hasActiveSubscription ? "default" : "secondary"}
      className={`${className} ${
        isPremium 
          ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-white border-0' 
          : isTrial
          ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white border-0'
          : ''
      }`}
    >
      {isPremium ? (
        <>
          <Crown className={`mr-1 ${iconSizes[size]}`} />
          Premium
        </>
      ) : isTrial ? (
        <>
          <Clock className={`mr-1 ${iconSizes[size]}`} />
          Premium Trial
        </>
      ) : (
        <>
          <Sparkles className={`mr-1 ${iconSizes[size]}`} />
          Free
        </>
      )}
    </Badge>
  );
}