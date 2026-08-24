import React from 'react';
import { Clock, Navigation, Zap, MapPin, Gauge } from 'lucide-react';

export const ETAInfoCard = ({ etaData, latestTracking }) => {
  const predictedEta = etaData?.predicted_eta || etaData?.eta || latestTracking?.timestamp;
  const remainingKm = etaData?.remaining_distance_km || latestTracking?.remaining_distance;
  const currentSpeed = latestTracking?.speed || etaData?.current_speed_kmh || 0;

  const formattedEta = predictedEta
    ? new Date(predictedEta).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    : 'Calculating...';

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
          <Clock className="w-4 h-4 text-cyan-400" />
          <span>Real-Time Predictive ETA Engine</span>
        </h4>
        <span className="text-[10px] font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2 py-0.5 rounded-full">
          AI Model Active
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-center">
        <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800">
          <Clock className="w-4 h-4 text-cyan-400 mx-auto mb-1" />
          <span className="text-[10px] text-slate-500 font-semibold uppercase">Estimated Arrival</span>
          <p className="text-sm font-black text-cyan-300 mt-0.5">{formattedEta}</p>
        </div>

        <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800">
          <Navigation className="w-4 h-4 text-emerald-400 mx-auto mb-1" />
          <span className="text-[10px] text-slate-500 font-semibold uppercase">Distance Remaining</span>
          <p className="text-sm font-black text-emerald-400 mt-0.5">
            {remainingKm !== undefined ? `${Number(remainingKm).toFixed(1)} km` : 'In Transit'}
          </p>
        </div>

        <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800">
          <Gauge className="w-4 h-4 text-amber-400 mx-auto mb-1" />
          <span className="text-[10px] text-slate-500 font-semibold uppercase">GPS Vehicle Speed</span>
          <p className="text-sm font-black text-amber-400 mt-0.5">
            {currentSpeed ? `${Number(currentSpeed).toFixed(0)} km/h` : 'Stopped / Idle'}
          </p>
        </div>
      </div>
    </div>
  );
};
