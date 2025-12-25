import { useEffect, useRef, useState } from 'react';
import toast from 'react-hot-toast';
import { API_BASE_URL } from '@/config/api';

export interface GoogleReview {
  reviewer_name: string;
  rating: number;
  date: string;
  title: string;
  text: string;
  source: string;
  confidence: number;
}

export interface GoogleReviewsSummary {
  average_rating: number;
  overall_sentiment: 'positive' | 'mixed' | 'negative' | 'neutral';
  common_praises: string[];
  common_complaints: string[];
  verified_patterns: {
    positive: string[];
    negative: string[];
  };
}

export interface UseGoogleReviewsReturn {
  reviews: GoogleReview[];
  summary: GoogleReviewsSummary | null;
  status: 'idle' | 'loading' | 'success' | 'error' | 'polling';
  error: string | null;
  totalFound: number;
  rawCount: number;
  filteredCount: number;
  taskId?: string;
}

/**
 * Hook for fetching Google Shopping reviews
 * Now uses Celery async tasks with polling
 * Prevents duplicate requests with deduplication logic
 */
export function useGoogleReviews(
  productName: string | null,
  googleShoppingUrl: string | null
): UseGoogleReviewsReturn {
  const [reviews, setReviews] = useState<GoogleReview[]>([]);
  const [summary, setSummary] = useState<GoogleReviewsSummary | null>(null);
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error' | 'polling'>('idle');
  const [error, setError] = useState<string | null>(null);
  const [totalFound, setTotalFound] = useState(0);
  const [rawCount, setRawCount] = useState(0);
  const [filteredCount, setFilteredCount] = useState(0);
  const [taskId, setTaskId] = useState<string>();

  // Track if we've already fetched to prevent duplicates
  const hasFetched = useRef(false);
  const lastFetchKey = useRef<string>('');
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const pollCountRef = useRef(0);

  // Poll for task status
  const pollTaskStatus = async (currentTaskId: string) => {
    if (!currentTaskId) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/reviews/status/${currentTaskId}`,
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
      console.log('[useGoogleReviews] Task status:', data.status);

      // Handle PROGRESS state - stream reviews as they arrive
      if (data.status === 'PROGRESS' && data.state_meta) {
        console.log('[useGoogleReviews] PROGRESS:', data.state_meta.current, '/', data.state_meta.total, '- Batch', data.state_meta.batch);
        
        // Update reviews progressively with all accumulated reviews
        if (data.state_meta.reviews?.length > 0) {
          setReviews(data.state_meta.reviews);
          setTotalFound(data.state_meta.total || data.state_meta.reviews.length);
          setStatus('polling');
          
          // Show progress toast every few batches
          if (data.state_meta.batch % 2 === 0) {
            // toast.loading(
            //   `📥 Loading reviews... ${data.state_meta.current}/${data.state_meta.total}`,
            //   { position: 'bottom-left', id: 'progress-toast' }
            // );
          }
        }
      } else if (data.status === 'SUCCESS' && data.result) {
        console.log('[useGoogleReviews] Task completed! Reviews:', data.result.reviews?.length);

        setReviews(data.result.reviews || []);
        setSummary(data.result.summary || null);
        setTotalFound(data.result.total_found || data.result.reviews?.length || 0);
        setRawCount(data.result.raw_count || 0);
        setFilteredCount(data.result.filtered_count || 0);
        setStatus('success');

        // Stop polling
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }

        // Dismiss progress toast and show final toast
        toast.dismiss('progress-toast');
        if (data.result.reviews?.length > 0) {
          toast.success(
            `🎉 Added ${data.result.reviews.length} Google Shopping reviews!`,
            { position: 'bottom-left', duration: 3000 }
          );
        }
      } else if (data.status === 'FAILURE') {
        throw new Error(data.error || 'Task failed');
      } else {
        // Task still processing
        pollCountRef.current++;
        if (pollCountRef.current % 3 === 0) {
          console.log(`[useGoogleReviews] Still polling... (${pollCountRef.current})`);
        }
      }
    } catch (err) {
      console.error('Error polling Google reviews status:', err);
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      setStatus('error');

      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    }
  };

  useEffect(() => {
    if (!productName || !googleShoppingUrl) {
      return;
    }

    // Create a key to track if this exact request was already made
    const fetchKey = `${productName}|${googleShoppingUrl}`;

    // Skip if we've already fetched this combination
    if (hasFetched.current && lastFetchKey.current === fetchKey) {
      return;
    }

    const submitGoogleReviewTask = async () => {
      try {
        setStatus('loading');
        setError(null);
        hasFetched.current = true;
        lastFetchKey.current = fetchKey;
        pollCountRef.current = 0;

        const response = await fetch(`${API_BASE_URL}/api/v1/reviews/google`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            product_name: productName,
            google_shopping_url: googleShoppingUrl,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to submit Google reviews task');
        }

        const data = await response.json();
        const newTaskId = data.task_id;

        console.log('[useGoogleReviews] Task submitted, ID:', newTaskId);
        setTaskId(newTaskId);
        setStatus('polling');

        // Start polling
        pollCountRef.current = 0;
        await pollTaskStatus(newTaskId);

        // Poll every 2 seconds
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
        }
        pollIntervalRef.current = setInterval(() => pollTaskStatus(newTaskId), 2000);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error';
        setError(errorMessage);
        setStatus('error');
        console.error('Error submitting Google reviews task:', err);
      }
    };

    submitGoogleReviewTask();

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
    }, [productName, googleShoppingUrl]);

  return {
    reviews,
    summary,
    status,
    error,
    totalFound,
    rawCount,
    filteredCount,
    taskId,
  };
}
