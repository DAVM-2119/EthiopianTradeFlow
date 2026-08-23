import React from 'react';
import { Activity, Clock, ShieldAlert, Package, Navigation, DollarSign } from 'lucide-react';

export const RecentActivityFeed = ({ activities = [] }) => {
  const getIcon = (type) => {
    switch (type) {
      case 'SECURITY':
        return <ShieldAlert className="w-4 h-4 text-amber-400" />;
      case 'LOAD':
        return <Package className="w-4 h-4 text-cyan-400" />;
      case 'PAYMENT':
        return <DollarSign className="w-4 h-4 text-emerald-400" />;
      default:
        return <Navigation className="w-4 h-4 text-cyan-400" />;
    }
  };

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
        <h3 className="text-sm font-bold text-white flex items-center space-x-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <span>Recent Activity Stream</span>
        </h3>
        <span className="text-[10px] text-cyan-400 font-semibold uppercase tracking-wider">Live Feed</span>
      </div>

      {activities.length === 0 ? (
        <div className="p-8 text-center text-xs text-slate-500">No recent activity recorded</div>
      ) : (
        <div className="space-y-4">
          {activities.map((act) => (
            <div key={act.id} className="flex items-start space-x-3 text-xs p-3 rounded-xl bg-slate-900/60 border border-slate-800/60">
              <div className="p-2 rounded-lg bg-slate-800/80 shrink-0 mt-0.5">{getIcon(act.type)}</div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-slate-200 truncate">{act.title}</p>
                <p className="text-slate-400 mt-0.5 text-[11px] leading-relaxed">{act.description}</p>
                <div className="flex items-center space-x-1 text-[10px] text-slate-500 mt-1.5">
                  <Clock className="w-3 h-3" />
                  <span>{act.timestamp}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
