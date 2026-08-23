import React from 'react';
import { LoadStatusBadge } from './LoadStatusBadge';
import { CargoTypeBadge } from './CargoTypeBadge';
import { MapPin, Calendar, Weight, Box, FileText, User } from 'lucide-react';

export const LoadSummary = ({ load }) => {
  const formatDate = (dt) => (dt ? new Date(dt).toLocaleString() : 'Not Specified');

  return (
    <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800 space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div>
          <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-widest">Load Listing #{load.id?.substring(0, 8)}</span>
          <h2 className="text-xl font-extrabold text-white mt-1">{load.title}</h2>
        </div>
        <div className="flex items-center space-x-2">
          <CargoTypeBadge cargoType={load.cargo_type} />
          <LoadStatusBadge status={load.status} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center space-x-1.5">
            <MapPin className="w-4 h-4" />
            <span>Origin Location</span>
          </h4>
          <div>
            <p className="text-sm font-bold text-white">{load.origin_city}</p>
            <p className="text-xs text-slate-400 mt-0.5">{load.origin_address || 'Standard Dry Port / Warehouse Hub'}</p>
          </div>
        </div>

        <div className="space-y-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
            <MapPin className="w-4 h-4" />
            <span>Destination Location</span>
          </h4>
          <div>
            <p className="text-sm font-bold text-white">{load.destination_city}</p>
            <p className="text-xs text-slate-400 mt-0.5">{load.destination_address || 'Regional Distribution Hub'}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
        <div className="p-3 bg-slate-900/40 rounded-xl border border-slate-800">
          <p className="text-[10px] text-slate-500 font-semibold uppercase">Total Weight</p>
          <p className="text-sm font-bold text-white mt-1 flex items-center space-x-1">
            <Weight className="w-3.5 h-3.5 text-cyan-400" />
            <span>{load.weight} Tons</span>
          </p>
        </div>

        <div className="p-3 bg-slate-900/40 rounded-xl border border-slate-800">
          <p className="text-[10px] text-slate-500 font-semibold uppercase">Total Volume</p>
          <p className="text-sm font-bold text-white mt-1 flex items-center space-x-1">
            <Box className="w-3.5 h-3.5 text-cyan-400" />
            <span>{load.volume ? `${load.volume} m³` : 'N/A'}</span>
          </p>
        </div>

        <div className="p-3 bg-slate-900/40 rounded-xl border border-slate-800">
          <p className="text-[10px] text-slate-500 font-semibold uppercase">Pickup Start</p>
          <p className="text-xs font-bold text-white mt-1">{formatDate(load.pickup_window_start)}</p>
        </div>

        <div className="p-3 bg-slate-900/40 rounded-xl border border-slate-800">
          <p className="text-[10px] text-slate-500 font-semibold uppercase">Pickup End</p>
          <p className="text-xs font-bold text-white mt-1">{formatDate(load.pickup_window_end)}</p>
        </div>
      </div>

      {load.special_requirements && (
        <div className="p-4 bg-slate-900/40 rounded-xl border border-slate-800 space-y-1">
          <p className="text-xs font-semibold text-amber-400 flex items-center space-x-1">
            <FileText className="w-3.5 h-3.5" />
            <span>Special Requirements</span>
          </p>
          <p className="text-xs text-slate-300">{load.special_requirements}</p>
        </div>
      )}

      <div className="pt-2 flex items-center space-x-2 text-xs text-slate-500 border-t border-slate-800/60">
        <User className="w-3.5 h-3.5" />
        <span>Posted by: {load.shipper_email || 'Shipper'}</span>
      </div>
    </div>
  );
};
