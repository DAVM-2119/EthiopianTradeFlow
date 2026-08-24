import React from 'react';
import { MapPin, Navigation, Compass, AlertTriangle, ShieldCheck } from 'lucide-react';

export const ShipmentMap = ({ latestTracking, origin = 'Djibouti Port', destination = 'Modjo Dry Port', isConnected }) => {
  const lat = latestTracking?.latitude || 11.589;
  const lng = latestTracking?.longitude || 43.145;
  const speed = latestTracking?.speed || 0;

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4 relative overflow-hidden">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Navigation className="w-4 h-4 text-cyan-400" />
            <span>Interactive GPS Live Corridor Tracking</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Djibouti Port ➔ Modjo Dry Port Freight Route (N1 Highway)
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span
            className={`px-2.5 py-1 text-[10px] font-bold rounded-full border flex items-center space-x-1 ${
              isConnected
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 animate-pulse'
                : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
            }`}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-current" />
            <span>{isConnected ? 'LIVE WEBSOCKET' : 'REST POLLING'}</span>
          </span>
        </div>
      </div>

      {/* Map visual canvas placeholder / Leaflet container */}
      <div className="h-72 w-full bg-slate-950 rounded-xl border border-slate-800 relative flex flex-col justify-between p-4 overflow-hidden bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px]">
        {/* Route Header Info */}
        <div className="flex items-center justify-between z-10">
          <div className="px-3 py-1.5 bg-slate-900/90 border border-slate-800 rounded-lg text-xs font-semibold text-cyan-400 flex items-center space-x-1.5">
            <MapPin className="w-3.5 h-3.5" />
            <span>Origin: {origin}</span>
          </div>

          <div className="px-3 py-1.5 bg-slate-900/90 border border-slate-800 rounded-lg text-xs font-semibold text-emerald-400 flex items-center space-x-1.5">
            <MapPin className="w-3.5 h-3.5" />
            <span>Destination: {destination}</span>
          </div>
        </div>

        {/* Live GPS Vehicle Marker */}
        <div className="my-auto text-center z-10 space-y-2">
          <div className="w-14 h-14 rounded-2xl bg-cyan-500/20 border-2 border-cyan-400 flex items-center justify-center mx-auto shadow-xl shadow-cyan-500/30 animate-bounce">
            <Navigation className="w-7 h-7 text-cyan-400 rotate-45" />
          </div>
          <div className="inline-block bg-slate-900/90 backdrop-blur px-4 py-2 rounded-xl border border-slate-800">
            <p className="text-xs font-bold text-white">Current Vehicle Telemetry Position</p>
            <p className="text-[11px] text-cyan-400 font-mono mt-0.5">
              Lat: {Number(lat).toFixed(4)}° | Lng: {Number(lng).toFixed(4)}°
            </p>
          </div>
        </div>

        {/* Corridor Security & Risk Status Banner */}
        <div className="flex items-center justify-between z-10 pt-2 border-t border-slate-800/80 text-[11px]">
          <span className="text-slate-400 flex items-center space-x-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Corridor Security: <strong className="text-emerald-400 font-bold">NORMAL</strong></span>
          </span>
          <span className="text-slate-400 flex items-center space-x-1">
            <Compass className="w-3.5 h-3.5 text-cyan-400" />
            <span>Speed: {speed ? `${Number(speed).toFixed(0)} km/h` : 'Stationary'}</span>
          </span>
        </div>
      </div>
    </div>
  );
};
