import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios, { AxiosError, AxiosRequestConfig } from "axios";

const API_BASE = "/api/v1/admin/crud";

// Helper to get auth token from localStorage
const getAuthToken = (): string | null => {
  try {
    // Check both 'auth' and 'auth_tokens' keys for compatibility
    let auth = localStorage.getItem("auth_tokens");
    if (!auth) {
      auth = localStorage.getItem("auth");
    }
    
    if (auth) {
      const parsed = JSON.parse(auth);
      const token = parsed.accessToken || null;
      if (token) {
        console.log("[axiosWithAuth] Token found, length:", token.length);
      } else {
        console.warn("[axiosWithAuth] No accessToken in parsed auth object. Keys:", Object.keys(parsed));
      }
      return token;
    } else {
      console.warn("[axiosWithAuth] No auth in localStorage");
    }
  } catch (e) {
    console.error("[axiosWithAuth] Error parsing auth:", e);
    return null;
  }
  return null;
};

// Helper to make authenticated axios requests
const axiosWithAuth = {
  get: <T = any,>(url: string, config: AxiosRequestConfig = {}) => {
    const token = getAuthToken();
    return axios.get<T>(url, {
      ...config,
      headers: {
        ...(config?.headers || {}),
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });
  },
  post: <T = any,>(url: string, data?: any, config: AxiosRequestConfig = {}) => {
    const token = getAuthToken();
    return axios.post<T>(url, data, {
      ...config,
      headers: {
        ...(config?.headers || {}),
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });
  },
  put: <T = any,>(url: string, data?: any, config: AxiosRequestConfig = {}) => {
    const token = getAuthToken();
    return axios.put<T>(url, data, {
      ...config,
      headers: {
        ...(config?.headers || {}),
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });
  },
  delete: <T = any,>(url: string, config: AxiosRequestConfig = {}) => {
    const token = getAuthToken();
    const headers = {
      ...(config?.headers || {}),
      ...(token && { Authorization: `Bearer ${token}` }),
    };
    console.log("[axiosWithAuth.delete]", { url, hasToken: !!token, headersSet: !!headers.Authorization });
    return axios.delete<T>(url, {
      ...config,
      headers,
    });
  },
};

// ==================== Types ====================

export interface User {
  id: string;
  email: string;
  full_name: string;
  subscription_tier: string;
  access_level: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

export interface UserInput {
  full_name?: string;
  email?: string;
  subscription_tier?: string;
  access_level?: string;
  avatar_url?: string;
}

export interface Transaction {
  id: string;
  user_id: string;
  subscription_id?: string;
  transaction_id: string;
  amount: number;
  currency: string;
  type: string;
  status: string;
  stripe_payment_intent_id?: string;
  stripe_session_id?: string;
  created_at: string;
  updated_at: string;
}

export interface TransactionInput {
  user_id: string;
  subscription_id?: string;
  transaction_id: string;
  amount: number;
  currency?: string;
  type: string;
  status?: string;
  stripe_payment_intent_id?: string;
  stripe_session_id?: string;
  metadata_json?: string;
}

export interface Subscription {
  id: string;
  user_id: string;
  plan_type: string;
  billing_cycle?: string;
  is_active: boolean;
  subscription_start: string;
  subscription_end?: string;
  trial_start?: string;
  trial_end?: string;
  stripe_customer_id?: string;
  stripe_subscription_id?: string;
  created_at: string;
  updated_at: string;
}

export interface SubscriptionInput {
  user_id: string;
  plan_type: string;
  billing_cycle?: string;
  is_active?: boolean;
  subscription_start?: string;
  subscription_end?: string;
  trial_start?: string;
  trial_end?: string;
  stripe_customer_id?: string;
  stripe_subscription_id?: string;
  stripe_product_id?: string;
}

// ==================== Users CRUD ====================

export const useCreateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: UserInput) => {
      const response = await axiosWithAuth.post<User>(`${API_BASE}/users`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin_users"] });
    },
  });
};

export const useUpdateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ userId, data }: { userId: string; data: UserInput }) => {
      const response = await axiosWithAuth.put<User>(`${API_BASE}/users/${userId}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin_users"] });
    },
  });
};

export const useDeleteUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (userId: string) => {
      await axiosWithAuth.delete(`${API_BASE}/users/${userId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin_users"] });
    },
  });
};

export const useGetUser = (userId: string) => {
  return useQuery({
    queryKey: ["admin_user", userId],
    queryFn: async () => {
      const response = await axiosWithAuth.get<User>(`${API_BASE}/users/${userId}`);
      return response.data;
    },
  });
};

// ==================== Transactions CRUD ====================

export const useCreateTransaction = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: TransactionInput) => {
      const response = await axiosWithAuth.post<Transaction>(`${API_BASE}/transactions`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin_transactions"] });
    },
  });
};

export const useUpdateTransaction = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      transactionId,
      data,
    }: {
      transactionId: string;
      data: Partial<TransactionInput>;
    }) => {
      const response = await axiosWithAuth.put<Transaction>(
        `${API_BASE}/transactions/${transactionId}`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin_transactions"] });
    },
  });
};

export const useDeleteTransaction = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (transactionId: string) => {
      await axiosWithAuth.delete(`${API_BASE}/transactions/${transactionId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin_transactions"] });
    },
  });
};

export const useGetTransaction = (transactionId: string) => {
  return useQuery({
    queryKey: ["admin_transaction", transactionId],
    queryFn: async () => {
      const response = await axiosWithAuth.get<Transaction>(
        `${API_BASE}/transactions/${transactionId}`
      );
      return response.data;
    },
  });
};

// ==================== Subscriptions CRUD ====================

export const useCreateSubscription = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: SubscriptionInput) => {
      const response = await axiosWithAuth.post<Subscription>(`${API_BASE}/subscriptions`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin_subscriptions"] });
    },
  });
};

export const useUpdateSubscription = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      subscriptionId,
      data,
    }: {
      subscriptionId: string;
      data: Partial<SubscriptionInput>;
    }) => {
      const response = await axiosWithAuth.put<Subscription>(
        `${API_BASE}/subscriptions/${subscriptionId}`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin_subscriptions"] });
    },
  });
};

export const useDeleteSubscription = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (subscriptionId: string) => {
      await axiosWithAuth.delete(`${API_BASE}/subscriptions/${subscriptionId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin_subscriptions"] });
    },
  });
};

export const useGetSubscription = (subscriptionId: string) => {
  return useQuery({
    queryKey: ["admin_subscription", subscriptionId],
    queryFn: async () => {
      const response = await axiosWithAuth.get<Subscription>(
        `${API_BASE}/subscriptions/${subscriptionId}`
      );
      return response.data;
    },
  });
};
