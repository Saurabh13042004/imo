import { useEffect, useRef, useState } from 'react';

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
  status: 'idle' | 'loading' | 'success' | 'error';
  error: string | null;
  totalFound: number;
  rawCount: number;
  filteredCount: number;
}

/**
 * Hook for fetching Google Shopping reviews
 * Prevents duplicate requests with deduplication logic
 */
export function useGoogleReviews(
  productName: string | null,
  googleShoppingUrl: string | null
): UseGoogleReviewsReturn {
  const [reviews, setReviews] = useState<GoogleReview[]>([]);
  const [summary, setSummary] = useState<GoogleReviewsSummary | null>(null);
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);
  const [totalFound, setTotalFound] = useState(0);
  const [rawCount, setRawCount] = useState(0);
  const [filteredCount, setFilteredCount] = useState(0);

  // Track if we've already fetched to prevent duplicates
  const hasFetched = useRef(false);
  const lastFetchKey = useRef<string>('');

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

    const fetchGoogleReviews = async () => {
      try {
        setStatus('loading');
        setError(null);

        const response = await fetch('/api/v1/reviews/google', {
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
          throw new Error(errorData.detail || 'Failed to fetch Google reviews');
        }

        const data = await response.json();

        setReviews(data.reviews || []);
        setSummary(data.summary || null);
        setTotalFound(data.total_found || 0);
        setRawCount(data.raw_count || 0);
        setFilteredCount(data.filtered_count || 0);
        setStatus('success');
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error';
        setError(errorMessage);
        setStatus('error');
        console.error('Error fetching Google reviews:', err);
      }
    };

    // Mark as fetched and store the key
    hasFetched.current = true;
    lastFetchKey.current = fetchKey;

    fetchGoogleReviews();
  }, [productName, googleShoppingUrl]);

  return {
    reviews,
    summary,
    status,
    error,
    totalFound,
    rawCount,
    filteredCount,
  };
}
