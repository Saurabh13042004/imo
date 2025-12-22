import { X, ExternalLink, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { motion, AnimatePresence } from "framer-motion";

interface Store {
  name: string;
  logo?: string;
  price?: string;
  extracted_price?: number;
  original_price?: string;
  extracted_original_price?: number;
  link: string;
  tag?: string;
  details_and_offers?: string[];
  rating?: number;
  reviews?: number;
  shipping?: string;
}

interface WhereToBuyModalProps {
  isOpen: boolean;
  onClose: () => void;
  stores: Store[];
  productTitle: string;
}

export const WhereToBuyModal = ({
  isOpen,
  onClose,
  stores,
  productTitle
}: WhereToBuyModalProps) => {
  // Sort stores by price (lowest first)
  const sortedStores = [...stores].sort((a, b) => {
    const priceA = a.extracted_price || Number.MAX_VALUE;
    const priceB = b.extracted_price || Number.MAX_VALUE;
    return priceA - priceB;
  });

  const formatPrice = (price?: number) => {
    if (!price) return "N/A";
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(price);
  };

  const getTagColor = (tag?: string) => {
    if (!tag) return "secondary";
    if (tag.toLowerCase().includes("popular")) return "default";
    if (tag.toLowerCase().includes("price")) return "destructive";
    return "secondary";
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-50"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="w-full max-w-2xl max-h-[90vh] bg-background border border-border rounded-lg shadow-2xl overflow-hidden flex flex-col">
              {/* Header */}
              <div className="bg-background border-b border-border px-6 py-4 flex items-center justify-between flex-shrink-0">
                <div>
                  <h2 className="text-2xl font-bold">Where to Buy</h2>
                  <p className="text-sm text-muted-foreground mt-1">{productTitle}</p>
                </div>
                <button
                  onClick={onClose}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              {/* Stores List */}
              <div className="overflow-y-auto p-6 space-y-4 flex-1">
              {sortedStores.map((store, idx) => (
                <motion.div
                  key={store.name}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="border border-border rounded-lg p-4 hover:border-primary/50 hover:bg-primary/5 transition-all"
                >
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div className="flex items-center gap-3 flex-1">
                      {store.logo && (
                        <img
                          src={store.logo}
                          alt={store.name}
                          className="h-10 w-10 rounded-lg object-cover"
                        />
                      )}
                      <div className="flex-1">
                        <h3 className="font-semibold text-foreground">{store.name}</h3>
                        {store.rating && (
                          <p className="text-sm text-muted-foreground">
                            ⭐ {store.rating} ({store.reviews} reviews)
                          </p>
                        )}
                      </div>
                    </div>

                    {store.tag && (
                      <Badge variant={getTagColor(store.tag) as any} className="whitespace-nowrap">
                        {store.tag === "Best price" ? (
                          <>
                            <Zap className="h-3 w-3 mr-1" />
                            {store.tag}
                          </>
                        ) : (
                          store.tag
                        )}
                      </Badge>
                    )}
                  </div>

                  {/* Price Info */}
                  <div className="mb-3 space-y-1">
                    <div className="flex items-baseline gap-3">
                      <span className="text-2xl font-bold text-primary">
                        {store.price || formatPrice(store.extracted_price)}
                      </span>
                      {store.original_price && (
                        <span className="text-sm text-muted-foreground line-through">
                          {store.original_price || formatPrice(store.extracted_original_price)}
                        </span>
                      )}
                    </div>
                    {store.shipping && (
                      <p className="text-sm text-muted-foreground">
                        {store.shipping === "Free" ? (
                          <span className="text-green-600 dark:text-green-400 font-semibold">✓ {store.shipping} Shipping</span>
                        ) : (
                          <>Shipping: {store.shipping}</>
                        )}
                      </p>
                    )}
                  </div>

                  {/* Details and Offers */}
                  {store.details_and_offers && store.details_and_offers.length > 0 && (
                    <div className="mb-4 space-y-1">
                      {store.details_and_offers.slice(0, 2).map((detail, i) => (
                        <p key={i} className="text-sm text-muted-foreground flex items-center">
                          <span className="text-green-600 dark:text-green-400 mr-2">✓</span>
                          {detail}
                        </p>
                      ))}
                      {store.details_and_offers.length > 2 && (
                        <p className="text-xs text-muted-foreground italic">
                          +{store.details_and_offers.length - 2} more benefits
                        </p>
                      )}
                    </div>
                  )}

                  {/* Buy Button */}
                  <Button
                    asChild
                    size="sm"
                    className="w-full rounded-lg bg-primary hover:bg-primary/90"
                  >
                    <a
                      href={store.link}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      View on {store.name}
                      <ExternalLink className="h-4 w-4 ml-2" />
                    </a>
                  </Button>
                </motion.div>
              ))}
              </div>

              {/* Footer */}
              <div className="border-t border-border px-6 py-3 bg-muted/50 flex-shrink-0">
                <p className="text-xs text-muted-foreground text-center">
                  Showing {sortedStores.length} available offers. Prices may vary and include shipping.
                </p>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
