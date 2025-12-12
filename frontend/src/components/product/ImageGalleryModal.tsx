import { useState } from "react";
import { X } from "lucide-react";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@/components/ui/carousel";

interface ImageGalleryModalProps {
  title: string;
  images: string[];
  isOpen: boolean;
  onClose: () => void;
}

export const ImageGalleryModal = ({ title, images, isOpen, onClose }: ImageGalleryModalProps) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-5xl w-full h-[90vh] p-0 border-0 bg-black/95 flex flex-col">
        <DialogTitle className="sr-only">Product Image Gallery - {title}</DialogTitle>
        
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-50 bg-white/10 hover:bg-white/20 text-white rounded-full p-2 transition-colors"
          aria-label="Close"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Image counter */}
        <div className="absolute top-4 left-4 z-50 bg-white/10 backdrop-blur-sm text-white px-3 py-1 rounded-full text-sm">
          {currentIndex + 1} / {images.length}
        </div>

        {/* Main carousel - flex-1 to take remaining space */}
        <div className="flex-1 flex items-center justify-center w-full overflow-hidden">
          <Carousel className="w-full h-full flex items-center justify-center" orientation="horizontal">
            <CarouselContent className="h-full m-0 flex items-center">
              {images.map((url, index) => (
                <CarouselItem key={index} className="h-full w-full flex items-center justify-center pl-0 basis-full">
                  <div className="w-full h-full flex items-center justify-center bg-black p-8">
                    {url ? (
                      <img
                        src={url}
                        alt={`${title} - Image ${index + 1}`}
                        className="max-w-full max-h-full object-contain"
                        onLoad={() => setCurrentIndex(index)}
                        onError={(e) => {
                          const target = e.currentTarget;
                          target.style.display = 'none';
                          const placeholder = target.nextElementSibling as HTMLElement;
                          if (placeholder) placeholder.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    <div
                      className="w-full h-full flex items-center justify-center text-muted-foreground"
                      style={{ display: 'none' }}
                    >
                      <span className="text-lg">Image not available</span>
                    </div>
                  </div>
                </CarouselItem>
              ))}
            </CarouselContent>
            <CarouselPrevious className="left-6 bg-white/10 hover:bg-white/20 text-white border-0" />
            <CarouselNext className="right-6 bg-white/10 hover:bg-white/20 text-white border-0" />
          </Carousel>
        </div>

        {/* Thumbnail strip at bottom */}
        {images.length > 1 && (
          <div className="bg-gradient-to-t from-black/80 to-transparent p-4 border-t border-white/10">
            <div className="flex gap-2 overflow-x-auto pb-2 justify-center">
              {images.map((url, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentIndex(index)}
                  className={`flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden border-2 transition-all ${
                    index === currentIndex
                      ? 'border-white/80 ring-2 ring-white/50'
                      : 'border-white/30 hover:border-white/50 opacity-60 hover:opacity-100'
                  }`}
                  aria-label={`View image ${index + 1}`}
                >
                  {url && (
                    <img
                      src={url}
                      alt={`Thumbnail ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  )}
                </button>
              ))}
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};
