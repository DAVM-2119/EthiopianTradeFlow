import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShipmentStatusBadge } from './ShipmentStatusBadge';
import { CargoTypeBadge } from '../loads/CargoTypeBadge';
import { MapPin, ArrowRight, UserCheck, Truck, Navigation } from 'lucide-react';

export const ShipmentCard = ({ shipment }) => {
  const navigate = useNavigate();

  const load = shipment.load_data || shipment.load_detail || {};
  const origin = shipment.origin_city || load.origin_city || 'Djibouti Port';
  const destination = shipment.destination_city || load.destination_city || 'Modjo Dry Port';
  const cargoType = shipment.cargo_type || load.cargo_type || 'GENERAL_CARGO';

  return (
    <div className="glass-card p-5 rounded-2xl border border-slate-800 hover:border-cyan-500/30 transition flex flex-col justify-between space-y-4">
      <div>
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-widest">
            Shipment #{shipment.id?.substring(0, 8)}
          </span>
          <ShipmentStatusBadge status={shipment.status} />
        </div>

        {/* Route Header */}
        <div className="flex items-center space-x-2 my-2 bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">
          <MapPin className="w-4 h-4 text-cyan-400 shrink-0" />
          <span className="text-xs font-bold text-white truncate">{origin}</span>
          <ArrowRight className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          <span className="text-xs font-bold text-white truncate">{destination}</span>
        </div>

        <div className="flex items-center justify-between pt-1 text-xs">
          <CargoTypeBadge cargoType={cargoType} />
          {shipment.vehicle && (
            <span className="text-[11px] text-slate-400 font-semibold flex items-center space-x-1">
              <Truck className="w-3.5 h-3.5 text-cyan-400" />
              <span>{shipment.vehicle_plate || 'Assigned Truck'}</span>
            </span>
          )}
        </div>
      </div>

      <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
        <span className="text-[10px] text-slate-500">
          Created {shipment.created_at ? new Date(shipment.created_at).toLocaleDateString() : 'Recently'}
        </span>

        <div className="flex items-center space-x-2">
          {shipment.status === 'IN_TRANSIT' && (
            <button
              onClick={() => navigate(`/tracking/${shipment.id}`)}
              className="px-2.5 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-xl text-xs font-semibold flex items-center space-x-1 transition"
            >
              <Navigation className="w-3.5 h-3.5" />
              <span>Live Map</span>
            </button>
          )}

          <button
            onClick={() => navigate(`/shipments/${shipment.id}`)}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold flex items-center space-x-1 transition"
          >
            <span>Overview</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
