import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { API_BASE_URL } from '../config/api';
import { useAuth } from './useAuth';

interface CreatePriceAlertRequest {
  product_id: string;
  product_name: string;
  product_url: string;
  target_price: number;
  current_price?: number;
  currency?: string;
  email?: string; // Required if not authenticated
}

interface UpdatePriceAlertRequest {
  target_price?: number;
  is_active?: boolean;
}

interface PriceAlert {
  id: string;
  user_id: string | null;
  product_id: string;
  product_name: string;
  product_url: string;
  target_price: number;
  current_price: number | null;
  currency: string;
  email: string;
  is_active: boolean;
  alert_sent: boolean;
  alert_sent_at: string | null;
  created_at: string;
  updated_at: string;
}

interface PriceAlertListResponse {
  total: number;
  alerts: PriceAlert[];
}

/**
 * Hook for managing price alerts
 * Supports both authenticated and non-authenticated users
 */
export const usePriceAlert = () => {
  const queryClient = useQueryClient();
  const { user } = useAuth();

  /**
   * Create a new price alert
   * For authenticated users: email is optional (uses user email by default)
   * For non-authenticated users: email is required
   */
  const createAlert = useMutation({
    mutationFn: async (data: CreatePriceAlertRequest) => {
      // If authenticated and no email provided, use user email
      const payload = {
        ...data,
        email: data.email || user?.email,
      };

      const response = await fetch(`${API_BASE_URL}/api/v1/price-alerts/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(user && { 'Authorization': `Bearer ${localStorage.getItem('token')}` }),
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create price alert');
      }

      return response.json();
    },
    onSuccess: () => {
      // Invalidate alerts list query
      queryClient.invalidateQueries({ queryKey: ['price-alerts'] });
    },
  });

  /**
   * Fetch user's price alerts
   * For authenticated users: fetches alerts by user_id
   * For non-authenticated users: fetches alerts by email
   */
  const fetchAlerts = useQuery({
    queryKey: ['price-alerts', user?.id, user?.email],
    queryFn: async () => {
      const params = new URLSearchParams();
      
      if (user?.id) {
        // Authenticated user - API will use user_id from token
        params.append('active_only', 'false');
      } else if (user?.email) {
        // Might have email from context
        params.append('email', user.email);
        params.append('active_only', 'false');
      }

      const response = await fetch(
        `${API_BASE_URL}/api/v1/price-alerts/list?${params.toString()}`,
        {
          headers: user ? { 'Authorization': `Bearer ${localStorage.getItem('token')}` } : {},
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch price alerts');
      }

      return response.json() as Promise<PriceAlertListResponse>;
    },
    enabled: !!user, // Only fetch if user exists (authenticated or has email)
  });

  /**
   * Fetch a single price alert
   */
  const fetchAlert = (alertId: string) =>
    useQuery({
      queryKey: ['price-alert', alertId],
      queryFn: async () => {
        const response = await fetch(
          `${API_BASE_URL}/api/v1/price-alerts/${alertId}`,
          {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch price alert');
        }

        return response.json() as Promise<PriceAlert>;
      },
      enabled: !!user, // Only fetch if authenticated
    });

  /**
   * Update a price alert
   */
  const updateAlert = useMutation({
    mutationFn: async ({
      alertId,
      data,
    }: {
      alertId: string;
      data: UpdatePriceAlertRequest;
    }) => {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/price-alerts/${alertId}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify(data),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update price alert');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['price-alerts'] });
    },
  });

  /**
   * Delete a price alert
   */
  const deleteAlert = useMutation({
    mutationFn: async (alertId: string) => {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/price-alerts/${alertId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete price alert');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['price-alerts'] });
    },
  });

  /**
   * Check if a product already has an alert for the current user
   */
  const hasExistingAlert = (productId: string): boolean => {
    if (!fetchAlerts.data?.alerts) return false;
    return fetchAlerts.data.alerts.some(
      (alert) => alert.product_id === productId && alert.is_active
    );
  };

  /**
   * Get existing alert for a product
   */
  const getExistingAlert = (productId: string): PriceAlert | undefined => {
    if (!fetchAlerts.data?.alerts) return undefined;
    return fetchAlerts.data.alerts.find(
      (alert) => alert.product_id === productId && alert.is_active
    );
  };

  return {
    // Mutations
    createAlert,
    updateAlert,
    deleteAlert,

    // Queries
    fetchAlerts,
    fetchAlert,

    // Helpers
    hasExistingAlert,
    getExistingAlert,

    // State
    isLoading: fetchAlerts.isLoading,
    isError: fetchAlerts.isError,
    alerts: fetchAlerts.data?.alerts || [],
    totalAlerts: fetchAlerts.data?.total || 0,
  };
};
