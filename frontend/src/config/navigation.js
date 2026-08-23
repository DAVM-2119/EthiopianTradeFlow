import {
  LayoutDashboard, Package, PlusCircle, ListFilter, Gavel,
  Navigation, MapPin, Truck, Users, FileCheck2, DollarSign,
  ShieldAlert, Bell, Settings, BarChart3, Receipt, FileText, UserCheck
} from 'lucide-react';

export const NAVIGATION_CONFIG = {
  SHIPPER: [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Marketplace', path: '/loads', icon: Package },
    { name: 'Shipments', path: '/shipments', icon: Navigation },
    { name: 'Live Tracking', path: '/tracking', icon: MapPin },
    { name: 'Customs Documents', path: '/customs', icon: FileCheck2 },
    { name: 'Payments & Invoice', path: '/payments', icon: DollarSign },
    { name: 'Security Alerts', path: '/risk', icon: ShieldAlert },
    { name: 'Notifications', path: '/notifications', icon: Bell },
    { name: 'Profile & Settings', path: '/profile', icon: Settings },
  ],
  TRANSPORTER: [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Available Loads', path: '/loads', icon: Package },
    { name: 'My Bids', path: '/bids', icon: Gavel },
    { name: 'Shipments', path: '/shipments', icon: Navigation },
    { name: 'Fleet Vehicles', path: '/fleet/vehicles', icon: Truck },
    { name: 'Drivers', path: '/fleet/drivers', icon: Users },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'Earnings & Payouts', path: '/payments', icon: DollarSign },
    { name: 'Notifications', path: '/notifications', icon: Bell },
    { name: 'Profile & Settings', path: '/profile', icon: Settings },
  ],
  DRIVER: [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Assigned Shipment', path: '/shipments', icon: Navigation },
    { name: 'Live Tracking', path: '/tracking', icon: MapPin },
    { name: 'Security Alerts', path: '/risk', icon: ShieldAlert },
    { name: 'Notifications', path: '/notifications', icon: Bell },
    { name: 'Profile', path: '/profile', icon: Settings },
  ],
  FREIGHT_FORWARDER: [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Client Loads', path: '/loads', icon: Package },
    { name: 'Shipments', path: '/shipments', icon: Navigation },
    { name: 'Customs Clearance', path: '/customs', icon: FileCheck2 },
    { name: 'Live Tracking', path: '/tracking', icon: MapPin },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'Notifications', path: '/notifications', icon: Bell },
    { name: 'Profile & Settings', path: '/profile', icon: Settings },
  ],
  CUSTOMS_STAFF: [
    { name: 'Clearance Queue', path: '/customs', icon: FileCheck2 },
    { name: 'Customs Documents', path: '/customs/documents', icon: FileText },
    { name: 'Shipments Review', path: '/shipments', icon: Navigation },
    { name: 'Notifications', path: '/notifications', icon: Bell },
    { name: 'Profile', path: '/profile', icon: Settings },
  ],
  ADMIN: [
    { name: 'System Overview', path: '/dashboard', icon: LayoutDashboard },
    { name: 'User Management', path: '/admin/users', icon: Users },
    { name: 'Verification Queue', path: '/admin/verifications', icon: UserCheck },
    { name: 'Loads Console', path: '/loads', icon: Package },
    { name: 'Shipments Console', path: '/shipments', icon: Navigation },
    { name: 'Payments & Disputes', path: '/payments', icon: DollarSign },
    { name: 'Risk Zones Manager', path: '/risk', icon: ShieldAlert },
    { name: 'Notifications Center', path: '/notifications', icon: Bell },
    { name: 'System Settings', path: '/profile', icon: Settings },
  ],
};

export const getNavigationForRole = (role) => {
  return NAVIGATION_CONFIG[role] || NAVIGATION_CONFIG.SHIPPER;
};
