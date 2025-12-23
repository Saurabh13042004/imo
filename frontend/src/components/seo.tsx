/**
 * SEO Meta Tags Component
 * Updates document head with SEO metadata
 */

interface MetaTagsProps {
  title?: string;
  description?: string;
  keywords?: string;
  image?: string;
  url?: string;
  type?: string;
  author?: string;
  canonicalUrl?: string;
}

export const MetaTags = ({
  title = 'Informed Market Opinions - AI-Powered Product Research',
  description = 'Discover the best products with AI-powered analysis of thousands of reviews, expert opinions, and video content.',
  keywords = 'product reviews, AI analysis, product recommendations, best products',
  image = 'https://informedmarketopinions.com/og-image.png',
  url = typeof window !== 'undefined' ? window.location.href : '',
  type = 'website',
  author = 'Informed Market Opinions',
  canonicalUrl,
}: MetaTagsProps) => {
  // Update document title
  if (typeof document !== 'undefined') {
    document.title = title;

    // Update meta tags
    const updateMeta = (name: string, content: string, isProperty = false) => {
      let element = document.querySelector(
        isProperty ? `meta[property="${name}"]` : `meta[name="${name}"]`
      ) as HTMLMetaElement;

      if (!element) {
        element = document.createElement('meta');
        if (isProperty) {
          element.setAttribute('property', name);
        } else {
          element.setAttribute('name', name);
        }
        document.head.appendChild(element);
      }

      element.content = content;
    };

    // Standard meta tags
    updateMeta('description', description);
    updateMeta('keywords', keywords);
    updateMeta('author', author);
    updateMeta('viewport', 'width=device-width, initial-scale=1.0');

    // Open Graph meta tags
    updateMeta('og:title', title, true);
    updateMeta('og:description', description, true);
    updateMeta('og:image', image, true);
    updateMeta('og:url', url, true);
    updateMeta('og:type', type, true);

    // Twitter Card meta tags
    updateMeta('twitter:card', 'summary_large_image');
    updateMeta('twitter:title', title);
    updateMeta('twitter:description', description);
    updateMeta('twitter:image', image);

    // Canonical URL
    if (canonicalUrl) {
      let canonical = document.querySelector(
        'link[rel="canonical"]'
      ) as HTMLLinkElement;

      if (!canonical) {
        canonical = document.createElement('link');
        canonical.rel = 'canonical';
        document.head.appendChild(canonical);
      }

      canonical.href = canonicalUrl;
    }
  }

  return null;
};
