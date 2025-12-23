import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import toast from 'react-hot-toast';

export const GoogleOAuthCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { loginWithGoogle } = useAuth();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const code = searchParams.get('code');
        const error = searchParams.get('error');
        const errorDescription = searchParams.get('error_description');

        if (error) {
          toast.error(errorDescription || error || 'Google authentication was cancelled.');
          navigate('/auth?tab=signin');
          return;
        }

        if (!code) {
          toast.error('Missing authorization code.');
          navigate('/auth?tab=signin');
          return;
        }

        // Show loading toast
        const loadingToast = toast.loading('Authenticating with Google...');

        // Call backend to exchange code for tokens
        const response = await fetch(`/api/v1/auth/google/callback?code=${encodeURIComponent(code)}`, {
          method: 'POST',
        });

        if (!response.ok) {
          const errorData = await response.json();
          toast.dismiss(loadingToast);
          toast.error(errorData.detail || 'Authentication failed');
          navigate('/auth?tab=signin');
          return;
        }

        const data = await response.json();
        
        // Use AuthContext to store tokens and user info properly
        if (data.token && data.user) {
          try {
            // Call loginWithGoogle to store tokens via AuthContext
            await loginWithGoogle(data);
            
            toast.dismiss(loadingToast);
            toast.success(`Welcome ${data.user.full_name || data.user.email}! 🎉`);

            // Redirect to home after a short delay
            setTimeout(() => {
              navigate('/');
            }, 1500);
          } catch (authError) {
            toast.dismiss(loadingToast);
            toast.error('Failed to save authentication. Please try again.');
            console.error('Auth context error:', authError);
            navigate('/auth?tab=signin');
          }
        }
      } catch (error: any) {
        console.error('OAuth callback error:', error);
        toast.error(error.message || 'An error occurred during authentication.');
        setTimeout(() => {
          navigate('/auth?tab=signin');
        }, 1500);
      } finally {
        setIsLoading(false);
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Authenticating with Google</CardTitle>
          </CardHeader>
          <CardContent className="flex justify-center py-8">
            <div className="flex flex-col items-center gap-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              <p className="text-sm text-muted-foreground">Please wait...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return null;
};

export default GoogleOAuthCallback;


