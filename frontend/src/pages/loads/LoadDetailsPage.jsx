import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import { PageHeader } from '../../components/common/PageHeader';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { LoadSummary } from '../../components/loads/LoadSummary';
import apiClient from '../../api/axios';
import { API_ENDPOINTS } from '../../api/endpoints';
import { ArrowLeft, Edit, Globe, XCircle, DollarSign, AlertCircle, CheckCircle2 } from 'lucide-react';

export const LoadDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [actionError, setActionError] = useState('');

  const { data: load, isLoading, error, refetch } = useQuery({
    queryKey: ['load-detail', id],
    queryFn: async () => {
      const res = await apiClient.get(`${API_ENDPOINTS.LOADS}${id}/`);
      return res.data?.data || res.data;
    },
  });

  const isOwner = load && (load.shipper === user?.id || load.shipper_email === user?.email);
  const isTransporter = user?.role === 'TRANSPORTER';

  const postMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post(`${API_ENDPOINTS.LOADS}${id}/post/`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['load-detail', id]);
      queryClient.invalidateQueries(['loads']);
    },
    onError: (err) => {
      setActionError(err.response?.data?.detail || 'Failed to post load.');
    },
  });

  const cancelMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post(`${API_ENDPOINTS.LOADS}${id}/cancel/`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['load-detail', id]);
      queryClient.invalidateQueries(['loads']);
    },
    onError: (err) => {
      setActionError(err.response?.data?.detail || 'Failed to cancel load.');
    },
  });

  if (isLoading) return <LoadingSpinner label="Loading load specifications..." />;
  if (error || !load) return <ErrorMessage title="Load Not Found" message={error?.message || 'Specified load listing does not exist.'} onRetry={refetch} />;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <PageHeader
        title={`Freight Load Details`}
        subtitle={`Listing #${load.id?.substring(0, 8)}`}
        actions={
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigate('/loads')}
              className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold flex items-center space-x-1 transition"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Loads</span>
            </button>

            {isOwner && load.status === 'DRAFT' && (
              <button
                onClick={() => postMutation.mutate()}
                disabled={postMutation.isPending}
                className="px-3.5 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition shadow-lg shadow-cyan-500/20"
              >
                <Globe className="w-4 h-4" />
                <span>Publish to Marketplace</span>
              </button>
            )}

            {isOwner && ['DRAFT', 'POSTED'].includes(load.status) && (
              <button
                onClick={() => navigate(`/loads/${id}/edit`)}
                className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition"
              >
                <Edit className="w-4 h-4" />
                <span>Edit Load</span>
              </button>
            )}

            {isOwner && ['DRAFT', 'POSTED'].includes(load.status) && (
              <button
                onClick={() => cancelMutation.mutate()}
                disabled={cancelMutation.isPending}
                className="px-3.5 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition"
              >
                <XCircle className="w-4 h-4" />
                <span>Cancel Load</span>
              </button>
            )}
          </div>
        }
      />

      {actionError && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs rounded-xl flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{actionError}</span>
        </div>
      )}

      <LoadSummary load={load} />

      {/* Transporter Bidding Preparation Section (Phase 23.6 Placeholder) */}
      {isTransporter && load.status === 'POSTED' && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div>
            <h4 className="text-sm font-bold text-white flex items-center space-x-2">
              <DollarSign className="w-4 h-4 text-cyan-400" />
              <span>Transporter Bidding Portal</span>
            </h4>
            <p className="text-xs text-slate-400 mt-1">
              Interested in carrying this freight? Submit a competitive rate bid on the Ethiopian TradeFlow marketplace.
            </p>
          </div>
          <button
            onClick={() => navigate('/bids')}
            className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-xl text-xs font-semibold flex items-center space-x-1.5 shadow-lg shadow-cyan-500/20 transition shrink-0"
          >
            <span>Submit Bid</span>
          </button>
        </div>
      )}
    </div>
  );
};

