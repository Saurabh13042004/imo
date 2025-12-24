import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FeaturedProductCard } from "./FeaturedProductCard";
import { ReactNode } from 'react';
import type { Product } from "@/types/search";

// Mock featured products for demo
const FEATURED_PRODUCTS: Product[] = [
  {
    id: "fp1",
    title: "Premium Wireless Headphones",
    description: "High-quality wireless headphones with active noise cancellation",
    price: 199.99,
    image_url: "https://image.cdn.shpy.in/305289/SKU-1621_0-1730988839304.webp?width=600&format=webp",
    product_url: "#",
    source: "Amazon",
    source_id: null,
    imo_score: 9.2,
    pros: ["Excellent sound quality", "30-hour battery life", "Comfortable fit"],
    cons: ["Premium price point"],
    created_at: new Date().toISOString(),
    site_rating: 4.8,
    reviews_count: 2450,
  },
  {
    id: "fp2",
    title: "4K Ultra HD Monitor",
    description: "27-inch 4K monitor perfect for professionals and gamers",
    price: 449.99,
    image_url: "https://www.lg.com/content/dam/channelbtb/lgcom/in/images/business/24ud58-b_atr_eail_in_b/gallery/24UD58-B-DZ-01.jpg",
    product_url: "#",
    source: "Walmart",
    source_id: null,
    imo_score: 8.9,
    pros: ["Sharp 4K display", "USB-C connectivity", "Adjustable stand"],
    cons: ["Can get warm under load"],
    created_at: new Date().toISOString(),
    site_rating: 4.6,
    reviews_count: 1820,
  },
  {
    id: "fp3",
    title: "Mechanical Gaming Keyboard",
    description: "RGB mechanical keyboard with custom switches",
    price: 159.99,
    image_url: "https://aulaindia.com/wp-content/uploads/2022/09/F2066-II_1.jpg",
    product_url: "#",
    source: "Amazon",
    source_id: null,
    imo_score: 8.7,
    pros: ["Responsive switches", "Beautiful RGB lighting", "Programmable keys"],
    cons: ["Quite loud", "Cable only"],
    created_at: new Date().toISOString(),
    site_rating: 4.5,
    reviews_count: 3200,
  },
];

export const FeaturedProductsSection = () => {
  // Demo mode: use mock products instead of API call
  const products = FEATURED_PRODUCTS;
  const isLoading = false;
  const error = null;

  // Don't render anything if we don't have enough products
  if (!isLoading && (!products || products.length < 3)) {
    return null;
  }

  // Show loading state (but maintain layout space)
  if (isLoading) {
    return (
      <section aria-label="Featured products loading" className="py-16">
        <div className="max-w-6xl mx-auto px-4">
          <div className="space-y-4 animate-pulse">
            <div className="h-8 w-64 bg-muted rounded" />
            <div className="h-4 w-96 bg-muted rounded" />
          </div>
        </div>
      </section>
    );
  }

  // Show error state
  if (error) {
    return (
      <section aria-label="Featured products error" className="py-16">
        <div className="max-w-6xl mx-auto px-4">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Failed to load featured products. Please try again later.
            </AlertDescription>
          </Alert>
        </div>
      </section>
    );
  }

  return (
    <section 
      aria-labelledby="featured-products-title"
      className="py-24"
    >
      <div className="max-w-6xl mx-auto px-4">
        <motion.div
          initial={{ 
            opacity: 0, 
            y: 30,
            filter: "blur(5px)" 
          }}
          whileInView={{ 
            opacity: 1, 
            y: 0,
            filter: "blur(0px)" 
          }}
          viewport={{ once: true }}
          transition={{ 
            duration: 0.5,
            ease: [0.25, 0.1, 0.25, 1.0]
          }}
          className="text-center mb-12"
        >
          <h2 
            id="featured-products-title" 
            className="text-4xl font-heading font-normal mb-4"
          >
            Featured Products
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Discover our curated selection of high-quality products with detailed reviews and 
            AI-powered insights.
          </p>
        </motion.div>

        <AnimatePresence>
          {products && (
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
            >
              {products.map((product, index) => (
                <FeaturedProductCard 
                  key={product.id} 
                  product={product} 
                  index={index}
                />
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
};