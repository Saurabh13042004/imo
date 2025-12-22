import { useParams, Link } from "react-router-dom";
import { useState, useEffect } from "react";
import { ArrowLeft, ShoppingBag, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useAnalytics } from "@/hooks/useAnalytics";
import { useParallax } from "@/hooks/useParallax";
import { useSearchUrl } from "@/hooks/useSearchUrl";
import { useAIVerdict } from "@/hooks/useAIVerdict";
import { useCommunityReviews } from "@/hooks/useCommunityReviews";
import { useStoreReviews } from "@/hooks/useStoreReviews";
import { formatPriceWithCurrency } from "@/utils/currencyUtils";
import { API_BASE_URL } from "@/config/api";
import { extractIdFromSlug } from "@/utils/slugUtils";
// import { useProductBasic, useProductReviews, useProductVideos } from "@/hooks/useProductDetails";

import { ProductLikeButton } from "@/components/product/ProductLikeButton";
import { ProductImages } from "@/components/product/ProductImages";
import { ProductInfo } from "@/components/product/ProductInfo";
import { ProductInfoSkeleton } from "@/components/product/ProductInfoSkeleton";
import { ProductProsAndCons } from "@/components/product/ProductProsAndCons";
import { ProductReviews } from "@/components/product/ProductReviews";
import { ShortVideoReviews } from "@/components/product/ShortVideoReviews";
// import { ProductReviewsSkeleton } from "@/components/product/ProductReviewsSkeleton";
import { VideoReviews } from "@/components/product/VideoReviews";

// import { YouTubeVideosSkeleton } from "@/components/product/YouTubeVideosSkeleton";
import { SearchAccessGate } from "@/components/product/SearchAccessGate";
import { Product } from "@/types/search";
import { useSearchAccess } from "@/hooks/useSearchAccess";
// import { useProductPriceComparison } from "@/hooks/useProductPriceComparison";

