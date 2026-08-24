import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import { PageHeader } from '../../components/common/PageHeader';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { ShipmentStatusBadge } from '../../components/shipments/ShipmentStatusBadge';
import { ShipmentTimeline } from '../../components/shipments/ShipmentTimeline';
import { ETAInfoCard } from '../../components/tracking/ETAInfoCard';
import apiClient from '../../api/axios';
import { API_ENDPOINTS } from '../../api/endpoints';
import { ArrowLeft, Truck, UserCheck, MapPin, Navigation, ShieldCheck, CheckCircle2, AlertCircle, FileText } from 'lucide-react';

export const ShipmentDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [selectedStatus, setSelectedStatus] = useState('');
  const [actionError, setActionError] = useState('');

  const { data: shipment, isLoading, error, refetch } = useQuery({
    queryKey: ['shipment-detail', id],
    queryFn: async () => {
      const res = await apiClient.get(API_ENDPOINTS.SHIPMENT_DETAIL(id));
      return res.data?.data || res.data;
    },
  });

  const { data: eventsData } = useQuery({
    queryKey: ['shipment-events', id],
    queryFn: async () => {
      const res = await apiClient.get(API_ENDPOINTS.SHIPMENT_EVENTS(id));
      return res.data?.data || res.data;
    },
    enabled: !!shipment,
  });

  const transitionMutation = useMutation({
    mutationFn: async (targetStatus) => {
      const res = await apiClient.post(API_ENDPOINTS.SHIPMENT_TRANSITION(id), { status: targetStatus });
      return res.data;
    },
    onSuccess: () => {
      setActionError('');
      queryClient.invalidateQueries(['shipment-detail', id]);
      queryClient.invalidateQueries(['shipments']);
    },
    onError: (err) => {
      setActionError(err.response?.data?.detail || 'Failed to update shipment status.');
    },
  });

  if (isLoading) return <LoadingSpinner label="Loading shipment overview..." />;
  if (error || !shipment) return <ErrorMessage title="Shipment Not Found" message={error?.message || 'Specified shipment does not exist.'} onRetry={refetch} />;

  const load = shipment.load_data || shipment.load_detail || {};
  const isTransporter = user?.role === 'TRANSPORTER';
  const isDriver = user?.role === 'DRIVER';

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <PageHeader
        title={`Shipment Overview`}
        subtitle={`Reference #${shipment.id?.substring(0, 8)}`}
        actions={
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigate('/shipments')}
              className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold flex items-center space-x-1 transition"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>

            <button
              onClick={() => navigate(`/tracking/${shipment.id}`)}
              className="px-3 py-1.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-xl text-xs font-semibold flex items-center space-x-1 shadow-lg shadow-cyan-500/20 transition"
            >
              <Navigation className="w-4 h-4" />
              <span>Live GPS Map</span>
            </button>
          </div>
        }
      />

      {actionError && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs rounded-xl flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{actionError}</span>
        </div>
      )}

      {/* Header Info Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <h2 className="text-xl font-bold text-white">
              {shipment.origin_city || load.origin_city || 'Djibouti Port'} ➔ {shipment.destination_city || load.destination_city || 'Modjo Dry Port'}
            </h2>
          </div>
          <p className="text-xs text-slate-400">
            Cargo: <strong className="text-cyan-300">{shipment.cargo_type || load.cargo_type || 'General Cargo'}</strong> | Weight: {shipment.weight || load.weight || '30.0'} Tons
          </p>
        </div>

        <ShipmentStatusBadge status={shipment.status} />
      </div>

      {/* Milestone Lifecycle Timeline */}
      <ShipmentTimeline currentStatus={shipment.status} events={Array.isArray(eventsData) ? eventsData : []} />

      {/* Status Transition Control (for Transporters/Drivers/Admins) */}
      {['BOOKED', 'ASSIGNED', 'PICKUP_READY', 'IN_TRANSIT', 'CUSTOMS_PROCESSING', 'CUSTOMS_CLEARED', 'DELIVERED'].includes(shipment.status) && (
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
          <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-1.5">
            <CheckCircle2 className="w-4 h-4 text-cyan-400" />
            <span>Update Shipment Status Transition</span>
          </h4>

          <div className="flex flex-wrap items-center gap-2 pt-1">
            {['ASSIGNED', 'PICKUP_READY', 'IN_TRANSIT', 'CUSTOMS_PROCESSING', 'CUSTOMS_CLEARED', 'DELIVERED', 'COMPLETED'].map((st) => (
              <button
                key={st}
                onClick={() => transitionMutation.mutate(st)}
                disabled={transitionMutation.isPending || shipment.status === st}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                  shipment.status === st
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 cursor-default'
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
                }`}
              >
                {st.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Predictive ETA Widget */}
      <ETAInfoCard latestTracking={shipment.latest_tracking} />
    </div>
  );
};
