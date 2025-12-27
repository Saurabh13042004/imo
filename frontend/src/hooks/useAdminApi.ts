import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getSessionId } from '@/utils/sessionUtils';
import { useAuth } from '@/hooks/useAuth';

interface AdminStats {
  totalUsers: number;
  totalSubscriptions: number;
  activeTrials: number;
  monthlyRevenue: number;
  totalUrls: number;
  apiCalls: number;
}

interface User {
  id: string;
  email: string;
  name: string;
  subscriptionTier: string;
  joinDate: string;
  lastActive: string;
  activeSubscription?: string;
}

interface Subscription {
  id: string;
  userId: string;
  userEmail: string;
  planType: string;
  billingCycle?: string;
  isActive: boolean;
  subscriptionStart?: string;
  subscriptionEnd?: string;
  trialStart?: string;
  trialEnd?: string;
}

interface Contact {
  id: string;
  name: string;
  email: string;
  subject: string;
  message: string;
  status?: string;
  createdAt: string;
}

interface Product {
  id: string;
  title: string;
  source: string;
  sourceId: string;
  price?: number;
  currency: string;
  rating?: number;
  reviewCount: number;
  imageUrl?: string;
  createdAt: string;
}

interface Review {
  id: string;
  productTitle?: string;
  rating: number;
  reviewTitle?: string;
  reviewText?: string;
  author?: string;
  source?: string;
  postedAt?: string;
  fetchedAt?: string;
  createdAt?: string;
}

interface ErrorLog {
  id: string;
  functionName: string;
  errorType: string;
  errorMessage: string;
  createdAt: string;
}

interface BackgroundTask {
  id: string;
  status: string;
  productsAnalyzed: number;
  totalProducts: number;
  startedAt: string;
  completedAt?: string;
}

interface PaymentTransaction {
  id: string;
  userEmail?: string;
  amount: number;
  currency: string;
  type: string;
  status: string;
  createdAt: string;
}

