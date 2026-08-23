import React from 'react';
import { MetricCard } from '../../components/dashboard/MetricCard';
import { DashboardChart } from '../../components/dashboard/DashboardChart';
import { RecentActivityFeed } from '../../components/dashboard/RecentActivityFeed';
import { Package, Navigation, DollarSign, Truck, Award } from 'lucide-react';

export const TransporterDashboard = ({ summary }) => {
  const m = summary?.metrics || {};

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Available Loads" value={m.available_loads || 0} icon={Package} color="cyan" subtext="Open marketplace load listings" />
        <MetricCard title="Active Cargo Shipments" value={m.active_shipments || 0} icon={Navigation} color="amber" subtext="Fleet trucks in motion" />
        <MetricCard title="Total Earnings (ETB)" value={`${(m.earnings_etb || 0).toLocaleString()} ETB`} icon={DollarSign} color="emerald" subtext="Confirmed settlement payouts" />
        <MetricCard title="On-Time Delivery Rate" value={`${m.on_time_delivery_rate || 96.4}%`} icon={Award} color="purple" subtext="Corridor benchmark accuracy" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <DashboardChart title="Transporter Earnings Trend (ETB)" type="bar" data={summary?.charts?.monthly_earnings || []} />
          <DashboardChart title="Fleet Utilization Breakdown" type="list" data={summary?.charts?.fleet_status || []} />
        </div>
        <div>
          <RecentActivityFeed activities={summary?.recent_activity || []} />
        </div>
      </div>
    </div>
  );
};
