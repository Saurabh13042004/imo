import { useNavigate, useSearchParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { getCachedZipcode, cacheZipcode, getUserZipcode } from '@/utils/geolocation';

export const useSearchUrl = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [detectedZipcode, setDetectedZipcode] = useState<string | null>(null);
  const [isDetectingLocation, setIsDetectingLocation] = useState(false);
  
  // Auto-detect user location on mount
  useEffect(() => {
    const initializeZipcode = async () => {
      // First check if we have a cached zipcode from previous session
      const cached = getCachedZipcode();
      if (cached) {
        setDetectedZipcode(cached);
        return;
      }

      // If no cache and not from URL params, attempt to detect location
      const urlZipcode = searchParams.get('zipcode');
      if (!urlZipcode) {
        setIsDetectingLocation(true);
        try {
          const result = await getUserZipcode();
          if (result) {
            cacheZipcode(result.zipcode);
            setDetectedZipcode(result.zipcode);
          } else {
            // Fallback to default if detection fails
            setDetectedZipcode('60607');
          }
        } catch (error) {
          console.error('Error detecting location:', error);
          setDetectedZipcode('60607');
        } finally {
          setIsDetectingLocation(false);
        }
      }
    };

    initializeZipcode();
  }, [searchParams]);
  
  // Get query and geo parameters from URL search params
  const query = searchParams.get('q') || '';
  const country = searchParams.get('country') || 'India';  // DEFAULT: India
  const city = searchParams.get('city') || '';
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
      localStorage.setItem('userCountry', finalCountry);
      localStorage.setItem('userCity', finalCity);
      localStorage.setItem('userLanguage', finalLanguage);
      
      const params = new URLSearchParams();
      params.set('q', trimmedQuery);
      params.set('country', finalCountry);
      params.set('zipcode', finalZipcode);
      if (finalCity) params.set('city', finalCity);
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
    localStorage.setItem('userCountry', newCountry);
    if (query) {
      updateSearchUrl(query, zipcode, newCountry, city, language);
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
    updateLanguage
  };
};