import { useNavigate, useSearchParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { getCachedZipcode, cacheZipcode, getUserZipcode } from '@/utils/geolocation';
import { getCountryForSearch, storeCountry, getStoredCountry } from '@/utils/locationUtils';

export const useSearchUrl = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [detectedZipcode, setDetectedZipcode] = useState<string | null>(null);
  const [detectedCountry, setDetectedCountry] = useState<string | null>(null);
  const [detectedCity, setDetectedCity] = useState<string | null>(null);
  const [isDetectingLocation, setIsDetectingLocation] = useState(false);
  
  // Auto-detect user location on mount
  useEffect(() => {
    const initializeLocation = async () => {
      // First check localStorage for country
      const storedCountry = getStoredCountry();
      
      if (storedCountry) {
        setDetectedCountry(storedCountry);
        
        // Also check for cached zipcode and city
        const cached = getCachedZipcode();
        const cachedCity = localStorage.getItem('userCity');
        
        if (cached) setDetectedZipcode(cached);
        if (cachedCity) setDetectedCity(cachedCity);
        return;
      }

      // If no stored country and not from URL params, attempt to detect
      const urlCountry = searchParams.get('country');
      
      if (!urlCountry) {
        setIsDetectingLocation(true);
        try {
          // Try to get location from IP (includes country)
          const result = await getUserZipcode();
          if (result) {
            // Store all detected information
            cacheZipcode(result.zipcode);
            storeCountry(result.country);  // Store the full country name
            setDetectedCountry(result.country);
            
            if (result.city) {
              localStorage.setItem('userCity', result.city);
              setDetectedCity(result.city);
            }
            setDetectedZipcode(result.zipcode);
          } else {
            // Fallback to location utilities if getUserZipcode fails
            const country = await getCountryForSearch();
            setDetectedCountry(country);
            setDetectedZipcode('60607');
          }
        } catch (error) {
          console.error('Error detecting location:', error);
          setDetectedCountry('United States');
          setDetectedZipcode('60607');
        } finally {
          setIsDetectingLocation(false);
        }
      }
    };

    initializeLocation();
  }, [searchParams]);
  
  // Get query and geo parameters from URL search params
  // Use detected location with fallbacks
  const query = searchParams.get('q') || '';
  const country = searchParams.get('country') || detectedCountry || getStoredCountry() || 'United States';
  const city = searchParams.get('city') || detectedCity || localStorage.getItem('userCity') || '';
  const language = searchParams.get('language') || 'en';
  const zipcode = searchParams.get('zipcode') || detectedZipcode || getCachedZipcode() || '60607';
  
  const updateSearchUrl = (
    searchQuery: string, 
    newZipcode?: string,
    newCountry?: string,
    newCity?: string,
    newLanguage?: string
  ) => {
    const finalZipcode = newZipcode || zipcode;
    const finalCountry = newCountry || country;
    const finalCity = newCity || city;
    const finalLanguage = newLanguage || language;
    
    if (searchQuery.trim()) {
      const trimmedQuery = searchQuery.trim();
      // Persist values to localStorage
      localStorage.setItem('userZipcode', finalZipcode);
      storeCountry(finalCountry);  // Use utility function
      localStorage.setItem('userCity', finalCity);
      localStorage.setItem('userLanguage', finalLanguage);
      
      const params = new URLSearchParams();
      params.set('q', trimmedQuery);
      params.set('country', finalCountry);
      params.set('zipcode', finalZipcode);
      // Only include city if it's explicitly provided in this search
      if (newCity) params.set('city', newCity);
      if (finalLanguage !== 'en') params.set('language', finalLanguage);
      
      navigate(`/search?${params.toString()}`);
    } else {
      setSearchParams({});
    }
  };
  
  const clearSearch = () => {
    setSearchParams({});
  };
  
  const setQuery = (newQuery: string | null, newZipcode?: string, newCountry?: string, newCity?: string) => {
    if (newQuery) {
      updateSearchUrl(newQuery, newZipcode, newCountry, newCity);
    } else {
      clearSearch();
    }
  };

  const updateZipcode = (newZipcode: string) => {
    localStorage.setItem('userZipcode', newZipcode);
    if (query) {
      updateSearchUrl(query, newZipcode, country, city, language);
    }
  };

  const updateCountry = (newCountry: string) => {
    storeCountry(newCountry);  // Use utility function
    // Clear city when country changes to avoid mismatch
    localStorage.removeItem('userCity');
    setDetectedCity(null);
    if (query) {
      updateSearchUrl(query, zipcode, newCountry, '', language);
    }
  };

  const updateCity = (newCity: string) => {
    localStorage.setItem('userCity', newCity);
    if (query) {
      updateSearchUrl(query, zipcode, country, newCity, language);
    }
  };

  const updateLanguage = (newLanguage: string) => {
    localStorage.setItem('userLanguage', newLanguage);
    if (query) {
      updateSearchUrl(query, zipcode, country, city, newLanguage);
    }
  };
  
  return {
    query,
    zipcode,
    country,
    city,
    language,
    updateSearchUrl,
    clearSearch,
    setQuery,
    updateZipcode,
    updateCountry,
    updateCity,
    updateLanguage,
    isDetectingLocation
  };
};