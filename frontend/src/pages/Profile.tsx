import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import toast from 'react-hot-toast';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { PaymentTransactionsCard } from '@/components/account/PaymentTransactionsCard';
import User from 'lucide-react/dist/esm/icons/user';
import Mail from 'lucide-react/dist/esm/icons/mail';
import Lock from 'lucide-react/dist/esm/icons/lock';
import Image from 'lucide-react/dist/esm/icons/image';
import LogOut from 'lucide-react/dist/esm/icons/log-out';
import Unlink from 'lucide-react/dist/esm/icons/unlink';
import LinkIcon from 'lucide-react/dist/esm/icons/link';

const API_URL = import.meta.env.VITE_API_URL;

interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  subscription_tier: string;
  access_level: string;
  oauth_provider?: string;
  created_at: string;
}

const GoogleIcon = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>
    <path d="M9.003 18c2.43 0 4.467-.806 5.956-2.18L12.05 13.56c-.806.54-1.836.86-3.047.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9.003 18z" fill="#34A853"/>
    <path d="M3.964 10.712c-.18-.54-.282-1.117-.282-1.71 0-.593.102-1.17.282-1.71V4.96H.957C.347 6.175 0 7.55 0 9.002c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
    <path d="M9.003 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.464.891 11.426 0 9.003 0 5.482 0 2.438 2.017.957 4.958L3.964 7.29c.708-2.127 2.692-3.71 5.036-3.71z" fill="#EA4335"/>
  </svg>
);

