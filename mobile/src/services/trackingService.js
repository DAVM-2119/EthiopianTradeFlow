import { apiClient } from '../api/axios.js';
import { API_ENDPOINTS } from '../api/endpoints.js';
import { offlineQueue } from '../storage/offlineQueue.js';

export const trackingService = {
  async sendLocationEvent(shipmentId, { latitude, longitude, speed = 0, heading = 0 }) {
    const payload = {
      shipment_id: shipmentId,
      latitude,
      longitude,
      speed,
      heading,
      timestamp: new Date().toISOString(),
    };

    try {
      const res = await apiClient.post(API_ENDPOINTS.TRACKING_EVENTS, payload);
      return res.data?.data || res.data;
    } catch (err) {
      if (!err.response) {
        await offlineQueue.enqueueEvent({
          eventType: 'TRACKING_EVENT',
          entityType: 'shipment',
          entityId: shipmentId,
          payload,
        });
        return { offline: true, message: 'GPS location queued offline.' };
      }
      throw err;
    }
  },

  async reportIncident(shipmentId, { incidentType, description, latitude, longitude }) {
    const payload = {
      shipment_id: shipmentId,
      incident_type: incidentType, // ACCIDENT, CHECKPOINT_DELAY, FUEL_UNAVAILABLE, ROAD_PROBLEM, SECURITY_INCIDENT
      description,
      latitude,
      longitude,
    };

    try {
      const res = await apiClient.post(API_ENDPOINTS.INCIDENTS, payload);
      return res.data?.data || res.data;
    } catch (err) {
      if (!err.response) {
        await offlineQueue.enqueueEvent({
          eventType: 'INCIDENT_REPORT',
          entityType: 'shipment',
          entityId: shipmentId,
          payload,
        });
        return { offline: true, message: 'Incident report queued offline.' };
      }
      throw err;
    }
  },

  async getSecurityAlerts() {
    const res = await apiClient.get(API_ENDPOINTS.SECURITY_ALERTS);
    return res.data?.data || res.data;
  },
};
