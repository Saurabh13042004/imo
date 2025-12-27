import { useQuery } from '@tanstack/react-query';
import { getSessionId } from '@/utils/sessionUtils';

export interface PaymentTransaction {
  id: string;
  user_id: string;
  subscription_id: string | null;
  transaction_id: string;
  amount: string;
  currency: string;
  type: 'subscription' | 'one_time' | 'refund';
  status: 'pending' | 'success' | 'failed' | 'refunded';
  stripe_payment_intent_id: string | null;
  stripe_session_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface TransactionStatus {
  status: 'pending' | 'success' | 'failed' | 'refunded';
  stripe_status: string;
  amount: number;
  currency: string;
  created: string;
  error?: string | null;
  local_transaction?: PaymentTransaction;
}

// Helper to get auth token
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

// Helper to make API calls
async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const API_URL = import.meta.env.VITE_API_URL;
  const url = `${API_URL}${endpoint}`;
  
  const sessionId = getSessionId();
  const authToken = getAuthToken();

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

export function usePaymentTransactions() {
  return useQuery({
    queryKey: ['payment-transactions'],
    queryFn: async () => {
      const data = await apiCall<PaymentTransaction[]>('/api/v1/payments/transactions');
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function usePaymentTransaction(transactionId: string) {
  return useQuery({
    queryKey: ['payment-transaction', transactionId],
    queryFn: async () => {
      const data = await apiCall<PaymentTransaction>(
        `/api/v1/payments/transactions/${transactionId}`
      );
      return data;
    },
    staleTime: 5 * 60 * 1000,
    enabled: !!transactionId,
  });
}

export function useTransactionStatus(paymentIntentId?: string, sessionId?: string) {
  return useQuery({
    queryKey: ['transaction-status', paymentIntentId, sessionId],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (paymentIntentId) params.append('payment_intent_id', paymentIntentId);
      if (sessionId) params.append('session_id', sessionId);
      
      const data = await apiCall<TransactionStatus>(
        `/api/v1/payments/transaction-status?${params.toString()}`
      );
      return data;
    },
    staleTime: 1 * 60 * 1000, // 1 minute for real-time updates
    enabled: !!(paymentIntentId || sessionId),
    refetchInterval: 3000, // Poll every 3 seconds for pending payments
  });
}
