import { useState, useEffect } from 'react';
import { trackingService } from '../services/trackingService.js';

export function useDriverLocation(shipmentId, { enabled = true, intervalMs = 10000 } = {}) {
  const [currentLocation, setCurrentLocation] = useState({
    latitude: 11.589, // Djibouti Port initial default
    longitude: 43.145,
    speed: 62.5,
    heading: 215,
  });

  const [broadcasting, setBroadcasting] = useState(false);

  useEffect(() => {
    if (!enabled || !shipmentId) return;

    setBroadcasting(true);

    const interval = setInterval(async () => {
      // Simulate slight realistic corridor GPS progress along N1 Highway (Djibouti -> Modjo)
      setCurrentLocation((prev) => {
        const nextLat = prev.latitude + 0.0012;
        const nextLng = prev.longitude - 0.0018;
        const nextSpeed = Math.floor(55 + Math.random() * 20);

        trackingService
          .sendLocationEvent(shipmentId, {
            latitude: nextLat,
            longitude: nextLng,
            speed: nextSpeed,
            heading: 215,
          })
          .catch(() => {});

        return {
          latitude: nextLat,
          longitude: nextLng,
          speed: nextSpeed,
          heading: 215,
        };
      });
    }, intervalMs);

    return () => {
      clearInterval(interval);
      setBroadcasting(false);
    };
  }, [shipmentId, enabled, intervalMs]);

  return {
    currentLocation,
    broadcasting,
  };
}
