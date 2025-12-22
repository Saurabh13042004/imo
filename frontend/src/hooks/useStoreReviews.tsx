import { useState, useEffect, useCallback, useMemo, useRef } from 'react';

export interface StoreReview {
  store: string;
  text: string;
  rating?: number | null;
}

export interface StoreReviewsState {
  reviews: StoreReview[];
  status: 'idle' | 'loading' | 'ready' | 'error';
  error?: string;
  total_found: number;
  summary?: {
    average_rating: number;
    trust_score: number;
  };
}

/**
 * Hook to fetch store reviews from retailer websites
 * Stateless API - no database dependency
 * Non-blocking, returns progressive updates
 */
export function useStoreReviews(productName: string | null, storeUrls?: string[]) {
  const [state, setState] = useState<StoreReviewsState>({
    reviews: [],
    status: 'idle',
    total_found: 0,
  });

  // Use ref to track if we've already fetched to prevent duplicate calls
  const hasFetched = useRef(false);
  const lastFetchKey = useRef<string>('');

  // Memoize store URLs to prevent unnecessary re-fetches
  const memoizedUrls = useMemo(() => storeUrls || [], [storeUrls ? storeUrls.join(',') : '']);
  
  // Create a stable key for this request to detect changes
  const fetchKey = `${productName}|${memoizedUrls.join(',')}`;

  const fetchReviews = useCallback(async () => {
    if (!productName || !memoizedUrls || memoizedUrls.length === 0) {
      setState(prev => ({ ...prev, status: 'idle' }));
      hasFetched.current = false;
      return;
    }

    // Only fetch if we haven't already fetched this combination
    if (hasFetched.current && lastFetchKey.current === fetchKey) {
      return;
    }

    setState(prev => ({ ...prev, status: 'loading' }));
    hasFetched.current = true;
    lastFetchKey.current = fetchKey;

    try {
      const response = await fetch(
        '/api/v1/reviews/store',
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

      setState({
        reviews: data.reviews || [],
        status: 'ready',
        total_found: data.total_found || 0,
        summary: data.summary,
      });
    } catch (error) {
      console.error('Error fetching store reviews:', error);
      setState(prev => ({
        ...prev,
        status: 'error',
        error: error instanceof Error ? error.message : 'Failed to fetch store reviews',
      }));
    }
  }, [productName, memoizedUrls, fetchKey]);

  // Fetch reviews when productName or memoizedUrls changes (but only once per unique combo)
  useEffect(() => {
    if (productName && memoizedUrls.length > 0 && lastFetchKey.current !== fetchKey) {
      fetchReviews();
    }
  }, [fetchKey, fetchReviews, productName, memoizedUrls]);

  return state;
}
