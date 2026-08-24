import { apiClient } from '../api/axios.js';
import { API_ENDPOINTS } from '../api/endpoints.js';
import { offlineQueue } from '../storage/offlineQueue.js';

export const shipmentService = {
  async getAssignedShipments() {
    const res = await apiClient.get(API_ENDPOINTS.SHIPMENTS);
    return res.data?.data || res.data;
  },

  async getShipmentDetail(id) {
    const res = await apiClient.get(API_ENDPOINTS.SHIPMENT_DETAIL(id));
    return res.data?.data || res.data;
  },

  async transitionStatus(id, targetStatus) {
    try {
      const res = await apiClient.post(API_ENDPOINTS.SHIPMENT_TRANSITION(id), { status: targetStatus });
      return res.data?.data || res.data;
    } catch (err) {
      if (!err.response) {
        // Enqueue offline action
        await offlineQueue.enqueueEvent({
          eventType: 'WAYPOINT_CHECKIN',
          entityType: 'shipment',
          entityId: id,
          payload: { target_status: targetStatus },
        });
        return { offline: true, message: 'Status update queued offline.' };
      }
      throw err;
    }
  },

  async submitProofOfDelivery(id, proofData) {
    try {
      const res = await apiClient.post(API_ENDPOINTS.SHIPMENT_PROOF_OF_DELIVERY(id), proofData);
      return res.data?.data || res.data;
    } catch (err) {
      if (!err.response) {
        await offlineQueue.enqueueEvent({
          eventType: 'WAYPOINT_CHECKIN',
          entityType: 'shipment',
          entityId: id,
          payload: { proof_of_delivery: proofData },
        });
        return { offline: true, message: 'Proof of delivery queued offline.' };
      }
      throw err;
    }
  },
};
