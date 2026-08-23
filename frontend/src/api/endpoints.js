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

  // Loads & Marketplace
  LOADS: '/loads/',
  MY_BIDS: '/my-bids/',

  // Freight Matching
  MATCHES: '/matches/',

  // Shipments
  SHIPMENTS: '/shipments/',

  // Tracking
  TRACKING_EVENTS: '/tracking/events/',

  // Sync
  SYNC_EVENTS: '/sync/events/',

  // Pricing
  PRICING: '/pricing/',

  // Routing
  ROUTES: '/routes/',

  // Customs
  CUSTOMS: '/customs/',

  // Fuel & Analytics
  ANALYTICS: '/analytics/',

  // Risk & Security
  RISK_ZONES: '/risk-zones/',
  INCIDENTS: '/incidents/',
  SECURITY_ALERTS: '/security-alerts/',

  // Payments & Financial Settlement
  PAYMENTS: '/payments/',
  PAYOUTS: '/payments/payouts/',
  SETTLEMENTS: '/payments/settlements/',
  DISPUTES: '/payments/disputes/',

  // Notifications
  NOTIFICATIONS: '/notifications/',
  NOTIFICATION_PREFERENCES: '/notifications/preferences/',
};
