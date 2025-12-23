/**
 * Utility functions for handling user location and country detection
 */

const COUNTRY_STORAGE_KEY = 'user-country';
const LOCATION_PERMISSION_KEY = 'location-permission-granted';

/**
 * Get country from localStorage
 */
export function getStoredCountry(): string | null {
  return localStorage.getItem(COUNTRY_STORAGE_KEY);
}

/**
 * Store country in localStorage
 */
export function storeCountry(country: string): void {
  localStorage.setItem(COUNTRY_STORAGE_KEY, country);
}

/**
 * Check if location permission was granted
 */
export function hasLocationPermission(): boolean {
  return localStorage.getItem(LOCATION_PERMISSION_KEY) === 'true';
}

/**
 * Store location permission status
 */
export function setLocationPermission(granted: boolean): void {
  localStorage.setItem(LOCATION_PERMISSION_KEY, granted ? 'true' : 'false');
}

/**
 * Reverse geocode coordinates to get country
 */
async function reverseGeocode(latitude: number, longitude: number): Promise<string | null> {
  try {
    // Using Nominatim (OpenStreetMap) - free and no API key required
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=3`,
      {
        headers: {
          'User-Agent': 'IMO-Search-App'
        }
      }
    );

    if (!response.ok) {
      throw new Error('Geocoding failed');
    }

    const data = await response.json();
    return data.address?.country || null;
  } catch (error) {
    console.error('Reverse geocoding error:', error);
    return null;
  }
}

/**
 * Get user's country from browser geolocation
 */
export async function detectUserCountry(): Promise<string> {
  return new Promise((resolve) => {
    // Check if geolocation is supported
    if (!navigator.geolocation) {
      console.warn('Geolocation not supported');
      resolve('United States'); // Default fallback
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        console.log('Detected coordinates:', { latitude, longitude });

        // Reverse geocode to get country
        const country = await reverseGeocode(latitude, longitude);
        
        if (country) {
          console.log('Detected country:', country);
          storeCountry(country);
          setLocationPermission(true);
          resolve(country);
        } else {
          console.warn('Could not determine country from coordinates');
          resolve('United States'); // Default fallback
        }
      },
      (error) => {
        console.error('Geolocation error:', error.message);
        setLocationPermission(false);
        resolve('United States'); // Default fallback on error
      },
      {
        timeout: 10000,
        maximumAge: 3600000, // Cache for 1 hour
        enableHighAccuracy: false
      }
    );
  });
}

/**
 * Get country for search - checks localStorage first, then detects
 */
export async function getCountryForSearch(): Promise<string> {
  // 1. Check localStorage first
  const storedCountry = getStoredCountry();
  if (storedCountry) {
    console.log('Using stored country:', storedCountry);
    return storedCountry;
  }

  // 2. Check if permission was previously granted
  if (hasLocationPermission()) {
    console.log('Permission granted, detecting country...');
    const country = await detectUserCountry();
    return country;
  }

  // 3. Return default (will trigger permission banner)
  console.log('No stored country, using default');
  return 'United States';
}

/**
 * Clear stored country (for testing/reset)
 */
export function clearStoredCountry(): void {
  localStorage.removeItem(COUNTRY_STORAGE_KEY);
}
