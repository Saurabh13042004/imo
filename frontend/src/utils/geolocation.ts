/**
 * Geolocation utilities for auto-detecting user location and postal code
 * 
 * Supports worldwide locations with automatic postal code detection.
 * 
 * Strategy (in order of preference):
 * 1. ipinfo.io API (CORS-friendly, fast) - Works globally
 * 2. Backend proxy endpoint (if frontend APIs blocked) - Works globally
 * 3. Browser Geolocation API (accurate but requires permission) - Works globally
 * 4. localStorage cache (instant for returning users)
 * 5. Default fallback ("60607")
 */

interface GeolocationResult {
  zipcode: string;
  city: string;
  state: string;
  latitude?: number;
  longitude?: number;
}

/**
 * Get user's zipcode from IP geolocation
 * Falls back to browser geolocation if available
 * @returns Promise<GeolocationResult | null>
 */
export async function getUserZipcode(): Promise<GeolocationResult | null> {
  try {
    // First, try IP-based geolocation (fast, no user permission needed)
    const ipGeoResult = await getLocationFromIP();
    if (ipGeoResult) {
      return ipGeoResult;
    }

    // Fallback: Try browser geolocation API (more accurate but requires permission)
    const browserGeoResult = await getLocationFromBrowser();
    if (browserGeoResult) {
      return browserGeoResult;
    }

    return null;
  } catch (error) {
    console.error("Error detecting user location:", error);
    return null;
  }
}

/**
 * Get location from IP-based geolocation service
 * Uses ipinfo.io (CORS-friendly, free tier with limited requests)
 * Falls back to backend proxy if frontend request fails
 */
async function getLocationFromIP(): Promise<GeolocationResult | null> {
  try {
    // Try ipinfo.io first (CORS-friendly)
    const result = await getLocationFromIPInfo();
    if (result) {
      return result;
    }

    // Fallback: Use backend proxy endpoint
    return await getLocationFromBackendProxy();
  } catch (error) {
    console.warn("Error fetching location from IP:", error);
    return null;
  }
}

/**
 * Get location from ipinfo.io (CORS-enabled)
 * Validates US-only zipcodes (5 digits)
 */
async function getLocationFromIPInfo(): Promise<GeolocationResult | null> {
  try {
    const response = await fetch("https://ipinfo.io/json", {
      method: "GET",
    });

    if (!response.ok) {
      console.warn("ipinfo.io request failed:", response.status);
      return null;
    }

    const data = await response.json();

    // Get postal code - format varies by country
    // US: 5 digits (12345), Canada: postal codes (K1A 0B1), India: 6 digits (500001), etc.
    const postalCode = data.postal;
    if (!postalCode) {
      console.warn("No postal code available from ipinfo.io");
      return null;
    }

    // Convert postal code to a simple numeric format for internal use
    // For US: keep as-is (5 digits)
    // For others: use first 5 characters or create identifier
    let zipcode = postalCode;
    if (!/^\d{5}/.test(zipcode)) {
      // For non-US postal codes, convert to 5-char identifier
      // Take first 5 chars and pad with zeros as needed
      zipcode = zipcode.replace(/[^a-zA-Z0-9]/g, '').substring(0, 5).padEnd(5, '0');
    } else {
      zipcode = zipcode.substring(0, 5);
    }

    return {
      zipcode: zipcode,
      city: data.city || "",
      state: data.region || "",
      latitude: data.loc ? parseFloat(data.loc.split(",")[0]) : undefined,
      longitude: data.loc ? parseFloat(data.loc.split(",")[1]) : undefined,
    };
  } catch (error) {
    console.warn("Error fetching location from ipinfo.io:", error);
    return null;
  }
}

/**
 * Get location from backend proxy endpoint
 * Use this if direct IP geolocation services fail due to CORS/rate limiting
 */
