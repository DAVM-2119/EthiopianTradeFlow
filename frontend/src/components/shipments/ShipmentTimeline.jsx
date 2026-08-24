import React from 'react';
import { CheckCircle2, Circle, Clock, Truck, ShieldCheck, PackageCheck, AlertTriangle } from 'lucide-react';

const MILESTONES = [
  { key: 'BOOKED', label: 'Booked' },
  { key: 'ASSIGNED', label: 'Assigned' },
  { key: 'PICKUP_READY', label: 'Pickup Ready' },
  { key: 'IN_TRANSIT', label: 'In Transit' },
  { key: 'CUSTOMS_PROCESSING', label: 'Customs' },
  { key: 'CUSTOMS_CLEARED', label: 'Cleared' },
  { key: 'DELIVERED', label: 'Delivered' },
  { key: 'COMPLETED', label: 'Completed' },
];

export const ShipmentTimeline = ({ currentStatus, events = [] }) => {
  const currentIndex = MILESTONES.findIndex((m) => m.key === currentStatus);
  const isExceptional = ['CANCELLED', 'FAILED', 'DISPUTED'].includes(currentStatus);

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-1.5">
          <Truck className="w-4 h-4 text-cyan-400" />
          <span>Shipment Milestone Lifecycle Progress</span>
        </h3>
        {isExceptional && (
          <span className="px-2.5 py-0.5 bg-rose-500/10 text-rose-400 border border-rose-500/20 text-[11px] font-bold rounded-full flex items-center space-x-1">
            <AlertTriangle className="w-3 h-3" />
            <span>Status: {currentStatus}</span>
          </span>
        )}
      </div>

      <div className="relative flex items-center justify-between overflow-x-auto py-4 px-2 gap-2">
        {MILESTONES.map((m, idx) => {
          const isDone = currentIndex >= 0 && idx <= currentIndex;
          const isCurrent = idx === currentIndex;

          return (
            <div key={m.key} className="flex-1 flex flex-col items-center min-w-[75px] relative group">
              {/* Connector line */}
              {idx < MILESTONES.length - 1 && (
                <div
                  className={`absolute top-4 left-[50%] right-[-50%] h-0.5 z-0 ${
                    currentIndex > idx ? 'bg-cyan-500' : 'bg-slate-800'
                  }`}
                />
              )}

              {/* Node indicator */}
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center z-10 transition font-bold text-xs ${
                  isCurrent
                    ? 'bg-cyan-500 text-white ring-4 ring-cyan-500/20 shadow-lg shadow-cyan-500/30'
                    : isDone
                    ? 'bg-emerald-500 text-white'
                    : 'bg-slate-900 border border-slate-800 text-slate-500'
                }`}
              >
                {isDone ? <CheckCircle2 className="w-4 h-4" /> : idx + 1}
              </div>

              {/* Label */}
              <span
                className={`text-[11px] font-semibold mt-2 text-center truncate max-w-[80px] ${
                  isCurrent ? 'text-cyan-400 font-bold' : isDone ? 'text-slate-200' : 'text-slate-500'
                }`}
              >
                {m.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
