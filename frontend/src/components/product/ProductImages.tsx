import { useState } from "react";
import { Package, ShoppingBag, Maximize2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { deduplicateImagesByBaseUrl } from "@/lib/utils";
import { ImageGalleryModal } from "./ImageGalleryModal";

interface ProductImagesProps {
  title: string;
  imageUrl?: string;
  imageUrls?: string[];
}

export const ProductImages = ({ title, imageUrl, imageUrls }: ProductImagesProps) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Determine which images to use for the modal
  const getImagesToDisplay = () => {
    if (imageUrls && imageUrls.length > 0) {
      return deduplicateImagesByBaseUrl(imageUrls);
    }
    return imageUrl ? [imageUrl] : [];
  };

  const imagesToDisplay = getImagesToDisplay();

  if (imageUrl) {
    return (
      <>
        <div className="space-y-3">
          <div className="aspect-square rounded-2xl overflow-hidden bg-muted/50">
            <div className="w-full h-full relative">
              {imageUrl ? (
                <img
                  src={imageUrl}
                  alt={title}
                  className="w-full h-full object-contain"
                  onError={(e) => {
                    const target = e.currentTarget;
                    target.style.display = 'none';
                    const placeholder = target.nextElementSibling as HTMLElement;
                    if (placeholder) placeholder.style.display = 'flex';
                  }}
                />
              ) : null}
              <div className="w-full h-full bg-muted/50 rounded-lg flex items-center justify-center text-muted-foreground" style={{ display: imageUrl ? 'none' : 'flex' }}>
                <Package className="h-12 w-12" />
              </div>
            </div>
          </div>

          {/* View More Images Button */}
          {imagesToDisplay.length > 0 && (
            <Button
              onClick={() => setIsModalOpen(true)}
              variant="outline"
              className="w-full gap-2 h-10"
            >
              <Maximize2 className="h-4 w-4" />
              View More Images ({imagesToDisplay.length})
            </Button>
          )}
        </div>

        {/* Image Gallery Modal */}
        {imagesToDisplay.length > 0 && (
          <ImageGalleryModal
            title={title}
            images={imagesToDisplay}
            isOpen={isModalOpen}
            onClose={() => setIsModalOpen(false)}
          />
        )}
      </>
    );
  }

  return (
    <div className="aspect-square rounded-2xl bg-muted flex items-center justify-center">
      <ShoppingBag className="h-20 w-20 text-muted-foreground/50" />
    </div>
  );
};