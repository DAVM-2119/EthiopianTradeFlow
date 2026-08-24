import React from 'react';
import { Clock, CheckCircle2, XCircle, RotateCcw, AlertTriangle } from 'lucide-react';

export const BidStatusBadge = ({ status }) => {
  const statusConfig = {
    ACTIVE: { label: 'Active', bg: 'bg-cyan-500/10', text: 'text-cyan-400', border: 'border-cyan-500/20', icon: Clock },
    ACCEPTED: { label: 'Accepted', bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/20', icon: CheckCircle2 },
    REJECTED: { label: 'Rejected', bg: 'bg-rose-500/10', text: 'text-rose-400', border: 'border-rose-500/20', icon: XCircle },
    WITHDRAWN: { label: 'Withdrawn', bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/20', icon: RotateCcw },
    EXPIRED: { label: 'Expired', bg: 'bg-slate-500/10', text: 'text-slate-400', border: 'border-slate-500/20', icon: AlertTriangle },
  };

  const config = statusConfig[status] || statusConfig.ACTIVE;
  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center space-x-1 px-2.5 py-1 text-[11px] font-semibold rounded-full border ${config.bg} ${config.text} ${config.border}`}>
      <Icon className="w-3 h-3 shrink-0" />
      <span>{config.label}</span>
    </span>
  );
};
