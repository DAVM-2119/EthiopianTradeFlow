export const API_BASE_URL = 'http://localhost:8000/api/v1';

export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login/',
  LOGOUT: '/auth/logout/',
  REFRESH_TOKEN: '/auth/token/refresh/',
  ME: '/auth/me/',

  // Shipments
  SHIPMENTS: '/shipments/',
  SHIPMENT_DETAIL: (id) => `/shipments/${id}/`,
  SHIPMENT_TRANSITION: (id) => `/shipments/${id}/transition/`,
  SHIPMENT_EVENTS: (id) => `/shipments/${id}/events/`,
  SHIPMENT_PROOF_OF_DELIVERY: (id) => `/shipments/${id}/proof-of-delivery/`,
  SHIPMENT_COMPLETE: (id) => `/shipments/${id}/complete/`,

  // GPS Tracking & Telemetry
  TRACKING_EVENTS: '/tracking/events/',
  SHIPMENT_TRACKING: (id) => `/shipments/${id}/tracking/`,
  SHIPMENT_TRACKING_LATEST: (id) => `/shipments/${id}/tracking/latest/`,

  // Offline Synchronization Batch
  SYNC_SUBMIT: '/sync/events/',
  SYNC_BATCH_SUBMIT: '/sync/events/batch/',
  SYNC_STATUS: '/sync/status/',

  // Risk & Security Alerts
  INCIDENTS: '/risk/incidents/',
  SECURITY_ALERTS: '/risk/security-alerts/',

  // Driver Profile & Performance
  DRIVER_PERFORMANCE: '/analytics/transporter/performance/',
};
