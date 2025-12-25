import { useState, useEffect, useCallback, useRef } from 'react';
import { API_BASE_URL } from '@/config/api';
import toast from 'react-hot-toast';

export interface CommunityReview {
  source: 'reddit' | 'forum';
  text: string;
  confidence?: number;
  reviewer_name?: string;
  rating?: number;
  date?: string;
}

export interface CommunityReviewsState {
  reviews: CommunityReview[];
  status: 'idle' | 'loading' | 'ready' | 'error' | 'polling';
  error?: string;
  total_found: number;
  taskId?: string;
}

/**
 * Hook to fetch community reviews from Reddit and forums
 * Now uses Celery async tasks with polling
 * Returns task_id immediately, polls for results in background
 */
export function useCommunityReviews(productName: string | null, brand?: string) {
  const [state, setState] = useState<CommunityReviewsState>({
    reviews: [],
    status: 'idle',
    total_found: 0,
  });

  const hasFetched = useRef(false);
  const lastFetchKey = useRef<string>('');
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const pollCountRef = useRef(0);
  
  const fetchKey = `${productName}|${brand || ''}`;

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
      console.log('[useCommunityReviews] Task status:', data.status);

      if (data.status === 'SUCCESS' && data.result) {
        console.log('[useCommunityReviews] Task completed! Reviews:', data.result.reviews?.length);
        
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
            `🎉 Added ${data.result.reviews.length} community reviews!`,
            { position: 'bottom-left', duration: 3000 }
          );
        }
      } else if (data.status === 'FAILURE') {
        throw new Error(data.error || 'Task failed');
      } else {
        // Task still processing - continue polling
        pollCountRef.current++;
        if (pollCountRef.current % 3 === 0) {
          console.log(`[useCommunityReviews] Still polling... (${pollCountRef.current})`);
        }
      }
    } catch (error) {
      console.error('Error polling community reviews status:', error);
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
    if (!productName) {
      console.log('[useCommunityReviews] Waiting for productName');
      setState(prev => ({ ...prev, status: 'idle' }));
      hasFetched.current = false;
      return;
    }

    // Only fetch if we haven't already fetched this combination
    if (hasFetched.current && lastFetchKey.current === fetchKey) {
      return;
    }

    console.log('[useCommunityReviews] Submitting task for:', productName);
    setState(prev => ({ ...prev, status: 'loading' }));
    hasFetched.current = true;
    lastFetchKey.current = fetchKey;
    pollCountRef.current = 0;

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/reviews/community`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            product_name: productName,
            brand: brand || '',
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      const taskId = data.task_id;

      console.log('[useCommunityReviews] Task submitted, ID:', taskId);
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
      console.error('Error submitting community review task:', error);
      setState(prev => ({
        ...prev,
        status: 'error',
        error: error instanceof Error ? error.message : 'Failed to submit review task',
      }));
    }
  }, [productName, brand, fetchKey, pollTaskStatus]);

  // Submit task when productName or brand changes
  useEffect(() => {
    if (productName && lastFetchKey.current !== fetchKey) {
      submitReviewTask();
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [fetchKey, submitReviewTask, productName, brand]);

  return state;
}
