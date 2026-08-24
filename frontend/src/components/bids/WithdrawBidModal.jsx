import React from 'react';
import { RotateCcw, AlertTriangle, X } from 'lucide-react';

export const WithdrawBidModal = ({ bid, onConfirm, onCancel, submitting, error }) => {
  if (!bid) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="glass-panel max-w-md w-full p-6 rounded-2xl border border-slate-800 space-y-5 shadow-2xl">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2 text-rose-400">
            <AlertTriangle className="w-5 h-5" />
            <h3 className="text-base font-bold text-white">Withdraw Rate Offer</h3>
          </div>
          <button onClick={onCancel} className="text-slate-500 hover:text-slate-300 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        {error && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs rounded-xl flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <p className="text-xs text-slate-300 leading-relaxed">
          Are you sure you want to withdraw your bid offer of <strong className="text-white">{Number(bid.amount).toLocaleString()} ETB</strong>?
          This action will mark your bid as <strong className="text-amber-400">WITHDRAWN</strong> and remove it from shipper evaluation.
        </p>

        <div className="flex justify-end space-x-3 pt-2">
          <button
            onClick={onCancel}
            disabled={submitting}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs rounded-xl transition"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={submitting}
            className="px-5 py-2 bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-rose-600/20 transition flex items-center space-x-1.5"
          >
            {submitting ? (
              <span className="animate-pulse">Withdrawing...</span>
            ) : (
              <>
                <RotateCcw className="w-4 h-4" />
                <span>Confirm Withdrawal</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
