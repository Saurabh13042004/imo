import { useState, useEffect, useCallback, useRef } from 'react';
import { API_BASE_URL } from '@/config/api';

export interface CommunityReview {
  source: 'reddit' | 'forum';
  text: string;
  confidence?: number;
}

export interface CommunityReviewsState {
  reviews: CommunityReview[];
  status: 'idle' | 'loading' | 'ready' | 'error';
  error?: string;
  total_found: number;
}

/**
 * Hook to fetch community reviews from Reddit and forums
 * Stateless API - no database dependency
 * Non-blocking, returns progressive updates
 */
export function useCommunityReviews(productName: string | null, brand?: string) {
  const [state, setState] = useState<CommunityReviewsState>({
    reviews: [],
    status: 'idle',
    total_found: 0,
  });

  // Use ref to track if we've already fetched to prevent duplicate calls
  const hasFetched = useRef(false);
  const lastFetchKey = useRef<string>('');
  
  // Create a stable key for this request to detect changes
  const fetchKey = `${productName}|${brand || ''}`;

  const fetchReviews = useCallback(async () => {
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

    console.log('[useCommunityReviews] Starting fetch for:', productName);
    setState(prev => ({ ...prev, status: 'loading' }));
    hasFetched.current = true;
    lastFetchKey.current = fetchKey;

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

      console.log('[useCommunityReviews] Got response:', data.reviews?.length, 'reviews');
      setState({
        reviews: data.reviews || [],
        status: 'ready',
        total_found: data.total_found || 0,
      });
    } catch (error) {
      console.error('Error fetching community reviews:', error);
      setState(prev => ({
        ...prev,
        status: 'error',
        error: error instanceof Error ? error.message : 'Failed to fetch community reviews',
      }));
    }
  }, [productName, brand, fetchKey]);

  // Fetch reviews when productName or brand changes (but only once per unique combo)
  useEffect(() => {
    if (productName && lastFetchKey.current !== fetchKey) {
      fetchReviews();
    }
  }, [fetchKey, fetchReviews, productName, brand]);

  return state;
}
