import React from 'react';
import { FileEdit, Globe, BookmarkCheck, XCircle } from 'lucide-react';

export const LoadStatusBadge = ({ status }) => {
  const statusConfig = {
    DRAFT: { label: 'Draft', bg: 'bg-slate-500/10', text: 'text-slate-400', border: 'border-slate-500/20', icon: FileEdit },
    POSTED: { label: 'Posted', bg: 'bg-cyan-500/10', text: 'text-cyan-400', border: 'border-cyan-500/20', icon: Globe },
    BOOKED: { label: 'Booked', bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/20', icon: BookmarkCheck },
    CANCELLED: { label: 'Cancelled', bg: 'bg-rose-500/10', text: 'text-rose-400', border: 'border-rose-500/20', icon: XCircle },
  };

  const config = statusConfig[status] || statusConfig.POSTED;
  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center space-x-1 px-2.5 py-1 text-[11px] font-semibold rounded-full border ${config.bg} ${config.text} ${config.border}`}>
      <Icon className="w-3 h-3 shrink-0" />
      <span>{config.label}</span>
    </span>
  );
};
