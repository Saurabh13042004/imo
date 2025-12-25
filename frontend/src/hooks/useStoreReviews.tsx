import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { API_BASE_URL } from '@/config/api';
import toast from 'react-hot-toast';

export interface StoreReview {
  store: string;
  text: string;
  rating?: number | null;
  reviewer_name?: string;
  title?: string;
  date?: string;
  verified_purchase?: boolean;
}

export interface StoreReviewsState {
  reviews: StoreReview[];
  status: 'idle' | 'loading' | 'ready' | 'error' | 'polling';
  error?: string;
  total_found: number;
  taskId?: string;
  summary?: {
    average_rating: number;
    trust_score: number;
  };
}

/**
 * Hook to fetch store reviews from retailer websites
 * Now uses Celery async tasks with polling
 * Returns task_id immediately, polls for results in background
 */
export function useStoreReviews(productName: string | null, storeUrls?: string[]) {
  const [state, setState] = useState<StoreReviewsState>({
    reviews: [],
    status: 'idle',
    total_found: 0,
  });

  const hasFetched = useRef(false);
  const lastFetchKey = useRef<string>('');
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const pollCountRef = useRef(0);

  // Memoize store URLs to prevent unnecessary re-fetches
  const memoizedUrls = useMemo(() => storeUrls || [], [storeUrls ? storeUrls.join(',') : '']);
  
  // Create a stable key for this request to detect changes
  const fetchKey = `${productName}|${memoizedUrls.join(',')}`;

  // Poll for task status
  const pollTaskStatus = useCallback(async (taskId: string) => {
    if (!taskId) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/reviews/status/${taskId}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Status check failed: ${response.status}`);
      }

      const data = await response.json();
      console.log('[useStoreReviews] Task status:', data.status);

      if (data.status === 'SUCCESS' && data.result) {
        console.log('[useStoreReviews] Task completed! Reviews:', data.result.reviews?.length);
        
        setState({
          reviews: data.result.reviews || [],
          status: 'ready',
          total_found: data.result.total_found || data.result.reviews?.length || 0,
          taskId,
        });

        // Stop polling
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }

        // Show toast
        if (data.result.reviews?.length > 0) {
          toast.success(
            `🎉 Added ${data.result.reviews.length} store reviews!`,
            { position: 'bottom-left', duration: 3000 }
          );
        }
      } else if (data.status === 'FAILURE') {
        throw new Error(data.error || 'Task failed');
      } else {
        // Task still processing
        pollCountRef.current++;
        if (pollCountRef.current % 3 === 0) {
          console.log(`[useStoreReviews] Still polling... (${pollCountRef.current})`);
        }
      }
    } catch (error) {
      console.error('Error polling store reviews status:', error);
      setState(prev => ({
        ...prev,
        status: 'error',
        error: error instanceof Error ? error.message : 'Failed to get review status',
      }));

      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    }
  }, []);

  const submitReviewTask = useCallback(async () => {
    if (!productName || !memoizedUrls || memoizedUrls.length === 0) {
      console.log('[useStoreReviews] Waiting for productName or store URLs');
      setState(prev => ({ ...prev, status: 'idle' }));
      hasFetched.current = false;
      return;
    }

    // Only fetch if we haven't already fetched this combination
    if (hasFetched.current && lastFetchKey.current === fetchKey) {
      return;
    }

    console.log('[useStoreReviews] Submitting task for:', productName, 'with URLs:', memoizedUrls.length);
    setState(prev => ({ ...prev, status: 'loading' }));
    hasFetched.current = true;
    lastFetchKey.current = fetchKey;
    pollCountRef.current = 0;

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/reviews/store`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            product_name: productName,
            store_urls: memoizedUrls,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      const taskId = data.task_id;

      console.log('[useStoreReviews] Task submitted, ID:', taskId);
      setState(prev => ({ ...prev, status: 'polling', taskId }));

      // Start polling
      pollCountRef.current = 0;
      pollTaskStatus(taskId);

      // Poll every 2 seconds
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
      pollIntervalRef.current = setInterval(() => pollTaskStatus(taskId), 2000);
    } catch (error) {
      console.error('Error submitting store review task:', error);
      setState(prev => ({
        ...prev,
        status: 'error',
        error: error instanceof Error ? error.message : 'Failed to submit review task',
      }));
    }
  }, [productName, memoizedUrls, fetchKey, pollTaskStatus]);

  // Submit task when productName or memoizedUrls changes
  useEffect(() => {
    if (productName && memoizedUrls.length > 0 && lastFetchKey.current !== fetchKey) {
      submitReviewTask();
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [fetchKey, submitReviewTask, productName, memoizedUrls]);

  return state;
}
