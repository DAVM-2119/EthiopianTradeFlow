import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { PageHeader } from '../../components/common/PageHeader';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import apiClient from '../../api/axios';
import { API_ENDPOINTS } from '../../api/endpoints';
import { ArrowLeft, DollarSign, CheckCircle2, ShieldCheck, AlertCircle, CreditCard } from 'lucide-react';

export const PaymentDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [actionError, setActionError] = useState('');

  const { data: payment, isLoading, error, refetch } = useQuery({
    queryKey: ['payment-detail', id],
    queryFn: async () => {
      const res = await apiClient.get(API_ENDPOINTS.PAYMENT_DETAIL(id));
      return res.data?.data || res.data;
    },
  });

  const initiateMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post(API_ENDPOINTS.PAYMENT_INITIATE(id));
      return res.data;
    },
    onSuccess: () => {
      setActionError('');
      queryClient.invalidateQueries(['payment-detail', id]);
    },
    onError: (err) => {
      setActionError(err.response?.data?.detail || 'Failed to initiate payment.');
    },
  });

  const confirmMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post(API_ENDPOINTS.PAYMENT_CONFIRM(id));
      return res.data;
    },
    onSuccess: () => {
      setActionError('');
      queryClient.invalidateQueries(['payment-detail', id]);
    },
    onError: (err) => {
      setActionError(err.response?.data?.detail || 'Failed to confirm payment.');
    },
  });

  if (isLoading) return <LoadingSpinner label="Fetching payment transaction record..." />;
  if (error || !payment) return <ErrorMessage title="Payment Not Found" message={error?.message || 'Specified transaction record does not exist.'} onRetry={refetch} />;

  const formattedAmount = Number(payment.amount).toLocaleString('en-US', { minimumFractionDigits: 2 });

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <PageHeader
        title={`Payment Transaction Ledger`}
        subtitle={`Transaction Ref #${payment.id?.substring(0, 8)}`}
        actions={
          <button
            onClick={() => navigate('/payments')}
            className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold flex items-center space-x-1 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Payments</span>
          </button>
        }
      />

      {actionError && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs rounded-xl flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{actionError}</span>
        </div>
      )}

      <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800 space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div>
            <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-widest">Escrow Payment Transaction</span>
            <h2 className="text-3xl font-black text-emerald-400 mt-1">
              {formattedAmount} <span className="text-sm text-emerald-500">{payment.currency || 'ETB'}</span>
            </h2>
          </div>
          <span className="px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-bold rounded-full">
            {payment.status || 'CONFIRMED'}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 space-y-1">
            <span className="text-slate-500 font-semibold uppercase text-[10px]">Payment Provider Engine</span>
            <p className="text-sm font-bold text-white flex items-center space-x-1.5">
              <CreditCard className="w-4 h-4 text-cyan-400" />
              <span>{payment.provider || 'TeleBirr / Commercial Escrow'}</span>
            </p>
          </div>

          <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 space-y-1">
            <span className="text-slate-500 font-semibold uppercase text-[10px]">Transaction Reference ID</span>
            <p className="text-sm font-bold text-slate-200 font-mono">{payment.provider_reference || payment.id?.substring(0, 12)}</p>
          </div>
        </div>

        {payment.status === 'PENDING' && (
          <div className="pt-4 border-t border-slate-800 flex justify-end space-x-3">
            <button
              onClick={() => initiateMutation.mutate()}
              disabled={initiateMutation.isPending}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-cyan-600/20 transition"
            >
              Initiate Settlement
            </button>
            <button
              onClick={() => confirmMutation.mutate()}
              disabled={confirmMutation.isPending}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-emerald-600/20 transition"
            >
              Confirm Release
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
