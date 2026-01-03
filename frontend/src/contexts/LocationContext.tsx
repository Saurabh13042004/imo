import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { getCachedZipcode, cacheZipcode, getUserZipcode } from '@/utils/geolocation';
import { getCountryForSearch, storeCountry, getStoredCountry } from '@/utils/locationUtils';

interface LocationContextType {
  zipcode: string;
  country: string;
  city: string;
  isDetectingLocation: boolean;
}

const LocationContext = createContext<LocationContextType | null>(null);

export function LocationProvider({ children }: { children: ReactNode }) {
  const [zipcode, setZipcode] = useState<string>('60607');
  const [country, setCountry] = useState<string>('United States');
  const [city, setCity] = useState<string>('');
  const [isDetectingLocation, setIsDetectingLocation] = useState(false);
  const [hasInitialized, setHasInitialized] = useState(false);

  // Initialize location once on app mount
  useEffect(() => {
    if (hasInitialized) return;

    const initializeLocation = async () => {
      // First check localStorage for country
      const storedCountry = getStoredCountry();
      
      if (storedCountry) {
        setCountry(storedCountry);
        
        // Also check for cached zipcode and city
        const cached = getCachedZipcode();
        const cachedCity = localStorage.getItem('userCity');
        
        if (cached) setZipcode(cached);
        if (cachedCity) setCity(cachedCity);
        setHasInitialized(true);
        return;
      }

      // Attempt to detect location from IP
      setIsDetectingLocation(true);
      try {
        const result = await getUserZipcode();
        
        if (result) {
          // Store all detected information
          cacheZipcode(result.zipcode);
          storeCountry(result.country);
          setCountry(result.country);
          setZipcode(result.zipcode);
          
          if (result.city) {
            localStorage.setItem('userCity', result.city);
            setCity(result.city);
          }
        } else {
          // Fallback
          const country = await getCountryForSearch();
          setCountry(country);
          setZipcode('60607');
        }
      } catch (error) {
        console.error('Error detecting location:', error);
        setCountry('United States');
        setZipcode('60607');
      } finally {
        setIsDetectingLocation(false);
        setHasInitialized(true);
      }
    };

    initializeLocation();
  }, [hasInitialized]);

  return (
    <LocationContext.Provider value={{ zipcode, country, city, isDetectingLocation }}>
      {children}
    </LocationContext.Provider>
  );
}

export function useLocation() {
  const context = useContext(LocationContext);
  if (!context) {
    throw new Error('useLocation must be used within LocationProvider');
  }
  return context;
}
