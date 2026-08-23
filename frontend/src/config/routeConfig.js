export const ROUTE_CONFIG = {
  '/dashboard': {
    title: 'Dashboard Overview',
    subtitle: 'Djibouti Port ➔ Modjo Dry Port Freight Corridor Status',
    breadcrumbs: [{ name: 'TradeFlow', path: '/dashboard' }, { name: 'Dashboard' }],
  },
  '/loads': {
    title: 'Marketplace Loads',
    subtitle: 'Manage, search, and post freight loads across Ethiopia',
    breadcrumbs: [{ name: 'TradeFlow', path: '/dashboard' }, { name: 'Marketplace', path: '/loads' }],
  },
  '/bids': {
    title: 'Transporter Bids',
    subtitle: 'Submitted freight bids and active load proposals',
    breadcrumbs: [{ name: 'TradeFlow', path: '/dashboard' }, { name: 'Bids' }],
  },
  '/shipments': {
    title: 'Shipment Operations',
    subtitle: 'Active freight movement, vehicle assignment, and milestone updates',
    breadcrumbs: [{ name: 'TradeFlow', path: '/dashboard' }, { name: 'Shipments' }],
  },
  '/tracking': {
    title: 'Live Spatial Tracking',
    subtitle: 'Real-time GPS vehicle positions & dynamic corridor ETA calculation',
    breadcrumbs: [{ name: 'TradeFlow', path: '/dashboard' }, { name: 'Tracking' }],
  },
  '/customs': {
    title: 'Digital Customs Documentation',
    subtitle: 'Ethiopian Customs Commission document submission & clearance status',
    breadcrumbs: [{ name: 'TradeFlow', path: '/dashboard' }, { name: 'Customs' }],
  },
  '/payments': {
    title: 'Payments & Settlement Engine',
    subtitle: 'Commission audit, transporter payouts, and reconciliation settlements',
    breadcrumbs: [{ name: 'TradeFlow', path: '/dashboard' }, { name: 'Payments' }],
  },
  '/risk': {
    title: 'Risk Zones & Security Alerts',
    subtitle: 'Geographic conflict monitoring, crowd incidents, and route safety',
    breadcrumbs: [{ name: 'TradeFlow', path: '/dashboard' }, { name: 'Risk & Safety' }],
  },
  '/analytics': {
    title: 'Transporter Performance Analytics',
    subtitle: 'Fuel efficiency metrics, on-time delivery rates, and anonymized benchmarks',
    breadcrumbs: [{ name: 'TradeFlow', path: '/dashboard' }, { name: 'Analytics' }],
  },
  '/notifications': {
    title: 'Notifications Center',
    subtitle: 'Asynchronous alerts, shipment updates, and channel preference settings',
    breadcrumbs: [{ name: 'TradeFlow', path: '/dashboard' }, { name: 'Notifications' }],
  },
  '/profile': {
    title: 'Profile & Account Settings',
    subtitle: 'Business identity, role permissions, and system preferences',
    breadcrumbs: [{ name: 'TradeFlow', path: '/dashboard' }, { name: 'Profile' }],
  },
  '/admin': {
    title: 'Platform Administration Console',
    subtitle: 'User verification queue, system audit logs, and global overrides',
    breadcrumbs: [{ name: 'TradeFlow', path: '/dashboard' }, { name: 'Admin Console' }],
  },
};

export const getRouteConfig = (pathname) => {
  return ROUTE_CONFIG[pathname] || {
    title: 'TradeFlow Platform',
    subtitle: 'Intelligent Ethiopian Logistics',
    breadcrumbs: [{ name: 'TradeFlow', path: '/dashboard' }],
  };
};
