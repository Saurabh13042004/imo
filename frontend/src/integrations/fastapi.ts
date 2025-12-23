/**
 * FastAPI Backend Configuration
 * Centralized API endpoint configuration and HTTP client
 */

import { getSessionId } from '@/utils/sessionUtils';

const API_URL =
  process.env.NODE_ENV === "production"
    ? "https://imo-6g57.onrender.com"
    : "http://localhost:8000";

/**
 * Get auth token from sessionStorage
 */
function getAuthToken(): string | null {
  try {
    const tokens = sessionStorage.getItem('auth_tokens');
    if (tokens) {
      const parsed = JSON.parse(tokens);
      return parsed.accessToken;
    }
  } catch (error) {
    console.error('Error getting auth token:', error);
  }
  return null;
}

/**
 * Generic fetch wrapper for API calls
 */
async function apiCall<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_URL}${endpoint}`;
  
  // Get session ID for guest users
  const sessionId = getSessionId();
  
  // Get auth token if available
  const authToken = getAuthToken();

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        "X-Session-ID": sessionId,  // Always send session ID
        ...(authToken && { "Authorization": `Bearer ${authToken}` }),  // Include auth token if available
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        errorText || `API Error: ${response.status} ${response.statusText}`
      );
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`API call failed: ${endpoint}`, error);
    throw error;
  }
}

/**
 * Search Products
 */
export interface SearchRequest {
  keyword: string;
  zipcode?: string;
  country?: string;
  city?: string;
  language?: string;
}

export interface SearchResponse {
  success: boolean;
  keyword: string;
  zipcode: string;
  total_results: number;
  results: Array<{
    id?: string;
    title: string;
    price?: string | number;
    image_url?: string;
    url?: string;
    source: string;
    source_id?: string;
    rating?: string | number;
    review_count?: number;
    description?: string;
    brand?: string;
    category?: string;
    availability?: string;
    asin?: string;
    created_at?: string;
    updated_at?: string;
  }>;
}

export async function searchProducts(
  request: SearchRequest
): Promise<SearchResponse> {
  return apiCall<SearchResponse>("/api/v1/search", {
    method: "POST",
    body: JSON.stringify({
      keyword: request.keyword,
      zipcode: request.zipcode || "60607",
      country: request.country || "United States",
      city: request.city || "",
      language: request.language || "en",
    }),
  });
}

/**
 * Get Trending Products
 */
export async function getTrendingProducts(limit: number = 10) {
  return apiCall(`/api/products/trending?limit=${limit}`, {
    method: "GET",
  });
}

/**
 * List Products
 */
export interface ListProductsResponse {
  success: boolean;
  products: Array<any>;
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export async function listProducts(
  page: number = 1,
  limit: number = 20,
  category?: string,
  sortBy: string = "relevance"
): Promise<ListProductsResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
    sort_by: sortBy,
  });

  if (category) {
    params.append("category", category);
  }

  return apiCall<ListProductsResponse>(`/products?${params.toString()}`, {
    method: "GET",
  });
}

/**
 * Get Product Details
 */
export async function getProductDetail(productId: string) {
  return apiCall(`/products/${productId}`, {
    method: "GET",
  });
}

/**
 * Get Product Basic Info
 */
export async function getProductBasic(productId: string) {
  return apiCall(`/products/${productId}`, {
    method: "GET",
  });
}

/**
 * Get Product Reviews
 */
export async function getProductReviews(productId: string) {
  return apiCall(`/products/${productId}/reviews`, {
    method: "GET",
  });
}

/**
 * Get Product Videos
 */
export async function getProductVideos(productId: string) {
  return apiCall(`/products/${productId}/videos`, {
    method: "GET",
  });
}

/**
 * Authentication
 */
export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  success: boolean;
  token: string;
  user: {
    id: string;
    email: string;
    full_name: string;
    subscription: string;
  };
}

export async function login(request: LoginRequest): Promise<AuthResponse> {
  return apiCall<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function signup(request: SignupRequest): Promise<AuthResponse> {
  return apiCall<AuthResponse>("/auth/signup", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function getCurrentUser(token: string) {
  return apiCall("/auth/me", {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

/**
 * Products - Likes
 */
export async function likeProduct(productId: string, userId: string) {
  return apiCall(`/products/${productId}/like?user_id=${userId}`, {
    method: "POST",
  });
}

export async function unlikeProduct(productId: string, userId: string) {
  return apiCall(`/products/${productId}/unlike?user_id=${userId}`, {
    method: "POST",
  });
}

export async function getUserLikedProducts(userId: string) {
  return apiCall(`/products/likes?user_id=${userId}`, {
    method: "GET",
  });
}

/**
 * Health Check
 */
export async function checkHealth() {
  return apiCall("/health", {
    method: "GET",
  });
}

/**
 * API URL getter (useful for dynamic configuration)
 */
export function getApiUrl(): string {
  return API_URL;
}

export default {
  searchProducts,
  getTrendingProducts,
  listProducts,
  getProductDetail,
  login,
  signup,
  getCurrentUser,
  likeProduct,
  unlikeProduct,
  getUserLikedProducts,
  checkHealth,
  getApiUrl,
};
