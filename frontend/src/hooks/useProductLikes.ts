import { useState, useCallback, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { API_BASE_URL } from '@/config/api';

interface UseProductLikesOptions {
  productId: string;
  initialLikeCount?: number;
  initialLikedByUser?: boolean;
  enabled?: boolean;
  productData?: {
    title?: string;
    image_url?: string;
    price?: number;
    currency?: string;
    source?: string;
    source_id?: string;
    brand?: string;
    description?: string;
    url?: string;
    category?: string;
    availability?: string;
  };
}

interface ProductLikeResponse {
  is_liked: boolean;
  like_count: number;
}

export function useProductLikes({
  productId,
  initialLikeCount = 0,
  initialLikedByUser = false,
  enabled = true,
  productData,
}: UseProductLikesOptions) {
  const queryClient = useQueryClient();
  const [isLiked, setIsLiked] = useState(initialLikedByUser);
  const [likeCount, setLikeCount] = useState(initialLikeCount);

  // Get auth token to check if user is authenticated
  const authTokens = localStorage.getItem('auth_tokens');
  const token = authTokens ? JSON.parse(authTokens).accessToken : null;

  // Fetch current like status (only if authenticated)
  const { data: statusData, isLoading } = useQuery({
    queryKey: ['productLike', productId],
    queryFn: async () => {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/products/${productId}/like/status`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch like status');
      }

      return response.json() as Promise<ProductLikeResponse>;
    },
    enabled: enabled && !!productId && !!token, // Only fetch if user is authenticated
    staleTime: 30000, // 30 seconds
  });

  // Update local state when data loads
  useEffect(() => {
    if (statusData) {
      setIsLiked(statusData.is_liked);
      setLikeCount(statusData.like_count);
    }
  }, [statusData]);

  // Toggle like mutation
  const toggleLikeMutation = useMutation({
    mutationFn: async () => {
      const authTokens = localStorage.getItem('auth_tokens');
      const token = authTokens ? JSON.parse(authTokens).accessToken : null;
      const response = await fetch(
        `${API_BASE_URL}/api/v1/products/${productId}/like`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify(productData || {}),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to toggle like');
      }

      return response.json() as Promise<ProductLikeResponse>;
    },
    onMutate: async () => {
      // Optimistic update
      const previousIsLiked = isLiked;
      const previousLikeCount = likeCount;

      setIsLiked(!isLiked);
      setLikeCount(isLiked ? likeCount - 1 : likeCount + 1);

      return { previousIsLiked, previousLikeCount };
    },
    onError: (error, variables, context) => {
      // Revert optimistic update on error
      if (context) {
        setIsLiked(context.previousIsLiked);
        setLikeCount(context.previousLikeCount);
      }
      console.error('Error toggling like:', error);
    },
    onSuccess: (data) => {
      // Update state with server response
      setIsLiked(data.is_liked);
      setLikeCount(data.like_count);

      // Invalidate related queries
      queryClient.invalidateQueries({
        queryKey: ['productLike', productId],
      });
      queryClient.invalidateQueries({
        queryKey: ['userLikedProducts'],
      });
    },
  });

  const toggleLike = useCallback(async () => {
    try {
      await toggleLikeMutation.mutateAsync();
    } catch (error) {
      console.error('Failed to toggle like:', error);
    }
  }, [toggleLikeMutation]);

  return {
    isLiked,
    likeCount,
    toggleLike,
    loading: isLoading || toggleLikeMutation.isPending,
    error: toggleLikeMutation.error as Error | null,
  };
}
