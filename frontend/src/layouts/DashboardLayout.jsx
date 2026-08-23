import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Truck, LayoutDashboard, Package, Navigation, MapPin,
  FileCheck2, DollarSign, Bell, Settings, LogOut, Menu, X, ShieldAlert, Users
} from 'lucide-react';

export const DashboardLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const role = user?.role || 'SHIPPER';

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Loads', path: '/loads', icon: Package },
    { name: 'Shipments', path: '/shipments', icon: Navigation },
    { name: 'Live Tracking', path: '/tracking', icon: MapPin },
    { name: 'Customs', path: '/customs', icon: FileCheck2 },
    { name: 'Payments', path: '/payments', icon: DollarSign },
    { name: 'Risk & Alerts', path: '/risk', icon: ShieldAlert },
    { name: 'Notifications', path: '/notifications', icon: Bell },
    { name: 'Profile & Settings', path: '/profile', icon: Settings },
  ];

  if (role === 'ADMIN') {
    navItems.push({ name: 'Admin Console', path: '/admin', icon: Users });
  }

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-950 flex text-slate-100">
      {/* Sidebar Desktop */}
      <aside className="hidden md:flex flex-col w-64 glass-panel border-r border-slate-800 shrink-0">
        <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-md">
            <Truck className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="font-extrabold text-lg text-white leading-tight">TradeFlow</h2>
            <p className="text-[10px] text-cyan-400 font-semibold uppercase tracking-wider">Ethiopia Freight</p>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition ${
                    isActive
                      ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center space-x-3 p-2 mb-2 rounded-lg bg-slate-900/60">
            <div className="w-9 h-9 rounded-full bg-cyan-500/20 text-cyan-300 flex items-center justify-center font-bold text-sm">
              {user?.email?.[0]?.toUpperCase() || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-slate-200 truncate">{user?.email}</p>
              <p className="text-[10px] text-cyan-400 font-medium">{role}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center space-x-2 px-3 py-2 text-xs font-semibold text-rose-400 hover:bg-rose-500/10 rounded-lg transition border border-rose-500/20"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header Bar */}
        <header className="h-16 glass-panel border-b border-slate-800 px-4 sm:px-8 flex items-center justify-between sticky top-0 z-30">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden text-slate-400 hover:text-white"
            >
              {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              Djibouti ➔ Modjo Corridor
            </span>
          </div>

          <div className="flex items-center space-x-4">
            <NavLink to="/notifications" className="relative p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-cyan-400 ring-2 ring-slate-950" />
            </NavLink>
          </div>
        </header>

        {/* Dynamic Page View */}
        <main className="flex-1 p-4 sm:p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
