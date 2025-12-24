/**
 * Authentication Context
 * Manages user state, tokens, and authentication operations
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { authAPI, UserResponse, SignUpRequest, SignInRequest } from '@/integrations/auth-api';

export interface AuthContextType {
  user: UserResponse | null;
  loading: boolean;
  isAuthenticated: boolean;
  accessToken: string | null;
  refreshToken: string | null;

  // Auth operations
  signUp: (data: SignUpRequest) => Promise<void>;
  signIn: (data: SignInRequest) => Promise<void>;
  loginWithGoogle: (response: any) => Promise<void>;
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<boolean>;
  refreshUserProfile: () => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_STORAGE_KEY = 'auth_tokens';
const USER_STORAGE_KEY = 'auth_user';
const SUBSCRIPTION_STORAGE_KEY = 'user_subscription';

// Use sessionStorage for security - tokens cleared when browser is closed
const storage = sessionStorage;

export interface StoredTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);

  // Load tokens and user from sessionStorage on mount
  useEffect(() => {
    const loadStoredAuth = async () => {
      try {
        const storedTokens = storage.getItem(TOKEN_STORAGE_KEY);
        const storedUser = storage.getItem(USER_STORAGE_KEY);

        if (storedTokens && storedUser) {
          const tokens: StoredTokens = JSON.parse(storedTokens);

          // Check if token is expired
          if (tokens.expiresAt && tokens.expiresAt < Date.now()) {
            // Token expired, try to refresh
            const refreshed = await refreshAccessTokenInternal(tokens.refreshToken);
            if (!refreshed) {
              // Refresh failed, clear storage
              storage.removeItem(TOKEN_STORAGE_KEY);
              storage.removeItem(USER_STORAGE_KEY);
              setLoading(false);
              return;
            }
          } else {
            // Token still valid, restore it
            setAccessToken(tokens.accessToken);
            setRefreshToken(tokens.refreshToken);
            setUser(JSON.parse(storedUser));
            
            // Refresh user profile in background to get latest subscription_tier
            // This ensures navbar shows correct subscription after payment
            setTimeout(async () => {
              try {
                const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
                  headers: { 'Authorization': `Bearer ${tokens.accessToken}` },
                });
                if (response.ok) {
                  const freshUser: UserResponse = await response.json();
                  storage.setItem(USER_STORAGE_KEY, JSON.stringify(freshUser));
                  setUser(freshUser);
                  console.log('🔄 User profile refreshed on load:', freshUser.subscription_tier);
                }
              } catch (error) {
                console.error('Failed to refresh user profile on load:', error);
              }
            }, 500); // Small delay to not block initial render
          }
        }
      } catch (error) {
        console.error('Failed to load stored auth:', error);
        storage.removeItem(TOKEN_STORAGE_KEY);
        storage.removeItem(USER_STORAGE_KEY);
      } finally {
        setLoading(false);
      }
    };

    loadStoredAuth();
  }, []);

  // Store tokens with expiration time
  const storeTokens = (access: string, refresh: string, expiresIn: number) => {
    const tokens: StoredTokens = {
      accessToken: access,
      refreshToken: refresh,
      expiresAt: Date.now() + expiresIn * 1000,
    };
    storage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(tokens));
    setAccessToken(access);
    setRefreshToken(refresh);
  };

  const storeUser = (userData: UserResponse) => {
    storage.setItem(USER_STORAGE_KEY, JSON.stringify(userData));
    // Also store subscription data if available
    if (userData.subscription) {
      storage.setItem(SUBSCRIPTION_STORAGE_KEY, JSON.stringify(userData.subscription));
    }
    setUser(userData);
  };

  const clearAuth = () => {
    storage.removeItem(TOKEN_STORAGE_KEY);
    storage.removeItem(USER_STORAGE_KEY);
    storage.removeItem(SUBSCRIPTION_STORAGE_KEY);
    setUser(null);
    setAccessToken(null);
    setRefreshToken(null);
  };

  // Claim orphaned price alerts (alerts created before login with user's email)
  const claimOrphanedAlerts = async (token: string) => {
    try {
      await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/price-alerts/claim-orphaned`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      // Silently claim alerts, don't throw errors if it fails
    } catch (error) {
      console.error('Failed to claim orphaned alerts:', error);
    }
  };

  // Internal refresh token function
  const refreshAccessTokenInternal = async (
    token: string
  ): Promise<boolean> => {
    try {
      const response = await authAPI.refreshToken(token);
      storeTokens(response.access_token, response.refresh_token, response.expires_in);
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      return false;
    }
  };

  // Public refresh token function
  const refreshAccessToken = async (): Promise<boolean> => {
    if (!refreshToken) return false;
    return refreshAccessTokenInternal(refreshToken);
  };

  const signUp = async (data: SignUpRequest) => {
    setLoading(true);
    try {
      const response = await authAPI.signUp(data);
      storeTokens(response.token.access_token, response.token.refresh_token, response.token.expires_in);
      storeUser(response.user);
      // Claim any orphaned alerts created before signup
      await claimOrphanedAlerts(response.token.access_token);
    } catch (error) {
      clearAuth();
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const signIn = async (data: SignInRequest) => {
    setLoading(true);
    try {
      const response = await authAPI.signIn(data);
      storeTokens(response.token.access_token, response.token.refresh_token, response.token.expires_in);
      storeUser(response.user);
      // Claim any orphaned alerts created before login
      await claimOrphanedAlerts(response.token.access_token);
    } catch (error) {
      clearAuth();
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const loginWithGoogle = async (response: any) => {
    setLoading(true);
    try {
      // Extract token and user from Google OAuth response
      storeTokens(response.token.access_token, response.token.refresh_token, response.token.expires_in);
      storeUser(response.user);
    } catch (error) {
      clearAuth();
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    if (accessToken) {
      try {
        await authAPI.logout(accessToken);
      } catch (error) {
        console.error('Logout API error:', error);
        // Still clear local auth even if API call fails
      }
    }
    clearAuth();
  };

  const changePassword = async (currentPassword: string, newPassword: string) => {
    if (!accessToken) {
      throw new Error('Not authenticated');
    }

    await authAPI.changePassword(accessToken, {
      current_password: currentPassword,
      new_password: newPassword,
    });
  };

  const refreshUserProfile = async () => {
    if (!accessToken) {
      console.warn('No access token available for profile refresh');
      return;
    }

    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to refresh user profile');
      }

      const userData: UserResponse = await response.json();
      storeUser(userData);
      console.log('✅ User profile refreshed:', userData);
    } catch (error) {
      console.error('Failed to refresh user profile:', error);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user && !!accessToken,
        accessToken,
        refreshToken,
        signUp,
        signIn,
        loginWithGoogle,
        logout,
        refreshAccessToken,
        refreshUserProfile,
        changePassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
};
