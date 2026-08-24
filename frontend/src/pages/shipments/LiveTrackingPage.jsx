import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { PageHeader } from '../../components/common/PageHeader';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { ShipmentMap } from '../../components/tracking/ShipmentMap';
import { ETAInfoCard } from '../../components/tracking/ETAInfoCard';
import { useShipmentTracking } from '../../hooks/useShipmentTracking';
import apiClient from '../../api/axios';
import { API_ENDPOINTS } from '../../api/endpoints';
import { ArrowLeft, Navigation, ShieldCheck, Clock, MapPin } from 'lucide-react';

export const LiveTrackingPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: shipment, isLoading, error, refetch } = useQuery({
    queryKey: ['shipment-detail', id],
    queryFn: async () => {
      const res = await apiClient.get(API_ENDPOINTS.SHIPMENT_DETAIL(id));
      return res.data?.data || res.data;
    },
  });

  const { latestTracking, trackingHistory, isConnected, loading: trackingLoading } = useShipmentTracking(id);

  if (isLoading) return <LoadingSpinner label="Initializing live GPS stream..." />;
  if (error || !shipment) return <ErrorMessage title="Shipment Not Found" message={error?.message || 'Specified shipment does not exist.'} onRetry={refetch} />;

  const load = shipment.load_data || shipment.load_detail || {};
  const origin = shipment.origin_city || load.origin_city || 'Djibouti Port';
  const destination = shipment.destination_city || load.destination_city || 'Modjo Dry Port';

  return (
    <div className="space-y-6">
      <PageHeader
        title="Real-Time GPS Live Telemetry & Tracking"
        subtitle={`Live Corridor Telemetry for Shipment #${id.substring(0, 8)}`}
        actions={
          <button
            onClick={() => navigate(`/shipments/${id}`)}
            className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold flex items-center space-x-1 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Shipment Overview</span>
          </button>
        }
      />

      <ETAInfoCard latestTracking={latestTracking} />

      <ShipmentMap
        latestTracking={latestTracking}
        origin={origin}
        destination={destination}
        isConnected={isConnected}
      />

      {/* Telemetry History Feed */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
        <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-1.5">
          <Clock className="w-4 h-4 text-cyan-400" />
          <span>Recent Telemetry Ping Stream ({trackingHistory.length})</span>
        </h4>

        {trackingHistory.length === 0 ? (
          <p className="text-xs text-slate-500 italic py-2">Awaiting initial GPS location ping broadcast...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-2 px-3 font-semibold">Timestamp</th>
                  <th className="py-2 px-3 font-semibold">Latitude</th>
                  <th className="py-2 px-3 font-semibold">Longitude</th>
                  <th className="py-2 px-3 font-semibold">Speed</th>
                  <th className="py-2 px-3 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
                {trackingHistory.slice(0, 10).map((pt, idx) => (
                  <tr key={idx} className="hover:bg-slate-900/40 text-slate-300">
                    <td className="py-2 px-3">{pt.timestamp ? new Date(pt.timestamp).toLocaleTimeString() : 'Just now'}</td>
                    <td className="py-2 px-3 text-cyan-400">{Number(pt.latitude).toFixed(5)}°</td>
                    <td className="py-2 px-3 text-cyan-400">{Number(pt.longitude).toFixed(5)}°</td>
                    <td className="py-2 px-3 text-amber-400">{pt.speed ? `${Number(pt.speed).toFixed(0)} km/h` : '0 km/h'}</td>
                    <td className="py-2 px-3">
                      <span className="text-emerald-400 font-sans font-semibold">Broadcasting</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
