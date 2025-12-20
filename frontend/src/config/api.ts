/**
 * API Configuration
 * Reads from VITE_API_URL environment variable
 * Defaults to localhost:8000 for development
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Helper to construct full API URLs
 * @param path - The API path (e.g., '/api/v1/product/123')
 * @returns Full URL string
 */
export const getApiUrl = (path: string): string => {
  // If path already includes protocol, return as-is
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  
  // Remove leading slash if present and construct full URL
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
};

// For development, proxy via relative paths
// In production, use full URLs if needed
export const useRelativePaths = import.meta.env.MODE === 'development';
