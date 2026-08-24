import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { PageHeader } from '../../components/common/PageHeader';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import apiClient from '../../api/axios';
import { API_ENDPOINTS } from '../../api/endpoints';
import { DollarSign, ArrowRight, ShieldCheck, CreditCard, AlertTriangle, CheckCircle2, Clock } from 'lucide-react';

export const PaymentsPage = () => {
  const navigate = useNavigate();

  const { data: paymentsData, isLoading, error, refetch } = useQuery({
    queryKey: ['payments'],
    queryFn: async () => {
      const res = await apiClient.get(API_ENDPOINTS.PAYMENTS);
      return res.data?.data || res.data;
    },
  });

  const paymentsList = Array.isArray(paymentsData) ? paymentsData : paymentsData?.results || [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Payments, Settlements & Payouts Engine"
        subtitle="Manage freight escrow payments, automated platform commission calculations, and transporter payouts."
        actions={
          <button
            onClick={() => navigate('/payments/disputes')}
            className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition"
          >
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>Disputes Portal</span>
          </button>
        }
      />

      {isLoading ? (
        <LoadingSpinner label="Fetching financial ledger..." />
      ) : error ? (
        <ErrorMessage title="Payments API Error" message={error.message} onRetry={refetch} />
      ) : paymentsList.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800 space-y-4 max-w-md mx-auto my-8">
          <CreditCard className="w-12 h-12 text-cyan-400 mx-auto" />
          <h3 className="text-base font-bold text-white">No payment transactions recorded</h3>
          <p className="text-xs text-slate-400">
            Escrow payments are created automatically when a load booking is confirmed.
          </p>
        </div>
      ) : (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <DollarSign className="w-4 h-4 text-emerald-400" />
            <span>Recent Payment Escrow Transactions ({paymentsList.length})</span>
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-2.5 px-3 font-semibold">Payment Ref</th>
                  <th className="py-2.5 px-3 font-semibold">Amount (ETB)</th>
                  <th className="py-2.5 px-3 font-semibold">Platform Fee</th>
                  <th className="py-2.5 px-3 font-semibold">Status</th>
                  <th className="py-2.5 px-3 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {paymentsList.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-900/40 text-slate-300">
                    <td className="py-3 px-3 font-mono font-bold text-cyan-400">#{p.id?.substring(0, 8)}</td>
                    <td className="py-3 px-3 font-black text-white">{Number(p.amount).toLocaleString()} ETB</td>
                    <td className="py-3 px-3 text-slate-400">{p.platform_commission ? `${Number(p.platform_commission).toLocaleString()} ETB` : '5% Standard'}</td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold rounded-full">
                        {p.status || 'CONFIRMED'}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => navigate(`/payments/${p.id}`)}
                        className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold inline-flex items-center space-x-1"
                      >
                        <span>Details</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
