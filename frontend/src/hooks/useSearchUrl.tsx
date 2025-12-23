import { useNavigate, useSearchParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { getCachedZipcode, cacheZipcode, getUserZipcode } from '@/utils/geolocation';

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
      // First check if we have a cached location from previous session
      const cached = getCachedZipcode();
      const cachedCountry = localStorage.getItem('userCountry');
      const cachedCity = localStorage.getItem('userCity');
      
      if (cached && cachedCountry) {
        setDetectedZipcode(cached);
        setDetectedCountry(cachedCountry);
        if (cachedCity) setDetectedCity(cachedCity);
        return;
      }

      // If no cache and not from URL params, attempt to detect location
      const urlZipcode = searchParams.get('zipcode');
      const urlCountry = searchParams.get('country');
      
      if (!urlZipcode || !urlCountry) {
        setIsDetectingLocation(true);
        try {
          const result = await getUserZipcode();
          if (result) {
            cacheZipcode(result.zipcode);
            localStorage.setItem('userCountry', result.country);
            if (result.city) localStorage.setItem('userCity', result.city);
            
            setDetectedZipcode(result.zipcode);
            setDetectedCountry(result.country);
            if (result.city) setDetectedCity(result.city);
          } else {
            // Fallback to defaults
            setDetectedZipcode('60607');
            setDetectedCountry('US');
          }
        } catch (error) {
          console.error('Error detecting location:', error);
          setDetectedZipcode('60607');
          setDetectedCountry('US');
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
  const country = searchParams.get('country') || detectedCountry || localStorage.getItem('userCountry') || 'US';
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
    updateLanguage,
    isDetectingLocation
  };
};