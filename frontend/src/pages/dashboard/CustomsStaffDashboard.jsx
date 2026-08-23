import React from 'react';
import { MetricCard } from '../../components/dashboard/MetricCard';
import { RecentActivityFeed } from '../../components/dashboard/RecentActivityFeed';
import { FileCheck2, Clock, CheckCircle2, XCircle } from 'lucide-react';

export const CustomsStaffDashboard = ({ summary }) => {
  const m = summary?.metrics || {};

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Pending Clearance" value={m.pending_documents || 0} icon={Clock} color="amber" subtext="Awaiting document verification" />
        <MetricCard title="Approved Customs Docs" value={m.approved_documents || 0} icon={CheckCircle2} color="emerald" subtext="ECC clearance issued" />
        <MetricCard title="Rejected Submissions" value={m.rejected_documents || 0} icon={XCircle} color="rose" subtext="Discrepancy flagged" />
        <MetricCard title="Total Document Intake" value={m.total_documents || 0} icon={FileCheck2} color="cyan" subtext="All declaration files" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <FileCheck2 className="w-5 h-5 text-cyan-400" />
            <span>Ethiopian Customs Commission Portal</span>
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            Reviewing Commercial Invoices, Packing Lists, Bills of Lading, and Certificates of Origin for active import/export declarations.
          </p>
        </div>

        <div>
          <RecentActivityFeed activities={summary?.recent_activity || []} />
        </div>
      </div>
    </div>
  );
};
