import { useState, useMemo } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from "@/components/ui/pagination";
import { Star, ThumbsUp, ThumbsDown, ShieldCheck, Filter } from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

interface ExternalReview {
  id: string;
  external_review_id: string;
  reviewer_name: string | null;
  rating: number;
  title: string | null;
  review_text: string | null;
  verified_purchase: boolean;
  review_date: string | null;
  positive_feedback: number;
  negative_feedback: number;
  source: string | null;
}

interface ExternalReviewsProps {
  productId: string;
  reviews?: ExternalReview[];
  reviewsSummary?: any;
  isLoading?: boolean;
}

export const ExternalReviews = ({ productId, reviews = [], reviewsSummary, isLoading }: ExternalReviewsProps) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortBy, setSortBy] = useState<'latest' | 'relevance' | 'rating-high' | 'rating-low'>('latest');
  const [selectedSources, setSelectedSources] = useState<Set<string>>(new Set());
  const reviewsPerPage = 5;
  const totalReviews = reviews.length;

  // Get unique sources for filter
  const uniqueSources = useMemo(() => {
    const sources = new Set<string>();
    reviews.forEach(review => {
      if (review.source) sources.add(review.source);
    });
    return Array.from(sources).sort();
  }, [reviews]);

  // Filter reviews by selected sources
  const filteredReviews = useMemo(() => {
    if (selectedSources.size === 0) return reviews;
    return reviews.filter(review => selectedSources.has(review.source || ''));
  }, [reviews, selectedSources]);

  // Sort reviews
  const sortedReviews = useMemo(() => {
    const sorted = [...filteredReviews];
    
    switch (sortBy) {
      case 'latest':
        return sorted.sort((a, b) => {
          const dateA = a.review_date ? new Date(a.review_date).getTime() : 0;
          const dateB = b.review_date ? new Date(b.review_date).getTime() : 0;
          return dateB - dateA;
        });
      case 'relevance':
        return sorted.sort((a, b) => {
          const scoreA = (a.positive_feedback - a.negative_feedback) + a.rating;
          const scoreB = (b.positive_feedback - b.negative_feedback) + b.rating;
          return scoreB - scoreA;
        });
      case 'rating-high':
        return sorted.sort((a, b) => b.rating - a.rating);
      case 'rating-low':
        return sorted.sort((a, b) => a.rating - b.rating);
      default:
        return sorted;
    }
  }, [filteredReviews, sortBy]);

  const toggleSource = (source: string) => {
    const newSources = new Set(selectedSources);
    if (newSources.has(source)) {
      newSources.delete(source);
    } else {
      newSources.add(source);
    }
    setSelectedSources(newSources);
    setCurrentPage(1);
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${
          i < rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
        }`}
      />
    ));
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Date not available';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const totalFilteredReviews = sortedReviews.length;
  const totalPages = Math.ceil(totalFilteredReviews / reviewsPerPage);

  const renderPagination = () => {
    if (totalPages <= 1) return null;

    const generatePageNumbers = () => {
      const pages = [];
      const maxVisiblePages = 5;

      if (totalPages <= maxVisiblePages) {
        for (let i = 1; i <= totalPages; i++) {
          pages.push(i);
        }
      } else {
        const start = Math.max(1, currentPage - 2);
        const end = Math.min(totalPages, start + maxVisiblePages - 1);

        for (let i = start; i <= end; i++) {
          pages.push(i);
        }
      }

      return pages;
    };

    return (
      <Pagination className="mt-6">
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              className={currentPage === 1 ? "pointer-events-none opacity-50" : "cursor-pointer"}
            />
          </PaginationItem>

          {generatePageNumbers().map((page) => (
            <PaginationItem key={page}>
              <PaginationLink
                onClick={() => setCurrentPage(page)}
                isActive={currentPage === page}
                className="cursor-pointer"
              >
                {page}
              </PaginationLink>
            </PaginationItem>
          ))}

          <PaginationItem>
            <PaginationNext
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              className={currentPage === totalPages ? "pointer-events-none opacity-50" : "cursor-pointer"}
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    );
  };

  if (isLoading) {
    return (
      <Card className="glass-card">
        <CardContent className="p-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-5 w-24" />
            </div>
            <div className="space-y-3">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-5/6" />
            </div>
            <div className="grid grid-cols-2 gap-4 pt-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-3 w-2/3" />
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (totalReviews === 0) {
    return (
      <Card>
        <CardContent className="p-6 text-center text-muted-foreground">
          No reviews available for this product.
        </CardContent>
      </Card>
    );
  }

  // Get current page reviews
  const startIndex = (currentPage - 1) * reviewsPerPage;
  const endIndex = startIndex + reviewsPerPage;
  const currentReviews = sortedReviews.slice(startIndex, endIndex);

  return (
    <Card className="glass-card">
      <CardContent className="p-6">
        <div className="space-y-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <h3 className="text-lg font-semibold">
              Product Reviews ({totalFilteredReviews}{selectedSources.size > 0 ? ` / ${totalReviews}` : ''})
            </h3>
            <div className="flex items-center gap-2">
              {totalPages > 1 && (
                <span className="text-sm text-muted-foreground">
                  Page {currentPage} of {totalPages}
                </span>
              )}
            </div>
          </div>

          {/* Sort and Filter Controls */}
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center flex-wrap">
            {/* Sort Dropdown */}
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium">Sort:</label>
              <select
                value={sortBy}
                onChange={(e) => {
                  setSortBy(e.target.value as any);
                  setCurrentPage(1);
                }}
                className="px-3 py-1 rounded-lg border border-border bg-background text-sm hover:border-primary/50 transition-colors"
              >
                <option value="latest">Latest First</option>
                <option value="relevance">Most Relevant</option>
                <option value="rating-high">Highest Rated</option>
                <option value="rating-low">Lowest Rated</option>
              </select>
            </div>

            {/* Source Filter */}
            {uniqueSources.length > 0 && (
              <div className="flex items-center gap-2 flex-wrap">
                <Filter className="h-4 w-4" />
                <label className="text-sm font-medium">Sources:</label>
                {uniqueSources.map((source) => (
                  <Button
                    key={source}
                    variant={selectedSources.has(source) ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => toggleSource(source)}
                    className="text-xs h-8"
                  >
                    {source}
                  </Button>
                ))}
                {selectedSources.size > 0 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setSelectedSources(new Set());
                      setCurrentPage(1);
                    }}
                    className="text-xs h-8 text-muted-foreground"
                  >
                    Clear All
                  </Button>
                )}
              </div>
            )}
          </div>

          {reviewsSummary && (
            <div className="bg-muted/50 rounded-lg p-4">
              <h4 className="font-medium mb-2">Review Summary</h4>
              {typeof reviewsSummary === 'string' ? (
                <p className="text-sm text-muted-foreground">{reviewsSummary}</p>
              ) : (
                <div className="space-y-2 text-sm text-muted-foreground">
                  {reviewsSummary.average_rating && (
                    <p><strong>Average Rating:</strong> {reviewsSummary.average_rating}/5</p>
                  )}
                  {reviewsSummary.overall_sentiment && (
                    <p><strong>Sentiment:</strong> {reviewsSummary.overall_sentiment.replace(/_/g, ' ').toUpperCase()}</p>
                  )}
                  {reviewsSummary.common_praises && reviewsSummary.common_praises.length > 0 && (
                    <div>
                      <strong>Common Praises:</strong> {reviewsSummary.common_praises.join(', ')}
                    </div>
                  )}
                  {reviewsSummary.common_complaints && reviewsSummary.common_complaints.length > 0 && (
                    <div>
                      <strong>Common Complaints:</strong> {reviewsSummary.common_complaints.join(', ')}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          <div className="space-y-4">
            {currentReviews.map((review, index) => (
          <motion.div
            key={review.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <Card className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2 flex-wrap gap-2">
                      <div className="flex">{renderStars(review.rating)}</div>
                      <span className="text-sm font-medium">
                        {review.rating}/5
                      </span>
                      {review.verified_purchase && (
                        <Badge variant="outline" className="text-xs bg-green-50 dark:bg-green-950 text-green-700 dark:text-green-300 border-green-200 dark:border-green-800">
                          <ShieldCheck className="h-3 w-3 mr-1" />
                          Verified Purchase
                        </Badge>
                      )}
                      {/* Verified badges for enriched API, Google, and store reviews - NOT for forums/community */}
                      {review.source && (
                        !review.source?.toLowerCase().includes('forum') &&
                        !review.source?.toLowerCase().includes('reddit') &&
                        !review.source?.toLowerCase().includes('community') &&
                        <Badge 
                          variant="outline" 
                          className="text-xs bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800"
                        >
                          <ShieldCheck className="h-3 w-3 mr-1" />
                          Verified
                        </Badge>
                      )}
                    </div>

                    <div className="flex items-center space-x-2 text-sm text-muted-foreground flex-wrap gap-2">
                      <span>{review.reviewer_name || 'Anonymous'}</span>
                      <span>•</span>
                      <span>{formatDate(review.review_date)}</span>
                      {review.source && (
                        <>
                          <span>•</span>
                          <Badge 
                            variant="secondary" 
                            className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200"
                          >
                            {review.source === 'FireCrawl' ? 'Official Review' : (review.source || 'Google Shopping')}
                          </Badge>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                {review.title && (
                  <h4 className="font-medium mb-2">{review.title}</h4>
                )}

                {review.review_text && (
                  <p className="text-muted-foreground leading-relaxed mb-4">
                    {review.review_text}
                  </p>
                )}

                {(review.positive_feedback > 0 || review.negative_feedback > 0) && (
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <div className="flex items-center space-x-1">
                      <ThumbsUp className="h-4 w-4" />
                      <span>{review.positive_feedback}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <ThumbsDown className="h-4 w-4" />
                      <span>{review.negative_feedback}</span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

          {renderPagination()}
        </div>
      </CardContent>
    </Card>
  );
};