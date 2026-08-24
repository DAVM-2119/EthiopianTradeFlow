import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { PageHeader } from '../../components/common/PageHeader';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { ShipmentCard } from '../../components/shipments/ShipmentCard';
import apiClient from '../../api/axios';
import { API_ENDPOINTS } from '../../api/endpoints';
import { Filter, RotateCcw, Package } from 'lucide-react';

export const ShipmentsPage = () => {
  const [statusFilter, setStatusFilter] = useState('');

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['shipments', statusFilter],
    queryFn: async () => {
      const params = statusFilter ? { status: statusFilter } : {};
      const res = await apiClient.get(API_ENDPOINTS.SHIPMENTS, { params });
      return res.data?.data || res.data;
    },
  });

  const shipmentsList = Array.isArray(data) ? data : data?.results || [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Shipments Management"
        subtitle="Monitor active freight movements, transport assignments, and milestone tracking."
      />

      <div className="glass-panel p-3 sm:p-4 rounded-xl border border-slate-800 flex items-center justify-between gap-3 text-xs">
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-cyan-400 shrink-0" />
          <span className="text-slate-400 font-semibold hidden sm:inline">Filter Status:</span>
          <div className="flex flex-wrap gap-1.5">
            {['', 'BOOKED', 'ASSIGNED', 'IN_TRANSIT', 'CUSTOMS_PROCESSING', 'DELIVERED', 'COMPLETED'].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1 rounded-lg font-semibold transition ${
                  statusFilter === st
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                    : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-white'
                }`}
              >
                {st === '' ? 'All Statuses' : st.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        {statusFilter && (
          <button
            onClick={() => setStatusFilter('')}
            className="text-slate-500 hover:text-slate-300 flex items-center space-x-1"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Reset</span>
          </button>
        )}
      </div>

      {isLoading ? (
        <LoadingSpinner label="Fetching shipments list..." />
      ) : error ? (
        <ErrorMessage title="Shipments API Error" message={error.message} onRetry={refetch} />
      ) : shipmentsList.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800 space-y-3 max-w-md mx-auto my-8">
          <Package className="w-10 h-10 text-cyan-400 mx-auto" />
          <h3 className="text-base font-bold text-white">No active shipments found</h3>
          <p className="text-xs text-slate-400">
            {statusFilter ? 'No shipments match the selected status filter.' : 'Shipments are created automatically when a transporter bid is accepted.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {shipmentsList.map((shipment) => (
            <ShipmentCard key={shipment.id} shipment={shipment} />
          ))}
        </div>
      )}
    </div>
  );
};
