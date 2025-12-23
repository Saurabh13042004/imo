import React, { useState, useEffect } from 'react';
import { AlertCircle, MapPin, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface LocationPermissionBannerProps {
  detectedCountry?: string;
  onDismiss: () => void;
}

/**
 * Component to request location permission and show detected location
 * Appears at the top of search page when location detection is in progress
 */
export const LocationPermissionBanner: React.FC<LocationPermissionBannerProps> = ({
  detectedCountry,
  onDismiss,
}) => {
  const [showBanner, setShowBanner] = useState(true);
  const [locationDetected, setLocationDetected] = useState(false);

  useEffect(() => {
    // Check if location was already detected
    if (detectedCountry && detectedCountry !== 'India') {
      setLocationDetected(true);
      // Auto-hide banner after 4 seconds if location was detected
      const timer = setTimeout(() => {
        setShowBanner(false);
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [detectedCountry]);

  const handleRequestLocation = async () => {
    try {
      if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser');
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          console.log('Location permission granted:', position.coords);
          setLocationDetected(true);
          // Auto-hide after getting permission
          setTimeout(() => {
            setShowBanner(false);
          }, 2000);
        },
        (error) => {
          console.warn('Location permission denied:', error);
          alert('Location permission was denied. We\'ll use IP-based detection instead.');
        }
      );
    } catch (error) {
      console.error('Error requesting location:', error);
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
            className="bg-blue-600 hover:bg-blue-700 text-white h-8 px-3 text-sm"
          >
            <MapPin className="w-3.5 h-3.5 mr-1.5" />
            Enable Location
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
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
