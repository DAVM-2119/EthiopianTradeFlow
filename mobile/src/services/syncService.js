import { apiClient } from '../api/axios.js';
import { API_ENDPOINTS } from '../api/endpoints.js';
import { offlineQueue } from '../storage/offlineQueue.js';

export const syncService = {
  async processOfflineQueue() {
    const queue = await offlineQueue.getQueue();
    if (queue.length === 0) {
      return { syncedCount: 0, failedCount: 0 };
    }

    try {
      const res = await apiClient.post(API_ENDPOINTS.SYNC_BATCH_SUBMIT, {
        events: queue.map((ev) => ({
          client_event_id: ev.client_event_id,
          device_id: ev.device_id || 'tradeflow-mobile-driver-01',
          event_type: ev.event_type,
          entity_type: ev.entity_type || 'shipment',
          entity_id: ev.entity_id,
          payload: ev.payload || {},
          client_created_at: ev.client_created_at,
        })),
      });

      const results = res.data?.data?.results || res.data?.results || [];
      const syncedClientIds = results.map((r) => r.client_event_id);

      if (syncedClientIds.length > 0) {
        await offlineQueue.removeEvents(syncedClientIds);
      }

      return {
        syncedCount: syncedClientIds.length,
        failedCount: queue.length - syncedClientIds.length,
      };
    } catch (err) {
      console.warn('Batch sync error:', err.message);
      return { syncedCount: 0, failedCount: queue.length, error: err.message };
    }
  },
};
