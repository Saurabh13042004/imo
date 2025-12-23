import React, { useState, useEffect } from 'react';
import { AlertCircle, MapPin, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { detectUserCountry, storeCountry, setLocationPermission, getStoredCountry } from '@/utils/locationUtils';

interface LocationPermissionBannerProps {
  detectedCountry?: string;
  onDismiss: () => void;
}

const LOCATION_BANNER_DISMISSED_KEY = 'location-banner-dismissed';
const LOCATION_PERMISSION_GRANTED_KEY = 'location-permission-granted';

/**
 * Component to request location permission and show detected location
 * Appears at the top of search page when location detection is in progress
 * Only shows once per user (stored in localStorage)
 */
export const LocationPermissionBanner: React.FC<LocationPermissionBannerProps> = ({
  detectedCountry,
  onDismiss,
}) => {
  const [showBanner, setShowBanner] = useState(() => {
    // Check if country is already stored in localStorage
    const storedCountry = getStoredCountry();
    if (storedCountry) {
      return false; // Don't show banner if country is already stored
    }
    
    // Check localStorage on mount - don't show if already dismissed
    const dismissed = localStorage.getItem(LOCATION_BANNER_DISMISSED_KEY);
    const permissionGranted = localStorage.getItem(LOCATION_PERMISSION_GRANTED_KEY);
    return !dismissed && !permissionGranted;
  });
  const [locationDetected, setLocationDetected] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);

  useEffect(() => {
    // Check if location was already detected
    if (detectedCountry && detectedCountry !== 'United States') {
      setLocationDetected(true);
      // Store that location was detected
      localStorage.setItem(LOCATION_PERMISSION_GRANTED_KEY, 'true');
      // Auto-hide banner after 4 seconds if location was detected
      const timer = setTimeout(() => {
        setShowBanner(false);
        onDismiss();
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [detectedCountry, onDismiss]);

  const handleRequestLocation = async () => {
    setIsDetecting(true);
    try {
      if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser');
        setIsDetecting(false);
        return;
      }

      // Use the utility function to detect country
      const country = await detectUserCountry();
      
      console.log('Detected country:', country);
      setLocationDetected(true);
      
      // Auto-hide after getting location
      setTimeout(() => {
        setShowBanner(false);
        onDismiss();
        // Reload to apply new country
        window.location.reload();
      }, 2000);
    } catch (error) {
      console.error('Error requesting location:', error);
      // Store dismissal even if error
      localStorage.setItem(LOCATION_BANNER_DISMISSED_KEY, 'true');
      setShowBanner(false);
      onDismiss();
    } finally {
      setIsDetecting(false);
    }
  };

  if (!showBanner) return null;

  // If location was detected successfully
  if (locationDetected) {
    return (
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-4 mb-6 flex items-start gap-3 shadow-sm">
        <div className="flex-shrink-0 pt-0.5">
          <MapPin className="w-5 h-5 text-green-600" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-green-900">
            ✓ Location detected: <span className="font-semibold">{detectedCountry || 'Detected'}</span>
          </p>
          <p className="text-sm text-green-700 mt-1">
            Showing search results for your region
          </p>
        </div>
        <button
          onClick={() => setShowBanner(false)}
          className="flex-shrink-0 text-green-600 hover:text-green-700"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    );
  }

  // If requesting location permission
  return (
    <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-lg p-4 mb-6 flex items-start gap-3 shadow-sm">
      <div className="flex-shrink-0 pt-0.5">
        <AlertCircle className="w-5 h-5 text-blue-600" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-blue-900">
          📍 Help us show you accurate results
        </p>
        <p className="text-sm text-blue-700 mt-1">
          Enable location access to get personalized search results for your region
        </p>
        <div className="flex gap-2 mt-3">
          <Button
            size="sm"
            onClick={handleRequestLocation}
            disabled={isDetecting}
            className="bg-blue-600 hover:bg-blue-700 text-white h-8 px-3 text-sm"
          >
            <MapPin className="w-3.5 h-3.5 mr-1.5" />
            {isDetecting ? 'Detecting...' : 'Enable Location'}
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              // Store dismissal in localStorage
              localStorage.setItem(LOCATION_BANNER_DISMISSED_KEY, 'true');
              setShowBanner(false);
              onDismiss();
            }}
            className="h-8 px-3 text-sm"
          >
            Skip
          </Button>
        </div>
      </div>
    </div>
  );
};
