import React from 'react';
import { Bookmark, Truck, CheckCircle2, ShieldCheck, XCircle, AlertTriangle, Clock, RefreshCw } from 'lucide-react';

export const ShipmentStatusBadge = ({ status }) => {
  const statusConfig = {
    BOOKED: { label: 'Booked', bg: 'bg-cyan-500/10', text: 'text-cyan-400', border: 'border-cyan-500/20', icon: Bookmark },
    ASSIGNED: { label: 'Assigned', bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/20', icon: Truck },
    PICKUP_READY: { label: 'Pickup Ready', bg: 'bg-indigo-500/10', text: 'text-indigo-400', border: 'border-indigo-500/20', icon: Clock },
    IN_TRANSIT: { label: 'In Transit', bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/20', icon: Truck },
    CUSTOMS_PROCESSING: { label: 'Customs Processing', bg: 'bg-purple-500/10', text: 'text-purple-400', border: 'border-purple-500/20', icon: RefreshCw },
    CUSTOMS_CLEARED: { label: 'Customs Cleared', bg: 'bg-teal-500/10', text: 'text-teal-400', border: 'border-teal-500/20', icon: ShieldCheck },
    DELIVERED: { label: 'Delivered', bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/20', icon: CheckCircle2 },
    COMPLETED: { label: 'Completed', bg: 'bg-green-500/10', text: 'text-green-400', border: 'border-green-500/20', icon: CheckCircle2 },
    CANCELLED: { label: 'Cancelled', bg: 'bg-rose-500/10', text: 'text-rose-400', border: 'border-rose-500/20', icon: XCircle },
    FAILED: { label: 'Failed', bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/20', icon: AlertTriangle },
    DISPUTED: { label: 'Disputed', bg: 'bg-orange-500/10', text: 'text-orange-400', border: 'border-orange-500/20', icon: AlertTriangle },
  };

  const config = statusConfig[status] || { label: status || 'Unknown', bg: 'bg-slate-500/10', text: 'text-slate-400', border: 'border-slate-500/20', icon: Clock };
  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center space-x-1 px-2.5 py-1 text-[11px] font-semibold rounded-full border ${config.bg} ${config.text} ${config.border}`}>
      <Icon className="w-3 h-3 shrink-0" />
      <span>{config.label}</span>
    </span>
  );
};