// Helper to make API calls
async function adminApiCall<T>(endpoint: string, authToken: string, options?: RequestInit): Promise<T> {
  const API_URL = import.meta.env.VITE_API_URL;
  const url = `${API_URL}${endpoint}`;
  
  const sessionId = getSessionId();

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-Session-ID': sessionId,
      ...(authToken && { 'Authorization': `Bearer ${authToken}` }),
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let errorMessage = `API Error: ${response.status} ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorMessage = typeof errorData.detail === 'string'
          ? errorData.detail
          : JSON.stringify(errorData.detail);
      }
    } catch {
      const errorText = await response.text();
      if (errorText) {
        errorMessage = errorText;
      }
    }
    throw new Error(errorMessage);
  }

  return response.json();
}

// Admin Stats Hook
export function useAdminStats() {
  const { accessToken } = useAuth();
  
  return useQuery({
    queryKey: ['admin-stats'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return adminApiCall<AdminStats>('/api/v1/admin/stats', accessToken);
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30 * 1000, // Refetch every 30 seconds
    enabled: !!accessToken,
  });
}

// Users List Hook
export function useAdminUsers(skip: number = 0, limit: number = 50, search?: string, subscriptionTier?: string) {
  const { accessToken } = useAuth();
  const params = new URLSearchParams();
  params.append('skip', skip.toString());
  params.append('limit', limit.toString());
  if (search) params.append('search', search);
  if (subscriptionTier) params.append('subscription_tier', subscriptionTier);

  return useQuery({
    queryKey: ['admin-users', skip, limit, search, subscriptionTier],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return adminApiCall<{ data: User[]; total: number; skip: number; limit: number }>(
        `/api/v1/admin/users?${params.toString()}`,
        accessToken
      );
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    enabled: !!accessToken,
  });
}

// Subscriptions List Hook
export function useAdminSubscriptions(skip: number = 0, limit: number = 50, status?: string) {
  const { accessToken } = useAuth();
  const params = new URLSearchParams();
  params.append('skip', skip.toString());
  params.append('limit', limit.toString());
  if (status) params.append('status', status);

  return useQuery({
    queryKey: ['admin-subscriptions', skip, limit, status],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return adminApiCall<{ data: Subscription[]; total: number; skip: number; limit: number }>(
        `/api/v1/admin/subscriptions?${params.toString()}`,
        accessToken
      );
    },
    staleTime: 2 * 60 * 1000,
    enabled: !!accessToken,
  });
}

// Contacts List Hook
export function useAdminContacts(skip: number = 0, limit: number = 50) {
  const { accessToken } = useAuth();
  const params = new URLSearchParams();
  params.append('skip', skip.toString());
  params.append('limit', limit.toString());

  return useQuery({
    queryKey: ['admin-contacts', skip, limit],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return adminApiCall<{ data: Contact[]; total: number; skip: number; limit: number }>(
        `/api/v1/admin/contacts?${params.toString()}`,
        accessToken
      );
    },
    staleTime: 2 * 60 * 1000,
    enabled: !!accessToken,
  });
}

// Products List Hook
export function useAdminProducts(skip: number = 0, limit: number = 50, source?: string) {
  const { accessToken } = useAuth();
  const params = new URLSearchParams();
  params.append('skip', skip.toString());
  params.append('limit', limit.toString());
  if (source) params.append('source', source);

  return useQuery({
    queryKey: ['admin-products', skip, limit, source],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return adminApiCall<{ data: Product[]; total: number; skip: number; limit: number }>(
        `/api/v1/admin/products?${params.toString()}`,
        accessToken
      );
    },
    staleTime: 2 * 60 * 1000,
    enabled: !!accessToken,
  });
}

// Reviews List Hook
export function useAdminReviews(skip: number = 0, limit: number = 50) {
  const { accessToken } = useAuth();
  const params = new URLSearchParams();
  params.append('skip', skip.toString());
  params.append('limit', limit.toString());

  return useQuery({
    queryKey: ['admin-reviews', skip, limit],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return adminApiCall<{ data: Review[]; total: number; skip: number; limit: number }>(
        `/api/v1/admin/reviews?${params.toString()}`,
        accessToken
      );
    },
    staleTime: 2 * 60 * 1000,
    enabled: !!accessToken,
  });
}

// Error Logs Hook
export function useAdminErrorLogs(skip: number = 0, limit: number = 50) {
  const { accessToken } = useAuth();
  const params = new URLSearchParams();
  params.append('skip', skip.toString());
  params.append('limit', limit.toString());

  return useQuery({
    queryKey: ['admin-error-logs', skip, limit],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return adminApiCall<{ data: ErrorLog[]; total: number; skip: number; limit: number }>(
        `/api/v1/admin/errors?${params.toString()}`,
        accessToken
      );
    },
    staleTime: 2 * 60 * 1000,
    enabled: !!accessToken,
  });
}

// Background Tasks Hook
export function useAdminBackgroundTasks(skip: number = 0, limit: number = 50, status?: string) {
  const { accessToken } = useAuth();
  const params = new URLSearchParams();
  params.append('skip', skip.toString());
  params.append('limit', limit.toString());
  if (status) params.append('status', status);

  return useQuery({
    queryKey: ['admin-background-tasks', skip, limit, status],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return adminApiCall<{ data: BackgroundTask[]; total: number; skip: number; limit: number }>(
        `/api/v1/admin/tasks?${params.toString()}`,
        accessToken
      );
    },
    staleTime: 2 * 60 * 1000,
    refetchInterval: 10 * 1000, // Refetch every 10 seconds
    enabled: !!accessToken,
  });
}

// Payment Transactions Hook
export function useAdminPaymentTransactions(skip: number = 0, limit: number = 50, status?: string) {
  const { accessToken } = useAuth();
  const params = new URLSearchParams();
  params.append('skip', skip.toString());
  params.append('limit', limit.toString());
  if (status) params.append('status', status);

  return useQuery({
    queryKey: ['admin-payment-transactions', skip, limit, status],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return adminApiCall<{ data: PaymentTransaction[]; total: number; skip: number; limit: number }>(
        `/api/v1/admin/payment-transactions?${params.toString()}`,
        accessToken
      );
    },
    staleTime: 2 * 60 * 1000,
    enabled: !!accessToken,
  });
}

// Update User Role Mutation
export function useUpdateUserRole() {
  const { accessToken } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ userId, role }: { userId: string; role: string }) => {
      if (!accessToken) throw new Error('Not authenticated');
      return adminApiCall(`/api/v1/admin/users/${userId}/role`, accessToken, {
        method: 'POST',
        body: JSON.stringify({ role }),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
  });
}

// Update User Subscription Mutation
export function useUpdateUserSubscription() {
  const { accessToken } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ userId, planType }: { userId: string; planType: string }) => {
      if (!accessToken) throw new Error('Not authenticated');
      return adminApiCall(`/api/v1/admin/users/${userId}/subscription`, accessToken, {
        method: 'POST',
        body: JSON.stringify({ plan_type: planType }),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      queryClient.invalidateQueries({ queryKey: ['admin-subscriptions'] });
      queryClient.invalidateQueries({ queryKey: ['admin-stats'] });
    },
  });
}
