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
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<boolean>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_STORAGE_KEY = 'auth_tokens';
const USER_STORAGE_KEY = 'auth_user';

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
    setUser(userData);
  };

  const clearAuth = () => {
    storage.removeItem(TOKEN_STORAGE_KEY);
    storage.removeItem(USER_STORAGE_KEY);
    setUser(null);
    setAccessToken(null);
    setRefreshToken(null);
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
        logout,
        refreshAccessToken,
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
