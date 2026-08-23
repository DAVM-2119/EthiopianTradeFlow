import React, { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Menu, Bell, Wifi, WifiOff } from 'lucide-react';
import { Breadcrumbs } from './Breadcrumbs';
import { UserMenu } from './UserMenu';
import { getRouteConfig } from '../../config/routeConfig';

export const Navbar = ({ onToggleSidebar, isSidebarCollapsed }) => {
  const location = useLocation();
  const routeMeta = getRouteConfig(location.pathname);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <header className="h-16 glass-panel border-b border-slate-800 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30 shrink-0">
      <div className="flex items-center space-x-3 min-w-0">
        <button
          onClick={onToggleSidebar}
          className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-800 transition"
          aria-label="Toggle Navigation Sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="min-w-0">
          <Breadcrumbs items={routeMeta.breadcrumbs} />
          <h1 className="text-sm sm:text-base font-extrabold text-white truncate leading-tight">
            {routeMeta.title}
          </h1>
        </div>
      </div>

      <div className="flex items-center space-x-3 sm:space-x-4 shrink-0">
        <div
          className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold border ${
            isOnline
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
              : 'bg-rose-500/10 text-rose-400 border-rose-500/20 animate-pulse'
          }`}
        >
          {isOnline ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
          <span className="hidden sm:inline">{isOnline ? 'Online' : 'Offline'}</span>
        </div>

        <NavLink
          to="/notifications"
          className="relative p-2 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition"
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-cyan-400 ring-2 ring-slate-950" />
        </NavLink>

        <UserMenu />
      </div>
    </header>
  );
};
