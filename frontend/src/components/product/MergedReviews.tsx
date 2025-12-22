import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';

interface Review {
  source: string;
  text: string;
  rating?: number | null;
  confidence?: number;
  store?: string;
}

interface MergedReviewsProps {
  reviews: Review[];
  loadingCommunity: boolean;
  loadingStore: boolean;
  errorCommunity?: string;
  errorStore?: string;
}

/**
 * Component to display merged reviews from multiple sources
 * Shows progressive loading with source labels
 */
export function MergedReviews({
  reviews,
  loadingCommunity,
  loadingStore,
  errorCommunity,
  errorStore,
}: MergedReviewsProps) {
  const hasReviews = reviews.length > 0;
  const isLoading = loadingCommunity || loadingStore;
  const hasErrors = errorCommunity || errorStore;

  return (
    <div className="space-y-4">
      {/* Loading and Error Status */}
      <div className="flex flex-wrap gap-2">
        {loadingCommunity && (
          <div className="flex items-center gap-2 px-3 py-2 rounded-full bg-blue-50 text-blue-700">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm">Loading community reviews…</span>
          </div>
        )}

        {loadingStore && (
          <div className="flex items-center gap-2 px-3 py-2 rounded-full bg-blue-50 text-blue-700">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm">Loading store reviews…</span>
          </div>
        )}

        {errorCommunity && (
          <div className="flex items-center gap-2 px-3 py-2 rounded-full bg-yellow-50 text-yellow-700">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">Community reviews unavailable</span>
          </div>
        )}

        {errorStore && (
          <div className="flex items-center gap-2 px-3 py-2 rounded-full bg-yellow-50 text-yellow-700">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">Store reviews unavailable</span>
          </div>
        )}
      </div>

      {/* Reviews Grid */}
      {hasReviews && (
        <div className="grid gap-4 mt-6">
          <AnimatePresence mode="popLayout">
            {reviews.map((review, idx) => (
              <motion.div
                key={`${review.source}-${idx}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="p-4 rounded-lg border border-gray-200 hover:border-gray-300 bg-white"
              >
                {/* Source Badge */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        review.source === 'community' || review.source === 'reddit'
                          ? 'bg-orange-100 text-orange-800'
                          : review.source === 'forum'
                            ? 'bg-purple-100 text-purple-800'
                            : 'bg-green-100 text-green-800'
                      }`}
                    >
                      {review.source === 'reddit'
                        ? '🔴 Reddit'
                        : review.source === 'forum'
                          ? '💬 Forum'
                          : review.store
                            ? `🛒 ${review.store.charAt(0).toUpperCase() + review.store.slice(1)}`
                            : '📦 Store'}
                    </span>
                  </div>

                  {/* Rating or Confidence */}
                  <div className="flex items-center gap-2">
                    {review.rating !== null && review.rating !== undefined && (
                      <div className="flex items-center gap-1">
                        <span className="text-sm font-medium text-gray-700">
                          {review.rating.toFixed(1)}⭐
                        </span>
                      </div>
                    )}
                    {review.confidence !== undefined && (
                      <div className="flex items-center gap-1">
                        <span className="text-xs text-gray-500">
                          {Math.round(review.confidence * 100)}% match
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Review Text */}
                <p className="text-sm text-gray-700 leading-relaxed line-clamp-4">
                  {review.text}
                </p>

                {/* Read More Link */}
                {review.text.length > 200 && (
                  <button className="text-xs text-blue-600 hover:text-blue-800 mt-2 font-medium">
                    Read more →
                  </button>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Empty State */}
      {!hasReviews && !isLoading && (
        <div className="text-center py-12">
          <CheckCircle2 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No reviews available yet</p>
        </div>
      )}

      {/* Loading Skeleton */}
      {!hasReviews && isLoading && (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="p-4 rounded-lg border border-gray-200 bg-gray-50 animate-pulse">
              <div className="h-4 bg-gray-300 rounded w-24 mb-3" />
              <div className="space-y-2">
                <div className="h-3 bg-gray-300 rounded" />
                <div className="h-3 bg-gray-300 rounded w-5/6" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
