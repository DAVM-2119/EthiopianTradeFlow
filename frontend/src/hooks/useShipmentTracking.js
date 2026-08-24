import { useState, useEffect, useRef } from 'react';
import apiClient from '../api/axios';
import { API_ENDPOINTS } from '../api/endpoints';

export const useShipmentTracking = (shipmentId) => {
  const [latestTracking, setLatestTracking] = useState(null);
  const [trackingHistory, setTrackingHistory] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const wsRef = useRef(null);

  useEffect(() => {
    if (!shipmentId) return;

    // Fetch initial latest tracking data via REST API
    const fetchTracking = async () => {
      try {
        setLoading(true);
        const [latestRes, historyRes] = await Promise.all([
          apiClient.get(API_ENDPOINTS.SHIPMENT_TRACKING_LATEST(shipmentId)).catch(() => null),
          apiClient.get(API_ENDPOINTS.SHIPMENT_TRACKING_HISTORY(shipmentId)).catch(() => null),
        ]);

        if (latestRes?.data) setLatestTracking(latestRes.data?.data || latestRes.data);
        if (historyRes?.data) {
          const hist = historyRes.data?.data || historyRes.data;
          setTrackingHistory(Array.isArray(hist) ? hist : hist?.results || []);
        }
      } catch (err) {
        console.error('REST tracking fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTracking();

    // Establish WebSocket Connection
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/tracking/${shipmentId}/`;

    try {
      const socket = new WebSocket(wsUrl);
      wsRef.current = socket;

      socket.onopen = () => {
        setIsConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          const data = message.data || message;
          if (data && data.latitude !== undefined) {
            setLatestTracking(data);
            setTrackingHistory((prev) => [data, ...prev.slice(0, 49)]);
          }
        } catch (e) {
          console.error('Error parsing WS tracking message:', e);
        }
      };

      socket.onclose = () => {
        setIsConnected(false);
      };

      socket.onerror = () => {
        setIsConnected(false);
      };
    } catch (e) {
      setIsConnected(false);
    }

    // Polling fallback if WebSocket is not active
    const interval = setInterval(() => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        fetchTracking();
      }
    }, 15000);

    return () => {
      clearInterval(interval);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [shipmentId]);

  return { latestTracking, trackingHistory, isConnected, loading };
};
