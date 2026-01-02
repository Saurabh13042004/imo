import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Lock, CheckCircle } from 'lucide-react';
import { PasswordStrengthMeter, calculatePasswordStrength } from '@/components/auth/PasswordStrengthMeter';

const API_URL = import.meta.env.VITE_API_URL;

export default function ResetPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [validToken, setValidToken] = useState<boolean | null>(null);
  const [resetEmail, setResetEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [resetSuccess, setResetSuccess] = useState(false);

  // Verify token on component mount
  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setValidToken(false);
        return;
      }

      try {
        const response = await fetch(`${API_URL}/api/v1/auth/verify-reset-token?token=${token}`);
        const data = await response.json();

        if (data.valid && data.email) {
          setValidToken(true);
          setResetEmail(data.email);
        } else {
          setValidToken(false);
        }
      } catch (error) {
        console.error('Token verification error:', error);
        setValidToken(false);
      }
    };

    verifyToken();
  }, [token]);

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newPassword || !confirmPassword) {
      toast.error('Please fill in all fields.');
      return;
    }

    if (newPassword !== confirmPassword) {
      toast.error("Passwords don't match. Please ensure both passwords are the same.");
      return;
    }

    const passwordStrengthResult = calculatePasswordStrength(newPassword);
    if (!passwordStrengthResult.isValid) {
      toast.error('Password too weak. Please create a stronger password.');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          new_password: newPassword,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setResetSuccess(true);
        toast.success('Password reset successfully! Redirecting to login...');
        
        setTimeout(() => {
          navigate('/auth');
        }, 2000);
      } else {
        toast.error(data.detail || 'Failed to reset password. Please try again.');
      }
    } catch (error: any) {
      console.error('Password reset error:', error);
      toast.error('Failed to reset password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (validToken === null) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background px-4 py-8">
        <Card className="border shadow-none bg-background max-w-md w-full">
          <CardContent className="pt-8">
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
            <p className="text-center text-muted-foreground mt-4">Verifying reset link...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!validToken) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background px-4 py-8">
        <Card className="border shadow-none bg-background max-w-md w-full">
          <CardHeader className="text-center space-y-3 pb-6">
            <CardTitle className="text-2xl font-bold">Invalid Reset Link</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground text-center">
              This password reset link is invalid or has expired. Please request a new one.
            </p>
            <Button
              onClick={() => navigate('/auth')}
              className="w-full h-10 bg-primary hover:bg-primary/90 rounded-lg font-medium"
            >
              Go to Login
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (resetSuccess) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background px-4 py-8">
        <Card className="border shadow-none bg-background max-w-md w-full">
          <CardHeader className="text-center space-y-3 pb-6">
            <div className="flex justify-center mb-4">
              <CheckCircle className="h-16 w-16 text-green-600" />
            </div>
            <CardTitle className="text-2xl font-bold">Password Reset Successful</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground text-center">
              Your password has been reset successfully. You can now log in with your new password.
            </p>
            <p className="text-xs text-muted-foreground text-center">
              Redirecting to login page...
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-background px-4 py-8">
      <Card className="border shadow-none bg-background max-w-md w-full">
        <CardHeader className="text-center space-y-3 pb-6">
          <CardTitle className="text-2xl font-bold">Reset Your Password</CardTitle>
          <p className="text-sm text-muted-foreground">Enter your new password below</p>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleResetPassword} className="space-y-4">
            <div className="flex flex-col gap-2">
              <Label htmlFor="email" className="text-sm font-medium">
                Email Address
              </Label>
              <Input
                id="email"
                type="email"
                value={resetEmail}
                disabled
                className="border-0 shadow-none focus-visible:ring-0 bg-muted text-sm"
              />
              <p className="text-xs text-muted-foreground">
                This is the email associated with your account
              </p>
            </div>

            <div className="flex flex-col gap-2">
              <Label htmlFor="new-password" className="text-sm font-medium">
                New Password
              </Label>
              <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                <Lock className="h-4 w-4 text-muted-foreground" />
                <Input
                  id="new-password"
                  type="password"
                  placeholder="••••••••"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="border-0 shadow-none focus-visible:ring-0 bg-transparent text-sm"
                  disabled={loading}
                  required
                />
              </div>
              <PasswordStrengthMeter password={newPassword} />
            </div>

            <div className="flex flex-col gap-2">
              <Label htmlFor="confirm-password" className="text-sm font-medium">
                Confirm Password
              </Label>
              <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                <Lock className="h-4 w-4 text-muted-foreground" />
                <Input
                  id="confirm-password"
                  type="password"
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="border-0 shadow-none focus-visible:ring-0 bg-transparent text-sm"
                  disabled={loading}
                  required
                />
              </div>
              {confirmPassword && newPassword !== confirmPassword && (
                <p className="text-xs text-destructive">Passwords do not match</p>
              )}
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full h-10 bg-primary hover:bg-primary/90 rounded-lg font-medium"
            >
              {loading ? 'Resetting Password...' : 'Reset Password'}
            </Button>
          </form>

          <div className="mt-6 pt-6 border-t border-muted">
            <p className="text-center text-xs text-muted-foreground">
              Remember your password?{' '}
              <button
                onClick={() => navigate('/auth')}
                className="text-primary hover:underline font-medium"
              >
                Sign In
              </button>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