export default function Profile() {
  const navigate = useNavigate();
  const { user, isAuthenticated, accessToken, signOut, loading: authLoading } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // Form states
  const [fullName, setFullName] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    // Wait for auth context to finish loading
    if (authLoading) {
      return;
    }

    // Check if user is authenticated
    if (!isAuthenticated || !accessToken) {
      navigate('/auth');
      return;
    }

    // If we have user from context, use it
    if (user) {
      setProfile(user);
      setFullName(user.full_name);
      setLoading(false);
    } else {
      // Otherwise fetch it
      fetchProfile();
    }
  }, [authLoading, isAuthenticated, accessToken, user, navigate]);

  const fetchProfile = async () => {
    try {
      if (!accessToken) {
        navigate('/auth');
        return;
      }

      const response = await fetch('/api/v1/profile/me', {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch profile');
      }

      const data = await response.json();
      setProfile(data);
      setFullName(data.full_name);
    } catch (error) {
      console.error('Error fetching profile:', error);
      toast.error('Failed to load profile');
      navigate('/auth');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUploadPhoto = async () => {
    if (!selectedFile) {
      toast.error('Please select a photo');
      return;
    }

    if (!accessToken) {
      toast.error('Authentication required');
      return;
    }

    setIsSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch('/api/v1/profile/upload-photo', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload photo');
      }

      const data = await response.json();
      setProfile(prev => prev ? { ...prev, avatar_url: data.avatar_url } : null);
      setSelectedFile(null);
      setPreviewUrl(null);
      toast.success('Photo uploaded successfully! 📸');
    } catch (error) {
      console.error('Error uploading photo:', error);
      toast.error('Failed to upload photo');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!accessToken) {
      toast.error('Authentication required');
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch('/api/v1/profile/update', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ full_name: fullName }),
      });

      if (!response.ok) {
        throw new Error('Failed to update profile');
      }

      const data = await response.json();
      setProfile(data);
      toast.success('Profile updated successfully! ✨');
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error('Failed to update profile');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (!accessToken) {
      toast.error('Authentication required');
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch('/api/v1/profile/change-password', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to change password');
      }

      toast.success('Password changed successfully! 🔒');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error: any) {
      console.error('Error changing password:', error);
      toast.error(error.message || 'Failed to change password');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDisconnectOAuth = async () => {
    if (!window.confirm('Are you sure you want to disconnect your Google account?')) {
      return;
    }

    if (!accessToken) {
      toast.error('Authentication required');
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch('/api/v1/profile/disconnect-oauth', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to disconnect OAuth');
      }

      setProfile(prev => prev ? { ...prev, oauth_provider: undefined } : null);
      toast.success('Google account disconnected! 🔓');
    } catch (error: any) {
      console.error('Error disconnecting OAuth:', error);
      toast.error(error.message || 'Failed to disconnect Google account');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleLogout = async () => {
    try {
      await signOut();
      navigate('/auth');
    } catch (error) {
      console.error('Logout error:', error);
      toast.error('Failed to logout');
    }
  };

  if (loading || authLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground mb-4">Profile not found</p>
            <Button onClick={() => navigate('/auth')} className="w-full">
              Go to Sign In
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container max-w-4xl mx-auto py-12 px-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div className="flex items-start space-x-6">
            {/* Avatar */}
            <div className="relative group">
              {profile.avatar_url ? (
                <img
                  src={profile.avatar_url}
                  alt={profile.full_name}
                  className="h-24 w-24 rounded-full object-cover border-4 border-primary/20"
                />
              ) : (
                <div className="h-24 w-24 rounded-full bg-gradient-to-br from-blue-500/20 to-cyan-500/20 flex items-center justify-center border-4 border-primary/20">
                  <User className="h-12 w-12 text-blue-500" />
                </div>
              )}
            </div>

            {/* User Info */}
            <div>
              <h1 className="text-3xl font-bold">{profile.full_name}</h1>
              <p className="text-muted-foreground flex items-center gap-2 mt-2">
                <Mail className="h-4 w-4" />
                {profile.email}
              </p>
              <div className="flex gap-4 mt-4">
                <div className="flex flex-col">
                  <span className="text-xs text-muted-foreground uppercase tracking-wider">Plan</span>
                  <span className="font-semibold capitalize">{profile.subscription_tier}</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-xs text-muted-foreground uppercase tracking-wider">Level</span>
                  <span className="font-semibold capitalize">{profile.access_level}</span>
                </div>
              </div>
            </div>
          </div>

          <Button variant="destructive" onClick={handleLogout}>
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="personal" className="space-y-4">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="personal">Personal</TabsTrigger>
            <TabsTrigger value="photo">Photo</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="reviews">My Reviews</TabsTrigger>
            <TabsTrigger value="payments">Payments</TabsTrigger>
            <TabsTrigger value="oauth">Connected Apps</TabsTrigger>
          </TabsList>

          {/* Personal Info Tab */}
          <TabsContent value="personal" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Personal Information</CardTitle>
                <CardDescription>Update your personal details</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleUpdateProfile} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="full_name">Full Name</Label>
                    <Input
                      id="full_name"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Enter your full name"
                      disabled={isSubmitting}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email (Read-only)</Label>
                    <Input
                      id="email"
                      value={profile.email}
                      disabled
                      className="bg-muted"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Account Created</Label>
                    <Input
                      value={new Date(profile.created_at).toLocaleDateString()}
                      disabled
                      className="bg-muted"
                    />
                  </div>

                  <Button type="submit" disabled={isSubmitting} className="w-full">
                    {isSubmitting ? 'Updating...' : 'Update Profile'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Photo Tab */}
          <TabsContent value="photo" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Profile Photo</CardTitle>
                <CardDescription>Upload or update your profile picture</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Current Photo */}
                {profile.avatar_url && (
                  <div className="space-y-2">
                    <Label>Current Photo</Label>
                    <div className="relative w-32 h-32 mx-auto">
                      <img
                        src={profile.avatar_url}
                        alt={profile.full_name}
                        className="w-full h-full rounded-lg object-cover border border-muted"
                      />
                    </div>
                  </div>
                )}

                {/* Upload Area */}
                <div className="space-y-2">
                  <Label htmlFor="photo">Choose Photo</Label>
                  <div className="relative border-2 border-dashed border-muted-foreground/30 rounded-lg p-6 hover:border-primary/50 transition cursor-pointer">
                    <input
                      id="photo"
                      type="file"
                      accept="image/*"
                      onChange={handleFileSelect}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                      disabled={isSubmitting}
                    />
                    <div className="text-center">
                      <Image className="h-8 w-8 text-muted-foreground/50 mx-auto mb-2" />
                      <p className="text-sm text-muted-foreground">
                        Click to upload or drag and drop
                      </p>
                      <p className="text-xs text-muted-foreground/60 mt-1">
                        PNG, JPG, GIF (Max 10MB)
                      </p>
                    </div>
                  </div>
                </div>

                {/* Preview */}
                {previewUrl && (
                  <div className="space-y-2">
                    <Label>Preview</Label>
                    <div className="relative w-32 h-32 mx-auto">
                      <img
                        src={previewUrl}
                        alt="Preview"
                        className="w-full h-full rounded-lg object-cover border border-primary"
                      />
                    </div>
                  </div>
                )}

                {selectedFile && (
                  <Button
                    onClick={handleUploadPhoto}
                    disabled={isSubmitting}
                    className="w-full"
                  >
                    {isSubmitting ? 'Uploading...' : 'Upload Photo'}
                  </Button>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Change Password</CardTitle>
                <CardDescription>Update your password to keep your account secure</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleChangePassword} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="current_password">Current Password</Label>
                    <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                      <Lock className="h-4 w-4 text-muted-foreground" />
                      <input
                        id="current_password"
                        type="password"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        placeholder="Enter current password"
                        disabled={isSubmitting}
                        className="flex-1 bg-transparent outline-none border-0"
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="new_password">New Password</Label>
                    <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                      <Lock className="h-4 w-4 text-muted-foreground" />
                      <input
                        id="new_password"
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="Enter new password"
                        disabled={isSubmitting}
                        className="flex-1 bg-transparent outline-none border-0"
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirm_password">Confirm Password</Label>
                    <div className="flex items-center gap-2 border rounded-lg px-3 h-10 focus-within:ring-2 focus-within:ring-ring">
                      <Lock className="h-4 w-4 text-muted-foreground" />
                      <input
                        id="confirm_password"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="Confirm new password"
                        disabled={isSubmitting}
                        className="flex-1 bg-transparent outline-none border-0"
                        required
                      />
                    </div>
                  </div>

                  <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                      Password must be at least 8 characters, contain 1 uppercase letter and 1 digit.
                    </p>
                  </div>

                  <Button type="submit" disabled={isSubmitting} className="w-full">
                    {isSubmitting ? 'Updating...' : 'Change Password'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Payments Tab */}
          <TabsContent value="payments" className="space-y-4">
            <PaymentTransactionsCard />
          </TabsContent>

          {/* OAuth Tab */}
          <TabsContent value="oauth" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Connected Applications</CardTitle>
                <CardDescription>Manage your connected social accounts</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Google */}
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <GoogleIcon />
                    <div>
                      <p className="font-semibold">Google</p>
                      <p className="text-sm text-muted-foreground">
                        {profile.oauth_provider === 'google'
                          ? 'Connected ✓'
                          : 'Not connected'}
                      </p>
                    </div>
                  </div>

                  {profile.oauth_provider === 'google' ? (
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={handleDisconnectOAuth}
                      disabled={isSubmitting}
                    >
                      <Unlink className="h-4 w-4 mr-2" />
                      Disconnect
                    </Button>
                  ) : (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={async () => {
                        try {
                          const response = await fetch('/api/v1/auth/google/login');
                          const data = await response.json();
                          if (data.auth_url) {
                            window.location.href = data.auth_url;
                          }
                        } catch (error) {
                          toast.error('Failed to connect Google');
                        }
                      }}
                      disabled={isSubmitting}
                    >
                      <LinkIcon className="h-4 w-4 mr-2" />
                      Connect
                    </Button>
                  )}
                </div>

                <div className="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-lg p-3">
                  <p className="text-sm text-amber-700 dark:text-amber-300">
                    Connecting a social account allows you to sign in using that account and enhances your profile with social data.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* My Reviews Tab */}
          <TabsContent value="reviews" className="space-y-4">
            <MyReviewsTab />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

// My Reviews Tab Component
function MyReviewsTab() {
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);
  const { accessToken } = useAuth();

  useEffect(() => {
    const fetchReviews = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/api/v1/reviews/my-submissions`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch reviews');
        }

        const data = await response.json();
        setReviews(data);
      } catch (error) {
        console.error('Error fetching reviews:', error);
        toast.error('Failed to load your reviews');
      } finally {
        setLoading(false);
      }
    };

    if (accessToken) {
      fetchReviews();
    }
  }, [accessToken, refreshKey]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 dark:bg-green-950 text-green-800 dark:text-green-300';
      case 'pending':
        return 'bg-yellow-100 dark:bg-yellow-950 text-yellow-800 dark:text-yellow-300';
      case 'rejected':
        return 'bg-red-100 dark:bg-red-950 text-red-800 dark:text-red-300';
      default:
        return 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-300';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return '✅';
      case 'pending':
        return '⏳';
      case 'rejected':
        return '❌';
      default:
        return '📝';
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="pt-6 flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading your reviews...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (reviews.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>My Video Reviews</CardTitle>
          <CardDescription>Your submitted video reviews and their approval status</CardDescription>
        </CardHeader>
        <CardContent className="text-center py-12">
          <p className="text-muted-foreground mb-4">You haven't submitted any video reviews yet.</p>
          <p className="text-sm text-muted-foreground">Start by uploading a video review on any product page!</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>My Video Reviews</CardTitle>
            <CardDescription>Your submitted video reviews and their approval status</CardDescription>
          </div>
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => setRefreshKey(k => k + 1)}
          >
            🔄 Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {reviews.map((review) => (
            <div 
              key={review.id}
              className="border rounded-lg p-4 hover:bg-accent/50 transition-colors"
            >
              {/* Header with status */}
              <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg flex items-center gap-2">
                    {review.title}
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(review.status)}`}>
                      {getStatusIcon(review.status)} {review.status.charAt(0).toUpperCase() + review.status.slice(1)}
                    </span>
                  </h3>
                </div>
                <div className="flex items-center gap-1 ml-4">
                  <span className="text-lg">{'⭐'.repeat(review.rating)}</span>
                  <span className="text-sm text-muted-foreground">({review.rating}/5)</span>
                </div>
              </div>

              {/* Description */}
              <p className="text-sm text-foreground/80 mb-3 line-clamp-2">
                {review.description}
              </p>

              {/* Meta info */}
              <div className="flex gap-4 text-xs text-muted-foreground mb-3 flex-wrap">
                <div>
                  📅 Submitted: {new Date(review.created_at).toLocaleDateString()}
                </div>
                {review.updated_at && review.updated_at !== review.created_at && (
                  <div>
                    🔄 Updated: {new Date(review.updated_at).toLocaleDateString()}
                  </div>
                )}
              </div>

              {/* Video preview / status message */}
              {review.status === 'approved' && review.video_url ? (
                <div className="rounded-lg bg-black/10 dark:bg-white/10 p-2 mb-3">
                  <video 
                    controls 
                    className="w-full rounded-lg max-h-64"
                    src={review.video_url}
                  />
                </div>
              ) : (
                <div className="rounded-lg bg-muted p-4 mb-3 text-center">
                  <div className="text-sm text-muted-foreground">
                    {review.status === 'pending' && (
                      <>
                        <p className="font-medium mb-1">⏳ Review Pending Approval</p>
                        <p className="text-xs">We're reviewing your video against our guidelines. This usually takes up to 1 business day.</p>
                      </>
                    )}
                    {review.status === 'rejected' && (
                      <>
                        <p className="font-medium mb-1">❌ Review Rejected</p>
                        <p className="text-xs">Your video didn't meet our guidelines. Please check our guidelines and submit a new one.</p>
                      </>
                    )}
                    {review.status === 'approved' && !review.video_url && (
                      <>
                        <p className="font-medium mb-1">✅ Approved</p>
                        <p className="text-xs">Your review has been approved!</p>
                      </>
                    )}
                  </div>
                </div>
              )}

              {/* Action buttons */}
              {review.status === 'rejected' && (
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="w-full">
                    📝 Review Guidelines
                  </Button>
                  <Button variant="default" size="sm" className="w-full">
                    🎬 Submit Again
                  </Button>
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
