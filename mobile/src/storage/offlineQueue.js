import { storage } from './asyncStorage.js';

const QUEUE_KEY = '@tradeflow_offline_queue';

// Simple fallback UUID v4 generator for React Native environments
export function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Offline Queue Engine capturing driver events performed offline.
 * Guarantees backend idempotency using unique client_event_id.
 */
export const offlineQueue = {
  async getQueue() {
    const queue = await storage.getItem(QUEUE_KEY);
    return Array.isArray(queue) ? queue : [];
  },

  async enqueueEvent({ eventType, entityType = 'shipment', entityId, payload = {} }) {
    const queue = await this.getQueue();

    const clientEventId = generateUUID();
    const now = new Date().toISOString();

    const newEvent = {
      client_event_id: clientEventId,
      device_id: 'tradeflow-mobile-driver-01',
      event_type: eventType, // WAYPOINT_CHECKIN, INCIDENT_REPORT, TRACKING_EVENT
      entity_type: entityType,
      entity_id: entityId,
      payload: payload,
      client_created_at: now,
      status: 'PENDING',
      attempt_count: 0,
    };

    queue.push(newEvent);
    await storage.setItem(QUEUE_KEY, queue);
    return newEvent;
  },

  async removeEvents(clientEventIds = []) {
    const queue = await this.getQueue();
    const idSet = new Set(clientEventIds);
    const updated = queue.filter((item) => !idSet.has(item.client_event_id));
    await storage.setItem(QUEUE_KEY, updated);
  },

  async clearQueue() {
    await storage.removeItem(QUEUE_KEY);
  },

  async count() {
    const queue = await this.getQueue();
    return queue.length;
  },
};
