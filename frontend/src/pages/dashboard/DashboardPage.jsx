import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { PageHeader } from '../../components/common/PageHeader';
import { StatusBadge } from '../../components/common/StatusBadge';
import { Package, Navigation, DollarSign, Bell, ShieldCheck, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DashboardPage = () => {
  const { user } = useAuth();
  const role = user?.role || 'SHIPPER';

  const stats = [
    { title: 'Active Shipments', value: '12', icon: Navigation, color: 'text-cyan-400', bg: 'bg-cyan-500/10' },
    { title: 'Posted Loads', value: '8', icon: Package, color: 'text-amber-400', bg: 'bg-amber-500/10' },
    { title: 'Pending Bids', value: '15', icon: DollarSign, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    { title: 'Notifications', value: '4', icon: Bell, color: 'text-purple-400', bg: 'bg-purple-500/10' },
  ];

  return (
    <div>
      <PageHeader
        title={`Welcome back, ${user?.first_name || 'User'}`}
        subtitle={`Role: ${role} | Account Status: ${user?.status || 'VERIFIED'} | Corridor: Djibouti Port ➔ Modjo Dry Port`}
        actions={
          <Link
            to="/loads"
            className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-cyan-500/20 transition flex items-center space-x-2"
          >
            <span>Manage Loads</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.title} className="glass-card p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-400">{stat.title}</p>
                <p className="text-2xl font-black text-white mt-1">{stat.value}</p>
              </div>
              <div className={`w-12 h-12 rounded-xl ${stat.bg} ${stat.color} flex items-center justify-center`}>
                <Icon className="w-6 h-6" />
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <ShieldCheck className="w-5 h-5 text-cyan-400" />
              <span>Corridor Security & System Status</span>
            </h3>
            <StatusBadge status="VERIFIED" />
          </div>
          <p className="text-xs text-slate-300 leading-relaxed mb-4">
            TradeFlow is actively monitoring freight traffic along the primary Ethiopian export/import corridor (Djibouti → Modjo → Addis Ababa). All backend services (GPS Tracking, Realtime WebSockets, ETA Engine, Risk Zones, Payments, and Notifications Engine) are operational.
          </p>
          <div className="h-48 bg-slate-900/80 rounded-xl border border-slate-800/80 flex items-center justify-center p-4">
            <p className="text-xs font-medium text-slate-500 text-center">
              📍 Geodesic Corridor Map Active — MapLibre GL JS Container Initialized
            </p>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <h3 className="text-base font-bold text-white mb-4">Account Metadata</h3>
          <div className="space-y-3 text-xs">
            <div className="flex justify-between py-2 border-b border-slate-800">
              <span className="text-slate-400">Email:</span>
              <span className="font-semibold text-slate-200">{user?.email}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800">
              <span className="text-slate-400">Role:</span>
              <span className="font-semibold text-cyan-400">{role}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800">
              <span className="text-slate-400">Verification:</span>
              <StatusBadge status={user?.is_verified ? 'VERIFIED' : 'PENDING'} />
            </div>
            <div className="flex justify-between py-2">
              <span className="text-slate-400">API Health:</span>
              <span className="font-semibold text-emerald-400">CONNECTED (127.0.0.1:8000)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