const ProductDetails = () => {
  useParallax();
  const { slug } = useParams<{ slug: string }>();
  // Extract product ID from slug
  const productId = slug ? extractIdFromSlug(slug) : undefined;
  const { zipcode, country } = useSearchUrl();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [enrichedData, setEnrichedData] = useState<any>(null);
  const [enrichmentLoading, setEnrichmentLoading] = useState(false);
  const [googleReviews, setGoogleReviews] = useState<any>(null);
  const [refreshReviews, setRefreshReviews] = useState(0);
  const { toast } = useToast();
  const { trackProductView } = useAnalytics();

  // Use AI Verdict hook for all products (not Amazon-specific)
  const { verdict: aiVerdict, status: verdictStatus } = useAIVerdict(
    productId,
    enrichedData
  );

  // Memoize store URLs - don't wait for enrichedData to fetch from stores
  const storeUrls = enrichedData?.immersive_data?.product_results?.stores
    ?.filter((s: any) => s.link)
    ?.map((s: any) => s.link) || [];

  // Use Community Reviews hook - start immediately, don't wait for enrichedData
  const communityReviews = useCommunityReviews(
    product?.title || '',
    product?.brand
  );

  // Use Store Reviews hook - start immediately with empty URLs, update when enrichedData arrives
  const storeReviews = useStoreReviews(
    product?.title || '',
    storeUrls.length > 0 ? storeUrls : undefined
  );

  // Fetch Google Shopping reviews - independent, non-blocking
  // This runs separately and appends results without blocking other APIs
  useEffect(() => {
    if (!product?.product_url || !product?.title) return;

    // Don't wait for enrichedData - start fetching immediately
    const fetchGoogleReviews = async () => {
      try {
        // Don't set loading - just fetch in background
        const response = await fetch(`${API_BASE_URL}/api/v1/reviews/google`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            product_name: product.title,
            google_shopping_url: product.product_url || ''
          })
        });

        if (response.ok) {
          const data = await response.json();
          // Just set the data - don't show loading state
          setGoogleReviews(data);
          // Show toast notification when reviews arrive
          if (data?.reviews?.length > 0) {
            toast({
              title: "IMO AI Just added new reviews",
              description: `${data.reviews.length} Google Shopping reviews loaded`,
              variant: "default",
              className: "fixed bottom-4 left-4"
            });
          }
        }
      } catch (error) {
        console.error('Error fetching Google Shopping reviews:', error);
        // Silently fail - no blocking, no error state
      }
    };

    fetchGoogleReviews();
  }, [product?.product_url, product?.title, toast]);

  // Show notification when community reviews arrive
  useEffect(() => {
    if (communityReviews.reviews && communityReviews.reviews.length > 0 && communityReviews.status === 'loaded') {
      toast({
        title: "IMO AI Just added new reviews",
        description: `${communityReviews.reviews.length} community reviews loaded`,
        variant: "default",
        className: "fixed bottom-4 left-4"
      });
    }
  }, [communityReviews.reviews?.length, communityReviews.status, toast]);

  // Show notification when store reviews arrive
  useEffect(() => {
    if (storeReviews.reviews && storeReviews.reviews.length > 0 && storeReviews.status === 'loaded') {
      toast({
        title: "IMO AI Just added new reviews",
        description: `${storeReviews.reviews.length} store reviews loaded`,
        variant: "default",
        className: "fixed bottom-4 left-4"
      });
    }
  }, [storeReviews.reviews?.length, storeReviews.status, toast]);

  // Validate productId early
  const isValidProductId = productId && 
    typeof productId === 'string' && 
    productId !== 'undefined' && 
    productId !== 'null' &&
    productId.length > 0;

  // Load product from localStorage
  useEffect(() => {
    if (!isValidProductId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      
      // Try currentProduct first
      let foundProduct = null;
      const currentProductStr = localStorage.getItem("currentProduct");
      
      if (currentProductStr) {
        const parsedProduct = JSON.parse(currentProductStr);
        if (parsedProduct.id === productId) {
          foundProduct = parsedProduct;
        }
      }
      
      // If not found, search in lastSearchResults
      if (!foundProduct) {
        const searchResults = localStorage.getItem("lastSearchResults");
        if (searchResults) {
          const results = JSON.parse(searchResults);
          foundProduct = results.find((p: any) => p.id === productId);
        }
      }
      
      if (foundProduct) {
        setProduct(foundProduct);
        // Track product view
        if (trackProductView && productId) {
          trackProductView(productId, foundProduct.query);
        }
      }
    } catch (error) {
      console.error("Error loading product from localStorage:", error);
      toast({
        title: "Error",
        description: "Could not load product data",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  }, [isValidProductId, productId, toast, trackProductView]);

  // Fetch enriched data for all products (product-agnostic)
  useEffect(() => {
    if (!product || !productId) return;
    
    const fetchEnrichedData = async () => {
      try {
        setEnrichmentLoading(true);
        console.log(`Fetching enriched product data for: ${productId}`);
        
        // For all products - fetch from enriched endpoint
        const immersiveApiLink = (product as any).immersive_product_api_link;
        
        if (!immersiveApiLink) {
          console.log("No immersive_product_api_link found, using base product data");
          setEnrichmentLoading(false);
          return;
        }

        const response = await fetch(
          `${API_BASE_URL}/api/v1/product/enriched/${productId}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              immersive_api_link: immersiveApiLink
            })
          }
        );

        if (!response.ok) {
          console.warn(`Failed to fetch enriched data: ${response.status}`);
          return;
        }

        const data = await response.json();
        console.log("Enriched product data received:", data);
        
        if (data) {
          setEnrichedData(data);
          console.log("Enriched data loaded successfully");
        }
      } catch (error) {
        console.error("Error fetching enriched product data:", error);
      } finally {
        setEnrichmentLoading(false);
      }
    };

    fetchEnrichedData();
  }, [product, productId]);

  // Handle invalid product ID
  if (!isValidProductId) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <ShoppingBag className="h-12 w-12 mx-auto mb-4 text-muted-foreground/50" />
          <h3 className="text-lg font-medium mb-2">Invalid Product ID</h3>
          <p className="text-muted-foreground mb-4">
            The product link appears to be broken or invalid.
          </p>
          <Button asChild>
            <Link to="/search">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Search
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">

      {!product && !loading ? (
        <div className="min-h-screen bg-background flex items-center justify-center">
          <div className="text-center">
            <ShoppingBag className="h-12 w-12 mx-auto mb-4 text-muted-foreground/50" />
            <h3 className="text-lg font-medium mb-2">Product not found</h3>
            <p className="text-muted-foreground mb-4">
              The product you're looking for doesn't exist.
            </p>
            <Button asChild>
              <Link to="/search">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Search
              </Link>
            </Button>
          </div>
        </div>
      ) : (
        <div className="relative overflow-clip">
          <div className="absolute inset-0 bg-gradient-background opacity-35 parallax-background"></div>
          
          <div className="absolute -top-32 -left-32 w-96 h-96 bg-gradient-primary rounded-full mix-blend-multiply filter blur-3xl opacity-[0.35] dark:opacity-[0.15] dark:mix-blend-normal parallax-slow"></div>
          <div className="absolute top-1/3 -right-32 w-80 h-80 bg-gradient-secondary rounded-full mix-blend-multiply filter blur-3xl opacity-[0.4] dark:opacity-[0.18] dark:mix-blend-normal parallax-medium"></div>

          <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6 }}
              className="space-y-8"
            >
              {/* Product Header */}
              {loading ? (
                <ProductInfoSkeleton />
              ) : product ? (
                <>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                    <div className="space-y-6">
                      <ProductImages 
                        title={product.title}
                        imageUrl={product.image_url}
                        imageUrls={
                          enrichedData?.immersive_data?.product_results?.thumbnails?.length > 0
                            ? enrichedData.immersive_data.product_results.thumbnails
                            : (product as any).image_urls
                        }
                      />
                    </div>

                    <div className="space-y-4">
                      <ProductInfo 
                        title={product.title}
                        price={product.price}
                        imoScore={product.imo_score}
                        aiVerdictScore={aiVerdict?.imo_score}
                        verdictStatus={verdictStatus}
                        description={enrichedData?.bullet_points ? enrichedData.bullet_points.split('\n')[0] : (enrichedData?.description || product.description)}
                        productUrl={product.product_url}
                        source={product.source as any}
                      />
                      <div className="flex justify-start">
                        <ProductLikeButton productId={product.id} />
                      </div>
                    </div>
                  </div>

                  {/* Pros and Cons */}
                  <ProductProsAndCons 
                    pros={enrichedData?.analysis?.pros || product.pros}
                    cons={enrichedData?.analysis?.cons || product.cons}
                  />
                </>
              ) : null}

              {/* Reviews and Videos Sections - Ready for API integration */}
              {product && (
                <div className="space-y-8 border-t border-border/50 pt-8">
                  {/* AI Verdict Section (for ALL products) */}
                  {aiVerdict && verdictStatus === "ready" && (
                    <motion.div
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ duration: 0.4 }}
                      className="bg-gradient-to-br from-primary/10 to-secondary/10 rounded-lg border border-primary/20 p-6 space-y-4"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h2 className="text-2xl font-bold text-foreground mb-2">
                            IMO AI Verdict
                          </h2>
                          <p className="text-muted-foreground">
                            {aiVerdict.summary}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-4xl font-bold text-primary">
                            {aiVerdict.imo_score?.toFixed(1) || "N/A"}
                          </div>
                          <p className="text-xs text-muted-foreground">out of 10</p>
                        </div>
                      </div>

                      {aiVerdict.who_should_buy && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-border/30">
                          <div>
                            <p className="text-sm font-semibold text-green-600 dark:text-green-400 mb-1">✓ Who should buy</p>
                            <p className="text-sm text-muted-foreground">{aiVerdict.who_should_buy}</p>
                          </div>
                          {aiVerdict.who_should_avoid && (
                            <div>
                              <p className="text-sm font-semibold text-orange-600 dark:text-orange-400 mb-1">✗ Who should avoid</p>
                              <p className="text-sm text-muted-foreground">{aiVerdict.who_should_avoid}</p>
                            </div>
                          )}
                        </div>
                      )}

                      {aiVerdict.deal_breakers && aiVerdict.deal_breakers.length > 0 && (
                        <div className="pt-4 border-t border-border/30">
                          <p className="text-sm font-semibold text-red-600 dark:text-red-400 mb-2">⚠ Deal Breakers</p>
                          <ul className="text-sm text-muted-foreground space-y-1">
                            {aiVerdict.deal_breakers.map((issue: string, idx: number) => (
                              <li key={idx}>• {issue}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </motion.div>
                  )}

                  {/* AI Verdict Processing State */}
                  {verdictStatus === "processing" && !aiVerdict && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex items-center justify-center py-12 gap-3 bg-gradient-to-br from-primary/5 to-secondary/5 rounded-lg border border-border/30 p-6"
                    >
                      <Loader2 className="h-5 w-5 animate-spin text-primary" />
                      <p className="text-sm text-muted-foreground">AI is analyzing this product...</p>
                    </motion.div>
                  )}
                  
                  {/* Detailed Product Information - For Products with Enriched Data */}
                  {enrichedData && !enrichmentLoading && (
                    <motion.div
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ duration: 0.4 }}
                      className="space-y-6"
                    >
                      <div className="border-b border-border/50 pb-4">
                        <h2 className="text-2xl font-bold text-foreground">
                          Product Details
                        </h2>
                        <p className="text-sm text-muted-foreground mt-1">
                          Complete specifications from Amazon
                        </p>
                      </div>

                      {/* Price Comparison - Amazon buybox */}
                      {enrichedData.buybox && enrichedData.buybox.filter((offer: any) => offer.price && offer.price > 0).length > 0 && (
                        <div className="bg-card rounded-lg border border-border/50 p-6 space-y-4">
                          <h3 className="font-semibold text-lg">Where to Buy</h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {enrichedData.buybox.filter((offer: any) => offer.price && offer.price > 0).map((offer: any, idx: number) => (
                              <div
                                key={idx}
                                className="p-4 bg-background rounded-lg border border-border/30"
                              >
                                <p className="font-medium text-sm mb-2">Amazon.com</p>
                                <p className="text-lg font-bold text-primary">{formatPriceWithCurrency(offer.price, country)}</p>
                                <p className="text-xs text-muted-foreground mt-2">{offer.stock}</p>
                                {offer.delivery_details && (
                                  <ul className="text-xs text-muted-foreground mt-2 space-y-1">
                                    {offer.delivery_details.slice(0, 2).map((delivery: any, i: number) => (
                                      <li key={i}>• {delivery.type}</li>
                                    ))}
                                  </ul>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* External Stores from SerpAPI */}
                      {enrichedData.external_stores && enrichedData.external_stores.filter((store: any) => store.extracted_price > 0 || store.price > 0).length > 0 && (
                        <div className="bg-card rounded-lg border border-border/50 p-6 space-y-4">
                          <h3 className="font-semibold text-lg">Other Retailers</h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {enrichedData.external_stores.filter((store: any) => store.extracted_price > 0 || store.price > 0).slice(0, 4).map((store: any, idx: number) => (
                              <a
                                key={idx}
                                href={store.link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="p-4 bg-background rounded-lg border border-border/30 hover:border-primary/50 transition-colors"
                              >
                                <p className="font-medium text-sm mb-2">{store.name}</p>
                                <p className="text-lg font-bold text-primary">{formatPriceWithCurrency(store.extracted_price || store.price, country)}</p>
                                {store.details_and_offers && (
                                  <ul className="text-xs text-muted-foreground mt-2 space-y-1">
                                    {store.details_and_offers.slice(0, 2).map((offer: string, i: number) => (
                                      <li key={i}>• {offer}</li>
                                    ))}
                                  </ul>
                                )}
                              </a>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Product Description/Features */}
                      {enrichedData.bullet_points && (
                        <div className="bg-card rounded-lg border border-border/50 p-6 space-y-4">
                          <h3 className="font-semibold text-lg">About This Product</h3>
                          <ul className="text-sm text-muted-foreground leading-relaxed space-y-2">
                            {(typeof enrichedData.bullet_points === 'string' 
                              ? enrichedData.bullet_points.split('\n') 
                              : enrichedData.bullet_points
                            ).filter((p: string) => p?.trim()).map((point: string, idx: number) => (
                              <li key={idx} className="flex gap-2">
                                <span className="text-primary">•</span>
                                <span>{point}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Rating Distribution */}
                      {enrichedData.rating_distribution && enrichedData.rating_distribution.length > 0 && (
                        <div className="bg-card rounded-lg border border-border/50 p-6 space-y-4">
                          <h3 className="font-semibold text-lg">Rating Distribution</h3>
                          <div className="space-y-3">
                            {enrichedData.rating_distribution.map((rating: any) => (
                              <div key={rating.rating} className="flex items-center gap-3">
                                <span className="text-sm font-medium w-12">{rating.rating} ★</span>
                                <div className="flex-1 bg-background rounded-full h-2">
                                  <div 
                                    className="bg-primary rounded-full h-2"
                                    style={{ width: `${rating.percentage}%` }}
                                  />
                                </div>
                                <span className="text-xs text-muted-foreground w-8">{rating.percentage}%</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </motion.div>
                  )}
                  {/* Enriched Product Data Section - for non-Amazon products */}
                  {enrichedData?.immersive_data && !enrichmentLoading && (
                    <motion.div
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ duration: 0.4 }}
                      className="space-y-6"
                    >
                      <div className="border-b border-border/50 pb-4">
                        <h2 className="text-2xl font-bold text-foreground">
                          Detailed Product Information
                        </h2>
                        <p className="text-sm text-muted-foreground mt-1">
                          Aggregated from multiple retailers
                        </p>
                      </div>

                      {/* Price Comparison - SerpAPI stores */}
                      {enrichedData.immersive_data.product_results?.stores && enrichedData.immersive_data.product_results.stores.filter((store: any) => store.extracted_price > 0 || store.price > 0).length > 0 && (
                        <div className="bg-card rounded-lg border border-border/50 p-6 space-y-4">
                          <h3 className="font-semibold text-lg">Where to Buy</h3>
                          
                          {/* SerpAPI stores */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {enrichedData.immersive_data.product_results.stores.filter((store: any) => store.extracted_price > 0 || store.price > 0).slice(0, 4).map((store: any, idx: number) => (
                              <a
                                key={idx}
                                href={store.link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="p-4 bg-background rounded-lg border border-border/30 hover:border-primary/50 transition-colors"
                              >
                                <p className="font-medium text-sm mb-2">{store.name}</p>
                                <p className="text-lg font-bold text-primary">{formatPriceWithCurrency(store.extracted_price || store.price, country)}</p>
                                {store.details_and_offers && (
                                  <ul className="text-xs text-muted-foreground mt-2 space-y-1">
                                    {store.details_and_offers.slice(0, 2).map((offer: string, i: number) => (
                                      <li key={i}>• {offer}</li>
                                    ))}
                                  </ul>
                                )}
                              </a>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Product Description/Features */}
                      {enrichedData.immersive_data?.product_results?.about_the_product?.description && (
                        <div className="bg-card rounded-lg border border-border/50 p-6 space-y-4">
                          <h3 className="font-semibold text-lg">About This Product</h3>
                          
                          {/* SerpAPI description */}
                          <p className="text-sm text-muted-foreground leading-relaxed">
                            {enrichedData.immersive_data.product_results.about_the_product.description.substring(0, 500)}
                            {enrichedData.immersive_data.product_results.about_the_product.description.length > 500 && "..."}
                          </p>
                        </div>
                      )}

                      {/* Product Features */}
                      {enrichedData.immersive_data.product_results?.about_the_product?.features && enrichedData.immersive_data.product_results.about_the_product.features.length > 0 && (
                        <div className="bg-card rounded-lg border border-border/50 p-6 space-y-4">
                          <h3 className="font-semibold text-lg">Key Specifications</h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {enrichedData.immersive_data.product_results.about_the_product.features.slice(0, 8).map((feature: any, idx: number) => (
                              <div key={idx} className="py-2 border-b border-border/30 last:border-0">
                                <p className="text-xs font-medium text-muted-foreground">{feature.title}</p>
                                <p className="text-sm font-semibold text-foreground mt-1">{feature.value}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Rating Distribution */}
                      {enrichedData.immersive_data.product_results?.ratings && enrichedData.immersive_data.product_results.ratings.length > 0 && (
                        <div className="bg-card rounded-lg border border-border/50 p-6 space-y-4">
                          <h3 className="font-semibold text-lg">Rating Distribution</h3>
                          <div className="space-y-3">
                            {/* SerpAPI ratings */}
                            {enrichedData.immersive_data.product_results.ratings.map((rating: any) => (
                              <div key={rating.stars} className="flex items-center gap-3">
                                <span className="text-sm font-medium w-12">{rating.stars} ★</span>
                                <div className="flex-1 bg-background rounded-full h-2">
                                  <div 
                                    className="bg-primary rounded-full h-2"
                                    style={{ 
                                      width: enrichedData.immersive_data.product_results.ratings.length > 0 
                                        ? `${(rating.amount / Math.max(...enrichedData.immersive_data.product_results.ratings.map((r: any) => r.amount))) * 100}%`
                                        : '0%'
                                    }}
                                  />
                                </div>
                                <span className="text-xs text-muted-foreground w-8">{rating.amount}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </motion.div>
                  )}

                  {/* Enrichment Loading State */}
                  {enrichmentLoading && !enrichedData && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex items-center justify-center py-12 gap-3"
                    >
                      <Loader2 className="h-5 w-5 animate-spin text-primary" />
                      <p className="text-sm text-muted-foreground">Loading detailed product information...</p>
                    </motion.div>
                  )}

                  {/* YouTube Videos Section */}
                  {enrichedData?.immersive_data?.product_results?.videos && (
                    <VideoReviews
                      productId={productId || ""} 
                      videos={(enrichedData.immersive_data.product_results.videos as any[]).map((video: any) => ({
                        id: video.link || `${video.title}-${Math.random()}`,
                        title: video.title || '',
                        description: video.description || '',
                        video_url: video.link || '',
                        thumbnail_url: video.thumbnail || '',
                        views: 0,
                        likes: 0,
                        platform: 'YouTube'
                      }))}
                    />
                  )}

                  {/* Short Video Reviews (YouTube Shorts / TikTok / Instagram Reels) */}
                  {productId && enrichedData && (
                    <ShortVideoReviews 
                      productId={productId} 
                      productTitle={enrichedData.immersive_data.product_results.title}
                    />
                  )}

                  {/* User Reviews Section - Combined All Sources */}
                  <ProductReviews 
                    productId={productId || ""}
                    reviews={[
                      // Amazon reviews from unified response (canonical source)
                      ...(enrichedData?.amazon_reviews?.map((review: any) => ({
                        id: review.id,
                        external_review_id: review.id,
                        reviewer_name: review.author,
                        rating: review.rating,
                        title: review.title,
                        review_text: review.content,
                        verified_purchase: review.is_verified,
                        review_date: review.timestamp,
                        positive_feedback: review.helpful_count || 0,
                        negative_feedback: 0,
                        source: "Amazon"
                      })) || []),
                      // External reviews from enrichment layer (SerpAPI intelligent endpoint)
                      ...(enrichedData?.external_reviews?.map((review: any) => ({
                        id: `${review.source}-${review.author}-${review.title}`,
                        external_review_id: `${review.source}-${review.author}`,
                        reviewer_name: review.author,
                        rating: review.rating || 0,
                        title: review.title,
                        review_text: review.content,
                        verified_purchase: false,
                        review_date: new Date().toISOString(),
                        positive_feedback: 0,
                        negative_feedback: 0,
                        source: review.source
                      })) || []),
                      // User reviews from immersive product endpoint (non-Amazon products)
                      ...(enrichedData?.immersive_data?.product_results?.user_reviews?.map((review: any) => ({
                        id: `${review.source}-${review.user_name}-${review.title}`,
                        external_review_id: `${review.source}-${review.user_name}`,
                        reviewer_name: review.user_name || "Anonymous",
                        rating: review.rating || 0,
                        title: review.title,
                        review_text: review.text,
                        verified_purchase: false,
                        review_date: review.date || new Date().toISOString(),
                        positive_feedback: 0,
                        negative_feedback: 0,
                        source: review.source || "SerpAPI"
                      })) || []),
                      // Community reviews (Reddit + Forums)
                      ...(communityReviews.reviews?.map((review: any) => ({
                        id: `community-${review.source}-${review.text?.substring(0, 20)}`,
                        external_review_id: `community-${review.source}`,
                        reviewer_name: review.author || "Community Member",
                        rating: 0,
                        title: `${review.source} Discussion`,
                        review_text: review.text,
                        verified_purchase: false,
                        review_date: new Date().toISOString(),
                        positive_feedback: 0,
                        negative_feedback: 0,
                        source: review.source
                      })) || []),
                      // Store reviews
                      ...(storeReviews.reviews?.map((review: any) => ({
                        id: `store-${review.store}-${review.text?.substring(0, 20)}`,
                        external_review_id: `store-${review.store}`,
                        reviewer_name: review.author || "Store Reviewer",
                        rating: review.rating || 0,
                        title: `Review from ${review.store}`,
                        review_text: review.text,
                        verified_purchase: false,
                        review_date: new Date().toISOString(),
                        positive_feedback: 0,
                        negative_feedback: 0,
                        source: review.store || "Store"
                      })) || []),
                      // Google Shopping reviews
                      ...(googleReviews?.reviews?.map((review: any) => ({
                        id: `google-${review.reviewer_name}-${review.title}`,
                        external_review_id: `google-${review.reviewer_name}`,
                        reviewer_name: review.reviewer_name,
                        rating: review.rating,
                        title: review.title || "Google Shopping Review",
                        review_text: review.text,
                        verified_purchase: false,
                        review_date: review.date || new Date().toISOString(),
                        positive_feedback: 0,
                        negative_feedback: 0,
                        source: "Google Shopping"
                      })) || [])
                    ]}
                    reviewsSummary={googleReviews?.summary || undefined}
                    refreshReviews={refreshReviews}
                    onRefreshReviews={() => setRefreshReviews(prev => prev + 1)}
                    isLoadingReviews={enrichmentLoading}
                  />
                </div>
              )}
            </motion.div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductDetails;