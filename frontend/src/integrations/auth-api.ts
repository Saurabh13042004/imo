/**
 * Authentication API Client
 * Handles all authentication-related API calls
 */

import { API_BASE_URL } from '@/config/api';

export interface SignUpRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface SignInRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  user: UserResponse;
  token: TokenResponse;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  subscription_tier: string;
  access_level: string;
  roles: string[];
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

class AuthAPI {
  private baseUrl = API_BASE_URL;
  private authPath = '/api/v1/auth';

  /**
   * Sign up a new user
   */
  async signUp(data: SignUpRequest): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}${this.authPath}/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Sign up failed');
    }

    return response.json();
  }

  /**
   * Sign in with email and password
   */
  async signIn(data: SignInRequest): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}${this.authPath}/signin`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Sign in failed');
    }

    return response.json();
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await fetch(`${this.baseUrl}${this.authPath}/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    return response.json();
  }

  /**
   * Get current user profile
   */
  async getCurrentUser(accessToken: string): Promise<UserResponse> {
    const response = await fetch(`${this.baseUrl}${this.authPath}/me`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Unauthorized');
      }
      throw new Error('Failed to fetch user profile');
    }

    return response.json();
  }

  /**
   * Change user password
   */
  async changePassword(
    accessToken: string,
    data: ChangePasswordRequest
  ): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}${this.authPath}/change-password`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to change password');
    }

    return response.json();
  }

  /**
   * Sign out (client-side only, server doesn't maintain sessions)
   */
  async logout(accessToken: string): Promise<{ message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}${this.authPath}/logout`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        console.warn('Logout API call failed, clearing local tokens anyway');
      }

      return { message: 'Logged out successfully' };
    } catch (error) {
      console.warn('Logout error:', error);
      // Don't throw - logout should always succeed on client
      return { message: 'Logged out successfully' };
    }
  }
}

export const authAPI = new AuthAPI();
