import { ShoppingBag, ArrowRight, ShoppingCart, Search } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Product } from "@/types/search";
import { Link } from "react-router-dom";
import React from "react";
import { useSearchUrl } from "@/hooks/useSearchUrl";
import { formatPriceWithCurrency } from "@/utils/currencyUtils";
import { generateSlug } from "@/utils/slugUtils";

interface ProductGridProps {
  products: Product[];
  totalCount?: number;
  searchQuery?: string;
  showUpgradeBanner?: boolean;
}

export const ProductGrid = ({ products }: ProductGridProps) => {
  const { country } = useSearchUrl();
  
  // Filter out products with invalid IDs before rendering
  const validProducts = products.filter(product => {
    const hasValidId = product.id && typeof product.id === 'string' && product.id !== 'undefined' && product.id !== 'null';
    return hasValidId;
  });

  // Save search results to localStorage for product details page fallback
  React.useEffect(() => {
    if (validProducts.length > 0) {
      // Save the complete raw API response to localStorage
      // This preserves all fields including immersive data
      localStorage.setItem("lastSearchResults", JSON.stringify(validProducts));
      console.log("Saved complete search results to localStorage:", validProducts.length, "products");
      console.log("Sample product fields:", Object.keys(validProducts[0]));
    }
  }, [validProducts]);

  if (validProducts.length === 0) {
    return (
      <div className="text-center py-16">
        <ShoppingBag className="h-12 w-12 mx-auto mb-4 text-muted-foreground/50" />
        <h3 className="text-lg font-medium mb-2">No products found</h3>
        <p className="text-muted-foreground">
          Try searching for a different product or keyword.
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {validProducts.map((product) => (
          <Card key={product.id} className="group hover-lift glass-card relative overflow-hidden">
            <CardContent className="p-6">
              {/* Product Image Container */}
              <div className="aspect-video rounded-xl overflow-hidden mb-6 bg-muted/50 group-hover:shadow-lg transition-all duration-300 flex items-center justify-center">
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.title}
                    className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
                    onError={(e) => {
                      const target = e.currentTarget;
                      target.style.display = 'none';
                      const placeholder = target.nextElementSibling as HTMLElement;
                      if (placeholder) placeholder.style.display = 'flex';
                    }}
                  />
                ) : null}
                <div className="w-full h-full bg-muted/50 rounded-lg flex items-center justify-center text-muted-foreground" style={{ display: product.image_url ? 'none' : 'flex' }}>
                  <ShoppingBag className="h-12 w-12 text-muted-foreground/50" />
                </div>
              </div>

              {/* Product Info */}
              <div className="space-y-3">
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <h3 className="font-semibold line-clamp-2 group-hover:text-primary transition-colors flex-1" title={product.title}>
                      {product.title}
                    </h3>
                  </div>
                  
                  {/* Source Badge */}
                  <div className="mb-2">
                    {product.source === 'amazon' ? (
                      <Badge className="bg-gradient-to-r from-orange-500 to-yellow-500 text-white border-0 flex items-center gap-1 w-fit">
                        <ShoppingCart className="h-3 w-3" />
                        Amazon
                      </Badge>
                    ) : (
                      <Badge className="bg-gradient-to-r from-blue-500 to-blue-600 text-white border-0 flex items-center gap-1 w-fit">
                        <Search className="h-3 w-3" />
                        {product.source || 'Unknown'}
                      </Badge>
                    )}
                  </div>
                  
                  <p className="text-2xl font-bold text-primary">
                    {formatPriceWithCurrency(product.price, country)}
                  </p>
                </div>

                {/* Rating Badge */}
                {product.site_rating && (
                  <div className="flex items-center space-x-2">
                    <Badge variant="secondary" className="font-semibold glass-card text-primary border-primary/20">
                      ⭐ {product.site_rating.toFixed(1)}/5
                    </Badge>
                    {product.reviews_count && (
                      <span className="text-xs text-muted-foreground">
                        ({product.reviews_count} reviews)
                      </span>
                    )}
                  </div>
                )}

                {/* CTA Button */}
                <Button
                  className="w-full rounded-xl bg-gradient-primary hover:shadow-lg hover:shadow-primary/25 border-0 font-medium text-primary-foreground"
                  size="default"
                  disabled={!product.id || product.id === 'undefined'}
                  onClick={() => {
                    if (product.id && product.id !== 'undefined') {
                      // Save the complete raw product object with all API fields
                      localStorage.setItem('currentProduct', JSON.stringify(product));
                      console.log('Saved complete product to currentProduct:', product.id);
                      console.log('Product fields:', Object.keys(product));
                      console.log('Immersive link:', (product as any).immersive_product_api_link);
                      // Generate slug and navigate to product details
                      const slug = generateSlug(product.title, product.id);
                      window.location.href = `/product/${slug}`;
                    }
                  }}
                >
                  View Product
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};
