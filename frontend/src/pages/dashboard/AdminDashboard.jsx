import React from 'react';
import { MetricCard } from '../../components/dashboard/MetricCard';
import { DashboardChart } from '../../components/dashboard/DashboardChart';
import { RecentActivityFeed } from '../../components/dashboard/RecentActivityFeed';
import { Users, UserCheck, Navigation, ShieldAlert } from 'lucide-react';

export const AdminDashboard = ({ summary }) => {
  const m = summary?.metrics || {};

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Registered Users" value={m.total_users || 0} icon={Users} color="cyan" subtext="Platform-wide accounts" />
        <MetricCard title="Pending Verifications" value={m.pending_verifications || 0} icon={UserCheck} color="amber" subtext="KYC & License review" />
        <MetricCard title="Global Active Shipments" value={m.total_shipments || 0} icon={Navigation} color="purple" subtext="Total system freight" />
        <MetricCard title="Open Disputes" value={m.disputes || 0} icon={ShieldAlert} color="rose" subtext="Financial settlement claims" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <DashboardChart title="User Roles Distribution" type="list" data={summary?.charts?.user_roles || []} />
        </div>
        <div>
          <RecentActivityFeed activities={summary?.recent_activity || []} />
        </div>
      </div>
    </div>
  );
};
