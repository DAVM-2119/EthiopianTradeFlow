import React from 'react';
import { MetricCard } from '../../components/dashboard/MetricCard';
import { RecentActivityFeed } from '../../components/dashboard/RecentActivityFeed';
import { Package, Navigation, FileCheck2, Clock } from 'lucide-react';

export const FreightForwarderDashboard = ({ summary }) => {
  const m = summary?.metrics || {};

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Managed Cargo Loads" value={m.managed_loads || 0} icon={Package} color="cyan" subtext="Client freight orders" />
        <MetricCard title="Active Cargo Movements" value={m.active_shipments || 0} icon={Navigation} color="amber" subtext="Active transit status" />
        <MetricCard title="Customs Cleared" value={m.customs_cleared || 0} icon={FileCheck2} color="emerald" subtext="Documents approved" />
        <MetricCard title="Avg Clearance Time" value={`${m.avg_clearance_days || 1.4} Days`} icon={Clock} color="purple" subtext="ECC processing speed" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <FileCheck2 className="w-5 h-5 text-cyan-400" />
            <span>Corridor Logistics Throughput</span>
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            Managing cross-border freight documentation between port of origin (Djibouti Port) and Ethiopian Dry Ports (Modjo, Semera, Kombolcha, Dire Dawa).
          </p>
        </div>

        <div>
          <RecentActivityFeed activities={summary?.recent_activity || []} />
        </div>
      </div>
    </div>
  );
};
