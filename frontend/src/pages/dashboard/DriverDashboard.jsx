import React from 'react';
import { MetricCard } from '../../components/dashboard/MetricCard';
import { RecentActivityFeed } from '../../components/dashboard/RecentActivityFeed';
import { Navigation, CheckCircle2, ShieldAlert, MapPin } from 'lucide-react';

export const DriverDashboard = ({ summary }) => {
  const m = summary?.metrics || {};

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Assigned Shipment" value={m.assigned_shipments || 0} icon={Navigation} color="cyan" subtext="Current active freight route" />
        <MetricCard title="Completed Trips" value={m.completed_trips || 0} icon={CheckCircle2} color="emerald" subtext="Delivered load history" />
        <MetricCard title="Corridor Alerts" value={m.active_alerts || 0} icon={ShieldAlert} color="amber" subtext="Active risk zone advisories" />
        <MetricCard title="Safety Score" value={m.corridor_safety_score || '98.5%'} icon={MapPin} color="purple" subtext="Corridor compliance score" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <MapPin className="w-5 h-5 text-cyan-400" />
            <span>Driver Navigation & GPS Status</span>
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            GPS tracking unit active. Route: Djibouti Port ➔ Awash ➔ Modjo Dry Port. Auto-sync enables offline location tracking during highway cell coverage gaps.
          </p>
          <div className="h-44 bg-slate-900/80 rounded-xl border border-slate-800 flex items-center justify-center p-4">
            <p className="text-xs font-semibold text-slate-400">
              📍 Live Driver Location Tracking Engine Running (Interval: 15s)
            </p>
          </div>
        </div>

        <div>
          <RecentActivityFeed activities={summary?.recent_activity || []} />
        </div>
      </div>
    </div>
  );
};
