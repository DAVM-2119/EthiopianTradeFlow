import React from 'react';
import { CheckCircle2, AlertCircle, DollarSign, UserCheck, MapPin, X } from 'lucide-react';

export const AcceptBidModal = ({ bid, load, onConfirm, onCancel, submitting, error }) => {
  if (!bid) return null;

  const formattedAmount = Number(bid.amount).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="glass-panel max-w-md w-full p-6 rounded-2xl border border-slate-800 space-y-5 shadow-2xl">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2 text-emerald-400">
            <CheckCircle2 className="w-5 h-5" />
            <h3 className="text-base font-bold text-white">Confirm Freight Booking</h3>
          </div>
          <button onClick={onCancel} className="text-slate-500 hover:text-slate-300 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        {error && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs rounded-xl flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="space-y-3 text-xs">
          <p className="text-slate-300 leading-relaxed">
            Are you sure you want to accept this transporter bid? Accepting will transition load status to <strong className="text-emerald-400 font-bold">BOOKED</strong> and reject other competing bids.
          </p>

          <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Transporter:</span>
              <span className="font-bold text-slate-200 flex items-center space-x-1">
                <UserCheck className="w-3.5 h-3.5 text-cyan-400" />
                <span>{bid.transporter_email}</span>
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-slate-400">Agreed Rate:</span>
              <span className="font-black text-emerald-400 text-sm">
                {formattedAmount} {bid.currency || 'ETB'}
              </span>
            </div>

            {load && (
              <div className="flex justify-between items-center pt-2 border-t border-slate-800/60">
                <span className="text-slate-400">Route Corridor:</span>
                <span className="font-semibold text-slate-300 flex items-center space-x-1">
                  <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                  <span>{load.origin_city} ➔ {load.destination_city}</span>
                </span>
              </div>
            )}
          </div>
        </div>

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
            className="px-5 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-emerald-600/20 transition flex items-center space-x-1.5"
          >
            {submitting ? (
              <span className="animate-pulse">Confirming Booking...</span>
            ) : (
              <>
                <CheckCircle2 className="w-4 h-4" />
                <span>Confirm Acceptance & Book</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

