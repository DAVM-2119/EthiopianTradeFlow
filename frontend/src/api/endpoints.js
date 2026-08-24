export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login/',
  REGISTER: '/auth/register/',
  LOGOUT: '/auth/logout/',
  REFRESH_TOKEN: '/auth/token/refresh/',
  ME: '/auth/me/',
  PASSWORD_CHANGE: '/auth/password/change/',

  // Health & Dashboard
  HEALTH: '/health/',
  DASHBOARD_SUMMARY: '/dashboard/summary/',


  // Profiles
  PROFILE: '/profiles/me/',
  TRANSPORTER_DRIVERS: '/profiles/transporter/drivers/',

  // Fleet
  VEHICLES: '/vehicles/',

  // Verification
  VERIFICATION_ME: '/verification/me/',
  VERIFICATION_SUBMIT: '/verification/me/submit/',
  ADMIN_VERIFICATIONS: '/admin/verifications/',

  // Loads & Marketplace & Bids
  LOADS: '/loads/',
  MY_BIDS: '/my-bids/',
  LOAD_BIDS: (loadId) => `/loads/${loadId}/bids/`,
  BID_DETAIL: (bidId) => `/bids/${bidId}/`,
  BID_WITHDRAW: (bidId) => `/bids/${bidId}/withdraw/`,
  BID_ACCEPT: (bidId) => `/bids/${bidId}/accept/`,


  // Freight Matching
  MATCHES: '/matches/',

  // Shipments & Tracking
  SHIPMENTS: '/shipments/',
  SHIPMENT_DETAIL: (id) => `/shipments/${id}/`,
  SHIPMENT_ASSIGN: (id) => `/shipments/${id}/assign/`,
  SHIPMENT_TRANSITION: (id) => `/shipments/${id}/transition/`,
  SHIPMENT_CANCEL: (id) => `/shipments/${id}/cancel/`,
  SHIPMENT_EVENTS: (id) => `/shipments/${id}/events/`,
  SHIPMENT_PROOF_OF_DELIVERY: (id) => `/shipments/${id}/proof-of-delivery/`,
  SHIPMENT_COMPLETE: (id) => `/shipments/${id}/complete/`,
  SHIPMENT_TRACKING_HISTORY: (id) => `/shipments/${id}/tracking/`,
  SHIPMENT_TRACKING_LATEST: (id) => `/shipments/${id}/tracking/latest/`,
  TRACKING_EVENTS: '/tracking/events/',

  // Customs
  SHIPMENT_CUSTOMS_DOCUMENTS: (id) => `/shipments/${id}/customs/documents/`,
  CUSTOMS_DOCUMENT_DETAIL: (docId) => `/customs/documents/${docId}/`,
  SHIPMENT_CUSTOMS_VALIDATE: (id) => `/shipments/${id}/customs/validate/`,
  SHIPMENT_CUSTOMS_SUBMIT: (id) => `/shipments/${id}/customs/submit/`,
  SHIPMENT_CUSTOMS_STATUS: (id) => `/shipments/${id}/customs/status/`,

  // Analytics & Fuel
  SHIPMENT_FUEL: (id) => `/shipments/${id}/fuel/`,
  FUEL_TRENDS: '/analytics/fuel/trends/',
  FUEL_RECOMMENDATIONS: '/analytics/fuel/recommendations/',
  TRANSPORTER_PERFORMANCE: '/analytics/transporter/performance/',
  TRANSPORTER_PERFORMANCE_HISTORY: '/analytics/transporter/performance/history/',

  // Risk & Security
  RISK_ZONES: '/risk-zones/',
  INCIDENTS: '/incidents/',
  SECURITY_ALERTS: '/security-alerts/',

  // Payments, Payouts & Disputes
  PAYMENTS: '/payments/',
  PAYMENT_DETAIL: (id) => `/payments/${id}/`,
  PAYMENT_INITIATE: (id) => `/payments/${id}/initiate/`,
  PAYMENT_CONFIRM: (id) => `/payments/${id}/confirm/`,
  PAYOUTS: '/payments/payouts/',
  PAYOUT_DETAIL: (id) => `/payments/payouts/${id}/`,
  SETTLEMENTS: '/payments/settlements/',
  SETTLEMENT_DETAIL: (id) => `/payments/settlements/${id}/`,
  DISPUTES: '/payments/disputes/',
  DISPUTE_DETAIL: (id) => `/payments/disputes/${id}/`,
  DISPUTE_RESOLVE: (id) => `/payments/disputes/${id}/resolve/`,

  // Notifications
  NOTIFICATIONS: '/notifications/',
  NOTIFICATION_PREFERENCES: '/notifications/preferences/',
};

