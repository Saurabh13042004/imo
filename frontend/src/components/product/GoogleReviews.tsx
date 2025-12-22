import React from 'react';
import { useGoogleReviews, GoogleReview, GoogleReviewsSummary } from '@/hooks/useGoogleReviews';
import { Star, AlertCircle, CheckCircle, TrendingUp } from 'lucide-react';

interface GoogleReviewsProps {
  productName: string;
  googleShoppingUrl: string;
}

const GoogleReviews: React.FC<GoogleReviewsProps> = ({ productName, googleShoppingUrl }) => {
  const { reviews, summary, status, error, totalFound, rawCount, filteredCount } =
    useGoogleReviews(productName, googleShoppingUrl);

  if (!productName || !googleShoppingUrl) {
    return null;
  }

  if (status === 'loading') {
    return (
      <div className="w-full py-8 px-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
        <div className="flex items-center justify-center space-x-3">
          <div className="w-5 h-5 rounded-full border-2 border-blue-300 border-t-blue-600 animate-spin"></div>
          <p className="text-blue-900 font-medium">Fetching Google Shopping reviews...</p>
        </div>
        <p className="text-center text-blue-700 text-sm mt-2">This may take a minute</p>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="w-full py-6 px-6 bg-red-50 rounded-lg border border-red-200">
        <div className="flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <div>
            <h4 className="font-semibold text-red-900">Failed to load reviews</h4>
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!summary || reviews.length === 0) {
    return (
      <div className="w-full py-6 px-6 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-gray-600 text-center">No reviews found</p>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">Google Shopping Reviews</h3>
        <p className="text-sm text-gray-600">
          {filteredCount > 0 && (
            <>
              Analyzed {rawCount} reviews, filtered to {totalFound}
            </>
          )}
          {filteredCount === 0 && `Found ${totalFound} reviews`}
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Average Rating */}
        <div className="bg-gradient-to-br from-yellow-50 to-amber-50 rounded-lg p-4 border border-yellow-200">
          <p className="text-sm font-medium text-yellow-900 mb-2">Average Rating</p>
          <div className="flex items-center space-x-2">
            <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
            <span className="text-2xl font-bold text-yellow-900">
              {summary.average_rating.toFixed(1)}
            </span>
          </div>
        </div>

        {/* Sentiment */}
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
          <p className="text-sm font-medium text-blue-900 mb-2">Overall Sentiment</p>
          <p className="text-xl font-bold text-blue-900 capitalize">
            {summary.overall_sentiment}
          </p>
        </div>

        {/* Praises Count */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
          <p className="text-sm font-medium text-green-900 mb-2">Common Praises</p>
          <p className="text-2xl font-bold text-green-900">{summary.common_praises.length}</p>
        </div>

        {/* Complaints Count */}
        <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-lg p-4 border border-red-200">
          <p className="text-sm font-medium text-red-900 mb-2">Common Complaints</p>
          <p className="text-2xl font-bold text-red-900">{summary.common_complaints.length}</p>
        </div>
      </div>

      {/* Patterns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Positive Patterns */}
        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <div className="flex items-center space-x-2 mb-3">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <h4 className="font-semibold text-green-900">What People Love</h4>
          </div>
          <div className="space-y-2">
            {summary.verified_patterns.positive.length > 0 ? (
              summary.verified_patterns.positive.map((pattern, idx) => (
                <div
                  key={idx}
                  className="text-sm text-green-800 bg-white rounded px-3 py-2 border border-green-100"
                >
                  ✓ {pattern}
                </div>
              ))
            ) : (
              <p className="text-sm text-green-700 italic">No positive patterns identified</p>
            )}
          </div>
        </div>

        {/* Negative Patterns */}
        <div className="bg-red-50 rounded-lg p-4 border border-red-200">
          <div className="flex items-center space-x-2 mb-3">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <h4 className="font-semibold text-red-900">Common Concerns</h4>
          </div>
          <div className="space-y-2">
            {summary.verified_patterns.negative.length > 0 ? (
              summary.verified_patterns.negative.map((pattern, idx) => (
                <div
                  key={idx}
                  className="text-sm text-red-800 bg-white rounded px-3 py-2 border border-red-100"
                >
                  ⚠ {pattern}
                </div>
              ))
            ) : (
              <p className="text-sm text-red-700 italic">No significant concerns identified</p>
            )}
          </div>
        </div>
      </div>

      {/* Praises and Complaints */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Praises */}
        <div className="rounded-lg p-4 bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200">
          <h4 className="font-semibold text-green-900 mb-3 flex items-center">
            <TrendingUp className="w-4 h-4 mr-2" />
            Top Positive Points
          </h4>
          <ul className="space-y-2">
            {summary.common_praises.map((praise, idx) => (
              <li key={idx} className="text-sm text-green-800">
                • {praise}
              </li>
            ))}
          </ul>
        </div>

        {/* Complaints */}
        <div className="rounded-lg p-4 bg-gradient-to-br from-orange-50 to-red-50 border border-orange-200">
          <h4 className="font-semibold text-orange-900 mb-3 flex items-center">
            <AlertCircle className="w-4 h-4 mr-2" />
            Top Negative Points
          </h4>
          <ul className="space-y-2">
            {summary.common_complaints.map((complaint, idx) => (
              <li key={idx} className="text-sm text-orange-800">
                • {complaint}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Reviews List */}
      <div className="mt-8">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">
          Recent Reviews ({reviews.length} shown)
        </h4>
        <div className="space-y-4 max-h-[600px] overflow-y-auto">
          {reviews.map((review, idx) => (
            <div key={idx} className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <p className="font-semibold text-gray-900">{review.title || 'Untitled'}</p>
                  <p className="text-sm text-gray-600">{review.reviewer_name}</p>
                </div>
                <div className="flex items-center space-x-1 ml-4">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`w-4 h-4 ${
                        i < Math.round(review.rating)
                          ? 'text-yellow-400 fill-yellow-400'
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                  <span className="text-sm font-medium text-gray-900 ml-1">
                    {review.rating.toFixed(1)}
                  </span>
                </div>
              </div>

              <p className="text-sm text-gray-700 mb-3">{review.text}</p>

              <div className="flex justify-between items-center text-xs text-gray-500">
                <span>{review.date}</span>
                <div className="flex items-center space-x-2">
                  <span>From: {review.source}</span>
                  {review.confidence && review.confidence < 1.0 && (
                    <span className="text-yellow-600 font-medium">
                      Confidence: {(review.confidence * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default GoogleReviews;
