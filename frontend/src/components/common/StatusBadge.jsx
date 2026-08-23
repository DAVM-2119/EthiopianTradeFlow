import React from 'react';

const statusStyles = {
  BOOKED: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  ASSIGNED: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
  IN_TRANSIT: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20 glow-cyan',
  CUSTOMS_PROCESSING: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  CUSTOMS_CLEARED: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  DELIVERED: 'bg-teal-500/10 text-teal-400 border-teal-500/20',
  COMPLETED: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  CANCELLED: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  FAILED: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
  
  VERIFIED: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  PENDING: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  PROCESSING: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  SENT: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
};

export const StatusBadge = ({ status }) => {
  const normalized = status ? String(status).toUpperCase() : 'UNKNOWN';
  const style = statusStyles[normalized] || 'bg-slate-800 text-slate-300 border-slate-700';

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${style}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5 animate-pulse" />
      {normalized.replace('_', ' ')}
    </span>
  );
};
