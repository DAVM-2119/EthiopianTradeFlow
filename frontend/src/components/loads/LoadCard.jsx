import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LoadStatusBadge } from './LoadStatusBadge';
import { CargoTypeBadge } from './CargoTypeBadge';
import { MapPin, Calendar, Weight, Box, ArrowRight } from 'lucide-react';

export const LoadCard = ({ load }) => {
  const navigate = useNavigate();

  const formattedPickup = load.pickup_window_start
    ? new Date(load.pickup_window_start).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    : 'Flexible';

  return (
    <div className="glass-card p-5 rounded-2xl border border-slate-800 hover:border-cyan-500/30 transition flex flex-col justify-between space-y-4">
      <div>
        <div className="flex items-center justify-between gap-2 mb-3">
          <LoadStatusBadge status={load.status} />
          <CargoTypeBadge cargoType={load.cargo_type} />
        </div>

        <h3 className="text-base font-bold text-white line-clamp-1 mb-2">{load.title}</h3>

        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80 mb-3">
          <div className="flex items-center space-x-1 shrink-0 text-cyan-400">
            <MapPin className="w-3.5 h-3.5" />
            <span>{load.origin_city}</span>
          </div>
          <ArrowRight className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          <div className="flex items-center space-x-1 shrink-0 text-emerald-400">
            <MapPin className="w-3.5 h-3.5" />
            <span>{load.destination_city}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs text-slate-400">
          <div className="flex items-center space-x-1.5">
            <Weight className="w-3.5 h-3.5 text-slate-500 shrink-0" />
            <span>{load.weight} Tons</span>
          </div>
          {load.volume && (
            <div className="flex items-center space-x-1.5">
              <Box className="w-3.5 h-3.5 text-slate-500 shrink-0" />
              <span>{load.volume} m³</span>
            </div>
          )}
          <div className="flex items-center space-x-1.5 col-span-2 mt-1">
            <Calendar className="w-3.5 h-3.5 text-slate-500 shrink-0" />
            <span>Pickup: {formattedPickup}</span>
          </div>
        </div>
      </div>

      <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
        <span className="text-[11px] text-slate-500 truncate max-w-[150px]">
          {load.shipper_email ? `By ${load.shipper_email}` : 'Shipper Freight'}
        </span>
        <button
          onClick={() => navigate(`/loads/${load.id}`)}
          className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white rounded-xl text-xs font-semibold flex items-center space-x-1 transition"
        >
          <span>View Details</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
