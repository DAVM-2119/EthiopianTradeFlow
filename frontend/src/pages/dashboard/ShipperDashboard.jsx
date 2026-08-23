import React from 'react';
import { MetricCard } from '../../components/dashboard/MetricCard';
import { DashboardChart } from '../../components/dashboard/DashboardChart';
import { RecentActivityFeed } from '../../components/dashboard/RecentActivityFeed';
import { Package, Navigation, DollarSign, CheckCircle2 } from 'lucide-react';

export const ShipperDashboard = ({ summary }) => {
  const m = summary?.metrics || {};

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Active Posted Loads" value={m.active_loads || 0} icon={Package} color="cyan" subtext="Open marketplace load listings" />
        <MetricCard title="In-Transit Freight" value={m.active_shipments || 0} icon={Navigation} color="amber" subtext="En route Djibouti ➔ Modjo" />
        <MetricCard title="Pending Bids" value={m.pending_bids || 0} icon={DollarSign} color="purple" subtext="Transporter rate offers" />
        <MetricCard title="Completed Shipments" value={m.completed_shipments || 0} icon={CheckCircle2} color="emerald" subtext="Successful delivery milestones" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <DashboardChart title="Monthly Freight Throughput (Shipments)" type="bar" data={summary?.charts?.monthly_shipments || []} />
          <DashboardChart title="Freight Status Breakdown" type="list" data={summary?.charts?.status_distribution || []} />
        </div>
        <div>
          <RecentActivityFeed activities={summary?.recent_activity || []} />
        </div>
      </div>
    </div>
  );
};