async function getLocationFromBackendProxy(): Promise<GeolocationResult | null> {
  try {
    const response = await fetch("/api/v1/utils/geolocation", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      console.warn("Backend geolocation proxy failed:", response.status);
      return null;
    }

    const data = await response.json();

    if (!data.zipcode || !/^\d{5}(-\d{4})?$/.test(data.zipcode)) {
      console.warn("Invalid zipcode from backend:", data.zipcode);
      return null;
    }

    return {
      zipcode: data.zipcode.substring(0, 5),
      city: data.city || "",
      state: data.state || "",
      latitude: data.latitude,
      longitude: data.longitude,
    };
  } catch (error) {
    console.warn("Error fetching location from backend proxy:", error);
    return null;
  }
}

/**
 * Get location from browser Geolocation API
 * More accurate but requires user permission
 */
async function getLocationFromBrowser(): Promise<GeolocationResult | null> {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      console.warn("Browser Geolocation API not available");
      resolve(null);
      return;
    }

    // Set a timeout to avoid hanging if user denies permission
    const timeout = setTimeout(() => {
      console.warn("Browser geolocation request timed out");
      resolve(null);
    }, 5000);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        clearTimeout(timeout);
        try {
          const { latitude, longitude } = position.coords;

          // Convert coordinates to zipcode using reverse geocoding
          const zipcode = await coordinatesToZipcode(latitude, longitude);

          if (zipcode) {
            resolve({
              zipcode,
              city: "",
              state: "",
              latitude,
              longitude,
            });
          } else {
            resolve(null);
          }
        } catch (error) {
          console.error("Error converting coordinates to zipcode:", error);
          resolve(null);
        }
      },
      (error) => {
        clearTimeout(timeout);
        console.warn("Browser geolocation error:", error.message);
        resolve(null);
      },
      {
        timeout: 5000,
        enableHighAccuracy: false, // Don't need high accuracy for zipcode
      }
    );
  });
}

/**
 * Convert latitude/longitude to zipcode using reverse geocoding
 * Uses OpenStreetMap's Nominatim API (free, no API key needed)
 */
async function coordinatesToZipcode(
  latitude: number,
  longitude: number
): Promise<string | null> {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=10`,
      {
        headers: {
          // Nominatim requires a User-Agent header
          "User-Agent": "IMO-App-Zipcode-Detection",
        },
      }
    );

    if (!response.ok) {
      console.warn("Reverse geocoding request failed:", response.status);
      return null;
    }

    const data = await response.json();

    // Extract zipcode from address
    const zipcode = data.address?.postcode;

    if (!zipcode) {
      console.warn("No zipcode found in reverse geocoding response");
      return null;
    }

    // Handle extended zipcode format (e.g., "60607-1234") - extract just 5 digits
    return zipcode.substring(0, 5);
  } catch (error) {
    console.error("Error in reverse geocoding:", error);
    return null;
  }
}

/**
 * Check if we already have a cached zipcode in localStorage
 * @returns Cached zipcode or null
 */
export function getCachedZipcode(): string | null {
  try {
    const cached = localStorage.getItem("userZipcode");
    const cacheTime = localStorage.getItem("userZipcodeTime");

    if (!cached || !cacheTime) {
      return null;
    }

    // Cache for 24 hours (86400000 ms)
    const cacheAge = Date.now() - parseInt(cacheTime);
    if (cacheAge > 24 * 60 * 60 * 1000) {
      console.log("Cached zipcode expired, fetching fresh location");
      localStorage.removeItem("userZipcode");
      localStorage.removeItem("userZipcodeTime");
      return null;
    }

    return cached;
  } catch (error) {
    console.error("Error reading cached zipcode:", error);
    return null;
  }
}

/**
 * Cache zipcode in localStorage with timestamp
 */
export function cacheZipcode(zipcode: string): void {
  try {
    localStorage.setItem("userZipcode", zipcode);
    localStorage.setItem("userZipcodeTime", Date.now().toString());
  } catch (error) {
    console.error("Error caching zipcode:", error);
  }
}

/**
 * Format location string for display
 */
export function formatLocationDisplay(result: GeolocationResult): string {
  if (result.city && result.state) {
    return `${result.city}, ${result.state}`;
  }
  return result.zipcode;
}
