import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import toast from 'react-hot-toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PasswordStrengthMeter, calculatePasswordStrength } from './PasswordStrengthMeter';
import { Mail, Lock, User } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL;

const GoogleIcon = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>
    <path d="M9.003 18c2.43 0 4.467-.806 5.956-2.18L12.05 13.56c-.806.54-1.836.86-3.047.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9.003 18z" fill="#34A853"/>
    <path d="M3.964 10.712c-.18-.54-.282-1.117-.282-1.71 0-.593.102-1.17.282-1.71V4.96H.957C.347 6.175 0 7.55 0 9.002c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
    <path d="M9.003 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.464.891 11.426 0 9.003 0 5.482 0 2.438 2.017.957 4.958L3.964 7.29c.708-2.127 2.692-3.71 5.036-3.71z" fill="#EA4335"/>
  </svg>
);

interface AuthFormProps {
  mode?: 'signin' | 'signup';
  isRecovery?: boolean;
}

export const AuthForm = ({ mode = 'signin', isRecovery = false }: AuthFormProps) => {
  const navigate = useNavigate();
  const { signIn, signUp } = useAuth();

  // Sign In State
  const [signinEmail, setSigninEmail] = useState('');
  const [signinPassword, setSigninPassword] = useState('');
  const [signinLoading, setSigninLoading] = useState(false);

  // Sign Up State
  const [signupName, setSignupName] = useState('');
  const [signupEmail, setSignupEmail] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [signupConfirmPassword, setSignupConfirmPassword] = useState('');
  const [signupLoading, setSignupLoading] = useState(false);

  // Reset State
  const [resetEmail, setResetEmail] = useState('');
  const [resetLoading, setResetLoading] = useState(false);

  const [currentMode, setCurrentMode] = useState<'signin' | 'signup' | 'reset'>(mode);

  const handleGoogleSignIn = async () => {
    try {
      const loadingToast = toast.loading('Connecting to Google...');
      
      // Get Google login URL from backend
      const response = await fetch(`${API_URL}/api/v1/auth/google/login`);
      const data = await response.json();
      
      toast.dismiss(loadingToast);
      
      if (data.auth_url) {
        // Redirect to Google OAuth consent screen
        window.location.href = data.auth_url;
      }
    } catch (error: any) {
      console.error('Google sign-in error:', error);
      toast.error('Failed to connect to Google. Please try again.');
    }
  };

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!signinEmail || !signinPassword) {
      toast.error('Please enter your email and password.');
      return;
    }

    setSigninLoading(true);

    try {
      await signIn({ email: signinEmail.trim(), password: signinPassword });

      toast.success("Welcome back! 👋");

      setTimeout(() => {
        navigate('/');
      }, 500);

      setSigninEmail('');
      setSigninPassword('');
    } catch (error: any) {
      console.error('Sign in error:', error);
      toast.error(error?.message || 'Please check your email and password.');
    } finally {
      setSigninLoading(false);
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!signupEmail || !signupPassword || !signupName) {
      toast.error('Please fill in all fields.');
      return;
    }

    if (signupName.trim().length < 2) {
      toast.error('Please enter a valid full name.');
      return;
    }

    if (signupPassword !== signupConfirmPassword) {
      toast.error("Passwords don't match. Please ensure both passwords are the same.");
      return;
    }

    const passwordStrengthResult = calculatePasswordStrength(signupPassword);
    if (!passwordStrengthResult.isValid) {
      toast.error('Password too weak. Please create a stronger password.');
      return;
    }

    setSignupLoading(true);

    try {
      await signUp({
        email: signupEmail.trim(),
        password: signupPassword,
        full_name: signupName.trim(),
      });

      toast.success('Account created! 🎉');

      setSignupEmail('');
      setSignupPassword('');
      setSignupConfirmPassword('');
      setSignupName('');

      setTimeout(() => {
        navigate('/');
      }, 500);
    } catch (error: any) {
      console.error('Sign up error:', error);
      toast.error(error?.message || 'Failed to create account. Please try again.');
    } finally {
      setSignupLoading(false);
    }
  };

  const handlePasswordReset = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!resetEmail) {
      toast.error('Please enter your email address.');
      return;
    }

    setResetLoading(true);

    try {
      toast.success('Check your email for password reset instructions.');
      setResetEmail('');
    } catch (error: any) {
      toast.error(error?.message || 'Failed to send reset link.');
    } finally {
      setResetLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-background px-4 py-8">
      {/* Desktop */}
      <div className="hidden md:block w-full max-w-md">
        <Card className="border shadow-none bg-background">
          <CardHeader className="text-center space-y-3 pb-6">
            <CardTitle className="text-2xl font-bold">Welcome to IMO</CardTitle>
            <p className="text-sm text-muted-foreground">AI-powered product research</p>
            <div className="flex items-center gap-2 text-xs text-muted-foreground justify-center">
              <svg className="h-4 w-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>No credit card required</span>
            </div>
          </CardHeader>

          <CardContent>
            <Tabs value={currentMode} onValueChange={(val: any) => setCurrentMode(val)} className="w-full">
              <TabsList className="grid w-full grid-cols-3 mb-6 bg-muted/50">
                <TabsTrigger value="signin" className="rounded-md text-sm">Sign In</TabsTrigger>
                <TabsTrigger value="signup" className="rounded-md text-sm">Sign Up</TabsTrigger>
                <TabsTrigger value="reset" className="rounded-md text-sm">Reset</TabsTrigger>
              </TabsList>

              {/* Sign In Tab */}
              <TabsContent value="signin" className="space-y-4">
                <form onSubmit={handleSignIn} className="space-y-4">
                  <div className="flex flex-col gap-2">
                    <Label htmlFor="email" className="text-sm font-medium">Email</Label>
                    <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <Input
                        id="email"
                        type="email"
                        placeholder="Enter your email"
                        value={signinEmail}
                        onChange={(e) => setSigninEmail(e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 bg-transparent"
                        disabled={signinLoading}
                        required
                      />
                    </div>
                  </div>

                  <div className="flex flex-col gap-2">
                    <Label htmlFor="password" className="text-sm font-medium">Password</Label>
                    <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                      <Lock className="h-4 w-4 text-muted-foreground" />
                      <Input
                        id="password"
                        type="password"
                        placeholder="Enter your password"
                        value={signinPassword}
                        onChange={(e) => setSigninPassword(e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 bg-transparent"
                        disabled={signinLoading}
                        required
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <input 
                        type="checkbox" 
                        id="remember" 
                        className="h-4 w-4 rounded border-input"
                      />
                      <Label htmlFor="remember" className="font-normal cursor-pointer text-sm">
                        Remember me
                      </Label>
                    </div>
                    <button className="text-primary hover:underline text-sm">
                      Forgot password?
                    </button>
                  </div>

                  <Button 
                    type="submit" 
                    disabled={signinLoading}
                    className="w-full h-10 bg-primary hover:bg-primary/90 rounded-lg font-medium"
                  >
                    {signinLoading ? 'Signing in...' : 'Sign In'}
                  </Button>
                </form>

                <div className="relative my-4">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-muted" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-background px-2 text-muted-foreground">or</span>
                  </div>
                </div>

                <Button 
                  type="button"
                  variant="outline" 
                  className="w-full h-10 rounded-lg flex items-center justify-center gap-2 border-muted hover:bg-muted/50"
                  onClick={handleGoogleSignIn}
                  disabled={signinLoading}
                >
                  <GoogleIcon />
                  <span className="text-sm">Continue with Google</span>
                </Button>

                <p className="text-center text-xs text-muted-foreground mt-4">
                  Don't have an account?{" "}
                  <button 
                    onClick={() => setCurrentMode('signup')}
                    className="text-primary hover:underline font-medium"
                  >
                    Sign Up
                  </button>
                </p>
              </TabsContent>

              {/* Sign Up Tab */}
              <TabsContent value="signup" className="space-y-4">
                <form onSubmit={handleSignUp} className="space-y-4">
                  <div className="flex flex-col gap-2">
                    <Label htmlFor="signup-name" className="text-sm font-medium">Full Name</Label>
                    <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                      <User className="h-4 w-4 text-muted-foreground" />
                      <Input
                        id="signup-name"
                        type="text"
                        placeholder="John Doe"
                        value={signupName}
                        onChange={(e) => setSignupName(e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 bg-transparent"
                        disabled={signupLoading}
                        required
                      />
                    </div>
                  </div>

                  <div className="flex flex-col gap-2">
                    <Label htmlFor="signup-email" className="text-sm font-medium">Email</Label>
                    <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <Input
                        id="signup-email"
                        type="email"
                        placeholder="you@example.com"
                        value={signupEmail}
                        onChange={(e) => setSignupEmail(e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 bg-transparent"
                        disabled={signupLoading}
                        required
                      />
                    </div>
                  </div>

                  <div className="flex flex-col gap-2">
                    <Label htmlFor="signup-password" className="text-sm font-medium">Password</Label>
                    <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                      <Lock className="h-4 w-4 text-muted-foreground" />
                      <Input
                        id="signup-password"
                        type="password"
                        placeholder="••••••••"
                        value={signupPassword}
                        onChange={(e) => setSignupPassword(e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 bg-transparent"
                        disabled={signupLoading}
                        required
                      />
                    </div>
                    <PasswordStrengthMeter password={signupPassword} />
                  </div>

                  <div className="flex flex-col gap-2">
                    <Label htmlFor="signup-confirm" className="text-sm font-medium">Confirm Password</Label>
                    <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                      <Lock className="h-4 w-4 text-muted-foreground" />
                      <Input
                        id="signup-confirm"
                        type="password"
                        placeholder="••••••••"
                        value={signupConfirmPassword}
                        onChange={(e) => setSignupConfirmPassword(e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 bg-transparent"
                        disabled={signupLoading}
                        required
                      />
                    </div>
                    {signupConfirmPassword && signupPassword !== signupConfirmPassword && (
                      <p className="text-xs text-destructive">Passwords do not match</p>
                    )}
                  </div>

                  <Button 
                    type="submit" 
                    disabled={signupLoading}
                    className="w-full h-10 bg-primary hover:bg-primary/90 rounded-lg font-medium"
                  >
                    {signupLoading ? 'Creating account...' : 'Sign Up'}
                  </Button>
                </form>

                <div className="relative my-4">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-muted" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-background px-2 text-muted-foreground">or</span>
                  </div>
                </div>

                <Button 
                  type="button"
                  variant="outline" 
                  className="w-full h-10 rounded-lg flex items-center justify-center gap-2 border-muted hover:bg-muted/50"
                  onClick={handleGoogleSignIn}
                  disabled={signupLoading}
                >
                  <GoogleIcon />
                  <span className="text-sm">Continue with Google</span>
                </Button>

                <p className="text-center text-xs text-muted-foreground mt-4">
                  Already have an account?{" "}
                  <button 
                    onClick={() => setCurrentMode('signin')}
                    className="text-primary hover:underline font-medium"
                  >
                    Sign In
                  </button>
                </p>
              </TabsContent>

              {/* Reset Tab */}
              <TabsContent value="reset" className="space-y-4">
                <form onSubmit={handlePasswordReset} className="space-y-4">
                  <div className="flex flex-col gap-2">
                    <Label htmlFor="reset-email" className="text-sm font-medium">Email</Label>
                    <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <Input
                        id="reset-email"
                        type="email"
                        placeholder="Enter your email"
                        value={resetEmail}
                        onChange={(e) => setResetEmail(e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 bg-transparent"
                        disabled={resetLoading}
                        required
                      />
                    </div>
                  </div>

                  <Button 
                    type="submit" 
                    disabled={resetLoading}
                    className="w-full h-10 bg-primary hover:bg-primary/90 rounded-lg font-medium"
                  >
                    {resetLoading ? 'Sending...' : 'Send Reset Link'}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>

      {/* Mobile */}
      <div className="md:hidden w-full max-w-sm">
        <Card className="border shadow-none bg-background">
          <CardHeader className="text-center space-y-3 pb-6">
            <CardTitle className="text-xl font-bold">Welcome to IMO</CardTitle>
            <p className="text-xs text-muted-foreground">AI-powered product research</p>
            <div className="flex items-center gap-2 text-xs text-muted-foreground justify-center">
              <svg className="h-3 w-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>No credit card required</span>
            </div>
          </CardHeader>

          <CardContent>
            <Tabs value={currentMode} onValueChange={(val: any) => setCurrentMode(val)} className="w-full">
              <TabsList className="grid w-full grid-cols-3 mb-6 bg-muted/50 h-10">
                <TabsTrigger value="signin" className="rounded-md text-xs">Sign In</TabsTrigger>
                <TabsTrigger value="signup" className="rounded-md text-xs">Sign Up</TabsTrigger>
                <TabsTrigger value="reset" className="rounded-md text-xs">Reset</TabsTrigger>
              </TabsList>

              {/* Mobile Sign In */}
              <TabsContent value="signin" className="space-y-4">
                <form onSubmit={handleSignIn} className="space-y-4">
                  <div className="flex flex-col gap-2">
                    <Label htmlFor="mobile-email" className="text-xs font-medium">Email</Label>
                    <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <Input
                        id="mobile-email"
                        type="email"
                        placeholder="Enter your email"
                        value={signinEmail}
                        onChange={(e) => setSigninEmail(e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 bg-transparent text-sm"
                        disabled={signinLoading}
                        required
                      />
                    </div>
                  </div>

                  <div className="flex flex-col gap-2">
                    <Label htmlFor="mobile-password" className="text-xs font-medium">Password</Label>
                    <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                      <Lock className="h-4 w-4 text-muted-foreground" />
                      <Input
                        id="mobile-password"
                        type="password"
                        placeholder="Enter your password"
                        value={signinPassword}
                        onChange={(e) => setSigninPassword(e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 bg-transparent text-sm"
                        disabled={signinLoading}
                        required
                      />
                    </div>
                  </div>

                  <Button 
                    type="submit" 
                    disabled={signinLoading}
                    className="w-full h-10 bg-primary hover:bg-primary/90 rounded-lg font-medium text-sm"
                  >
                    {signinLoading ? 'Signing in...' : 'Sign In'}
                  </Button>
                </form>

                <div className="relative my-4">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-muted" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-background px-2 text-muted-foreground">or</span>
                  </div>
                </div>

                <Button 
                  type="button"
                  variant="outline" 
                  className="w-full h-10 rounded-lg flex items-center justify-center gap-2 border-muted hover:bg-muted/50 text-sm"
                  onClick={handleGoogleSignIn}
                  disabled={signinLoading}
                >
                  <GoogleIcon />
                  <span>Continue with Google</span>
                </Button>
              </TabsContent>

              {/* Mobile Sign Up */}
              <TabsContent value="signup" className="space-y-4">
                <form onSubmit={handleSignUp} className="space-y-4">
                  <div className="flex flex-col gap-2">
                    <Label htmlFor="mobile-signup-name" className="text-xs font-medium">Full Name</Label>
                    <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                      <User className="h-4 w-4 text-muted-foreground" />
                      <Input
                        id="mobile-signup-name"
                        type="text"
                        placeholder="John Doe"
                        value={signupName}
                        onChange={(e) => setSignupName(e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 bg-transparent text-sm"
                        disabled={signupLoading}
                        required
                      />
                    </div>
                  </div>

                  <div className="flex flex-col gap-2">
                    <Label htmlFor="mobile-signup-email" className="text-xs font-medium">Email</Label>
                    <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <Input
                        id="mobile-signup-email"
                        type="email"
                        placeholder="you@example.com"
                        value={signupEmail}
                        onChange={(e) => setSignupEmail(e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 bg-transparent text-sm"
                        disabled={signupLoading}
                        required
                      />
                    </div>
                  </div>

                  <div className="flex flex-col gap-2">
                    <Label htmlFor="mobile-signup-password" className="text-xs font-medium">Password</Label>
                    <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                      <Lock className="h-4 w-4 text-muted-foreground" />
                      <Input
                        id="mobile-signup-password"
                        type="password"
                        placeholder="••••••••"
                        value={signupPassword}
                        onChange={(e) => setSignupPassword(e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 bg-transparent text-sm"
                        disabled={signupLoading}
                        required
                      />
                    </div>
                    <PasswordStrengthMeter password={signupPassword} />
                  </div>

                  <div className="flex flex-col gap-2">
                    <Label htmlFor="mobile-signup-confirm" className="text-xs font-medium">Confirm Password</Label>
                    <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                      <Lock className="h-4 w-4 text-muted-foreground" />
                      <Input
                        id="mobile-signup-confirm"
                        type="password"
                        placeholder="••••••••"
                        value={signupConfirmPassword}
                        onChange={(e) => setSignupConfirmPassword(e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 bg-transparent text-sm"
                        disabled={signupLoading}
                        required
                      />
                    </div>
                    {signupConfirmPassword && signupPassword !== signupConfirmPassword && (
                      <p className="text-xs text-destructive">Passwords do not match</p>
                    )}
                  </div>

                  <Button 
                    type="submit" 
                    disabled={signupLoading}
                    className="w-full h-10 bg-primary hover:bg-primary/90 rounded-lg font-medium text-sm"
                  >
                    {signupLoading ? 'Creating account...' : 'Sign Up'}
                  </Button>
                </form>

                <div className="relative my-4">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-muted" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-background px-2 text-muted-foreground">or</span>
                  </div>
                </div>

                <Button 
                  type="button"
                  variant="outline" 
                  className="w-full h-10 rounded-lg flex items-center justify-center gap-2 border-muted hover:bg-muted/50 text-sm"
                  onClick={handleGoogleSignIn}
                  disabled={signupLoading}
                >
                  <GoogleIcon />
                  <span>Continue with Google</span>
                </Button>
              </TabsContent>

              {/* Mobile Reset */}
              <TabsContent value="reset" className="space-y-4">
                <form onSubmit={handlePasswordReset} className="space-y-4">
                  <div className="flex flex-col gap-2">
                    <Label htmlFor="mobile-reset-email" className="text-xs font-medium">Email</Label>
                    <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <Input
                        id="mobile-reset-email"
                        type="email"
                        placeholder="Enter your email"
                        value={resetEmail}
                        onChange={(e) => setResetEmail(e.target.value)}
                        className="border-0 shadow-none focus-visible:ring-0 bg-transparent text-sm"
                        disabled={resetLoading}
                        required
                      />
                    </div>
                  </div>

                  <Button 
                    type="submit" 
                    disabled={resetLoading}
                    className="w-full h-10 bg-primary hover:bg-primary/90 rounded-lg font-medium text-sm"
                  >
                    {resetLoading ? 'Sending...' : 'Send Reset Link'}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
