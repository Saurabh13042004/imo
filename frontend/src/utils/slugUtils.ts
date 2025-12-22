/**
 * Generate a URL-friendly slug from a product title and ID
 * @param title - Product title
 * @param id - Product ID
 * @returns URL-friendly slug
 */
export const generateSlug = (title: string, id: string): string => {
  // Convert title to lowercase and replace spaces with hyphens
  const titleSlug = title
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '') // Remove special characters
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/-+/g, '-') // Replace multiple hyphens with single hyphen
    .slice(0, 50); // Limit length for URL readability

  // Return slug in format: title-id
  return `${titleSlug}-${id}`;
};

/**
 * Extract product ID from slug
 * @param slug - Product slug in format: title-id
 * @returns Product ID
 */
export const extractIdFromSlug = (slug: string): string => {
  // The ID is after the last hyphen if it looks like a UUID
  const parts = slug.split('-');
  
  // Check if last part looks like a UUID (36 characters with hyphens = 8-4-4-4-12)
  const lastPart = parts[parts.length - 1];
  
  // Try to find a UUID pattern in the slug
  const uuidRegex = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/;
  const match = slug.match(uuidRegex);
  
  if (match) {
    return match[0];
  }
  
  // Fallback: assume ID is everything after the last 36 characters
  if (slug.length > 36) {
    return slug.slice(-36);
  }
  
  return lastPart;
};
