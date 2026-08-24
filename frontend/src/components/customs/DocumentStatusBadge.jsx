import React from 'react';
import { Clock, RefreshCw, CheckCircle2, XCircle } from 'lucide-react';

export const DocumentStatusBadge = ({ status }) => {
  const statusConfig = {
    SUBMITTED: { label: 'Submitted', bg: 'bg-cyan-500/10', text: 'text-cyan-400', border: 'border-cyan-500/20', icon: Clock },
    UNDER_REVIEW: { label: 'Under Review', bg: 'bg-purple-500/10', text: 'text-purple-400', border: 'border-purple-500/20', icon: RefreshCw },
    CLEARED: { label: 'Cleared', bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/20', icon: CheckCircle2 },
    REJECTED: { label: 'Rejected', bg: 'bg-rose-500/10', text: 'text-rose-400', border: 'border-rose-500/20', icon: XCircle },
  };

  const config = statusConfig[status] || { label: status || 'Submitted', bg: 'bg-slate-500/10', text: 'text-slate-400', border: 'border-slate-500/20', icon: Clock };
  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center space-x-1 px-2.5 py-1 text-[11px] font-semibold rounded-full border ${config.bg} ${config.text} ${config.border}`}>
      <Icon className="w-3 h-3 shrink-0" />
      <span>{config.label}</span>
    </span>
  );
};
