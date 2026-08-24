import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { PageHeader } from '../../components/common/PageHeader';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import apiClient from '../../api/axios';
import { API_ENDPOINTS } from '../../api/endpoints';
import { AlertTriangle, Plus, CheckCircle2, ShieldCheck, FileText, ArrowLeft, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const disputeSchema = z.object({
  dispute_type: z.string().min(1, 'Dispute category type is required'),
  reason: z.string().min(10, 'Reason description must be at least 10 characters'),
  claimed_amount: z.coerce.number().optional(),
});

export const DisputesPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [submitError, setSubmitError] = useState('');

  const { data: disputesData, isLoading, error, refetch } = useQuery({
    queryKey: ['disputes'],
    queryFn: async () => {
      const res = await apiClient.get(API_ENDPOINTS.DISPUTES);
      return res.data?.data || res.data;
    },
  });

  const disputesList = Array.isArray(disputesData) ? disputesData : disputesData?.results || [];

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(disputeSchema),
    defaultValues: {
      dispute_type: 'CARGO_DAMAGE',
      reason: '',
      claimed_amount: '',
    },
  });

  const createDisputeMutation = useMutation({
    mutationFn: async (payload) => {
      const res = await apiClient.post(API_ENDPOINTS.DISPUTES, payload);
      return res.data;
    },
    onSuccess: () => {
      setShowCreateModal(false);
      reset();
      queryClient.invalidateQueries(['disputes']);
    },
    onError: (err) => {
      setSubmitError(err.response?.data?.detail || 'Failed to file dispute claim.');
    },
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dispute Resolution Escrow Claims"
        subtitle="File and track cargo damage, delay penalties, and freight pricing claims."
        actions={
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigate('/payments')}
              className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold flex items-center space-x-1 transition"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Payments</span>
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-gradient-to-r from-rose-600 to-amber-600 hover:from-rose-500 hover:to-amber-500 text-white rounded-xl text-xs font-semibold flex items-center space-x-1.5 shadow-lg shadow-rose-600/20 transition"
            >
              <Plus className="w-4 h-4" />
              <span>File New Dispute</span>
            </button>
          </div>
        }
      />

      {isLoading ? (
        <LoadingSpinner label="Fetching dispute cases..." />
      ) : error ? (
        <ErrorMessage title="Disputes API Error" message={error.message} onRetry={refetch} />
      ) : disputesList.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800 space-y-4 max-w-md mx-auto my-8">
          <ShieldCheck className="w-12 h-12 text-emerald-400 mx-auto" />
          <h3 className="text-base font-bold text-white">No active dispute claims</h3>
          <p className="text-xs text-slate-400">
            TradeFlow automated escrow protection guarantees 100% dispute resolution audit trail.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {disputesList.map((d) => (
            <div key={d.id} className="glass-card p-5 rounded-2xl border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-rose-400 uppercase">{d.dispute_type || 'CARGO DISPUTE'}</span>
                <span className="px-2 py-0.5 bg-amber-500/10 text-amber-400 border border-amber-500/20 text-[10px] font-bold rounded-full">
                  {d.status || 'OPEN'}
                </span>
              </div>
              <p className="text-xs text-slate-300 line-clamp-2 italic">"{d.reason}"</p>
              <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-500 flex justify-between">
                <span>Ref #{d.id?.substring(0, 8)}</span>
                <span>Filed {new Date(d.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
          <div className="glass-panel max-w-md w-full p-6 rounded-2xl border border-slate-800 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2 text-rose-400">
                <AlertTriangle className="w-5 h-5" />
                <h3 className="text-base font-bold text-white">File Dispute Claim</h3>
              </div>
              <button onClick={() => setShowCreateModal(false)} className="text-slate-500 hover:text-slate-300 transition">
                <X className="w-4 h-4" />
              </button>
            </div>

            {submitError && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs rounded-xl flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                <span>{submitError}</span>
              </div>
            )}

            <form onSubmit={handleSubmit((d) => createDisputeMutation.mutate(d))} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Dispute Category</label>
                <select
                  {...register('dispute_type')}
                  className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-cyan-500 transition"
                >
                  <option value="CARGO_DAMAGE">Cargo Damage / Loss</option>
                  <option value="DELIVERY_DELAY">Delivery Delay Penalty</option>
                  <option value="PAYMENT_DISPUTE">Escrow Payment Mismatch</option>
                  <option value="DOCUMENTATION_ISSUE">Customs Documentation Issue</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Detailed Explanation & Claims Basis</label>
                <textarea
                  rows={3}
                  {...register('reason')}
                  placeholder="Describe cargo condition or payment discrepancy..."
                  className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-cyan-500 transition"
                />
                {errors.reason && <p className="text-[11px] text-rose-400 mt-1">{errors.reason.message}</p>}
              </div>

              <div className="pt-2 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs rounded-xl transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createDisputeMutation.isPending}
                  className="px-5 py-2 bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-rose-600/20 transition flex items-center space-x-2"
                >
                  {createDisputeMutation.isPending ? (
                    <span className="animate-pulse">Filing...</span>
                  ) : (
                    <>
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Submit Claim</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
