import { Badge } from '@/components/ui/badge';
import { Crown, Sparkles, CheckCircle } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

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
  
  // Check if user is logged in and has a premium subscription
  const hasActiveSubscription = user && user.subscription_tier === 'premium';

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
        {hasActiveSubscription ? (
          <Crown className={`${iconSizes[size]} text-yellow-500`} />
        ) : (
          <Sparkles className={`${iconSizes[size]} text-muted-foreground`} />
        )}
      </div>
    );
  }

  if (variant === 'text') {
    return (
      <div className={`flex items-center space-x-1 ${sizeClasses[size]} ${className}`}>
        {hasActiveSubscription ? (
          <>
            <Crown className={iconSizes[size]} />
            <span className="font-medium text-yellow-600">Premium</span>
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
        hasActiveSubscription 
          ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-white border-0' 
          : ''
      }`}
    >
      {hasActiveSubscription ? (
        <>
          <Crown className={`mr-1 ${iconSizes[size]}`} />
          Premium
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