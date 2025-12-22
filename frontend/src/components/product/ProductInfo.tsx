import { Star, ArrowRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAnalytics } from "@/hooks/useAnalytics";
import { useParams } from "react-router-dom";
import { ProductSource } from "./ProductSource";
import { sanitizeHtml, isHtmlContent } from "@/utils/htmlSanitizer";
import { useSearchUrl } from "@/hooks/useSearchUrl";
import { formatPriceIntl } from "@/utils/currencyUtils";

interface ProductInfoProps {
  title: string;
  price: number;
  imoScore?: number;
  aiVerdictScore?: number;
  verdictStatus?: "idle" | "processing" | "ready" | "error";
  description?: string;
  productUrl: string;
  source: 'Amazon' | 'Walmart' | 'Home Depot' | 'Google';
  priceRange?: string;
  enrichedProductDescription?: string;
}

export const ProductInfo = ({ title, price, imoScore, aiVerdictScore, verdictStatus, description, productUrl, source, priceRange, enrichedProductDescription }: ProductInfoProps) => {
  const { productId } = useParams<{ productId: string }>();
  const { trackAffiliateClick } = useAnalytics();
  const { country } = useSearchUrl();

  const formatPrice = (price: number) => {
    return formatPriceIntl(price, country || 'United States');
  };

  const getAffiliateUrl = (url: string, source: string): string => {
    if (source === 'Amazon') {
      // Handle relative URLs by converting to absolute
      const fullUrl = url.startsWith('/') ? `https://www.amazon.com${url}` : url;
      
      // Check if URL already has query parameters
      const separator = fullUrl.includes('?') ? '&' : '?';
      
      // Append Amazon Associate tag
      return `${fullUrl}${separator}tag=Imoapp01-20`;
    }
    
    // Return unchanged for other sources (Walmart support coming soon)
    return url;
  };

  const handleAffiliateClick = () => {
    if (productId) {
      trackAffiliateClick(productId, source);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-start justify-between gap-4 mb-4">
          <h1 className="text-4xl font-bold tracking-tight flex-1">
            {title}
          </h1>
          <ProductSource source={source} />
        </div>
        
        {/* Price Display */}
        <div className="space-y-2 mb-6">
          {/* <p className="text-3xl font-bold text-primary">
          
          </p> */}
          {priceRange && (
            <p className="text-xl text-muted-foreground">
              Price Range: <span className="font-semibold text-foreground">  {priceRange}</span>
            </p>
          )}
        </div>

        {/* AI Verdict Score - Priority over basic IMO score */}
        {aiVerdictScore !== undefined ? (
          <div className="flex items-center space-x-2 mb-6">
            {verdictStatus === "processing" ? (
              <Badge variant="secondary" className="font-semibold glass-card text-amber-600 dark:text-amber-400 border-amber-200 dark:border-amber-900 text-lg px-4 py-2 animate-pulse">
                <Star className="h-4 w-4 mr-2" />
                🤖 IMO Score Loading...
              </Badge>
            ) : (
              <Badge variant="secondary" className="font-semibold glass-card bg-gradient-to-r from-purple-500/10 to-blue-500/10 text-purple-600 dark:text-purple-400 border-purple-200 dark:border-purple-900 text-lg px-4 py-2">
                <Star className="h-4 w-4 mr-2" />
                IMO Score: {aiVerdictScore.toFixed(1)}/10
              </Badge>
            )}
          </div>
        ) : imoScore ? (
          <div className="flex items-center space-x-2 mb-6">
            <Badge variant="secondary" className="font-semibold glass-card text-primary border-primary/20 text-lg px-4 py-2">
              <Star className="h-4 w-4 mr-2" />
              Rating: {imoScore}/10
            </Badge>
          </div>
        ) : null}

        {/* Enhanced Product Description */}
        {(enrichedProductDescription || description) && (
          <div className="text-muted-foreground text-base leading-relaxed mb-8 prose prose-slate dark:prose-invert max-w-none">
            {isHtmlContent(enrichedProductDescription || description) ? (
              <div 
                dangerouslySetInnerHTML={{ 
                  __html: sanitizeHtml(enrichedProductDescription || description || '') 
                }}
                className="[&>p]:mb-4 [&>h2]:text-xl [&>h2]:font-bold [&>h2]:mb-3 [&>h3]:text-lg [&>h3]:font-semibold [&>h3]:mb-2 [&>ul]:mb-4 [&>li]:mb-1 [&>strong]:font-semibold line-clamp-3"
              />
            ) : (
              <p className="line-clamp-3">{enrichedProductDescription || description}</p>
            )}
          </div>
        )}
      </div>

      {/* Buy Button */}
      <Button 
        asChild 
        size="lg"
        className="w-full rounded-xl bg-gradient-primary hover:shadow-lg hover:shadow-primary/25 border-0 font-medium text-lg py-6 text-primary-foreground"
      >
        <a 
          href="#whereToBuy"
          rel="noopener noreferrer"
          onClick={handleAffiliateClick}
        >
          Buy Now
          <ArrowRight className="h-5 w-5 ml-2" />
        </a>
      </Button>
    </div>
  );
};