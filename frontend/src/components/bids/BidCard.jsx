import React from 'react';
import { useNavigate } from 'react-router-dom';
import { BidStatusBadge } from './BidStatusBadge';
import { DollarSign, Calendar, MessageSquare, ArrowRight, UserCheck } from 'lucide-react';

export const BidCard = ({ bid, isShipper, onAccept, onWithdraw }) => {
  const navigate = useNavigate();

  const formattedAmount = Number(bid.amount).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  const formattedDate = bid.created_at
    ? new Date(bid.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    : 'Recent';

  return (
    <div className="glass-card p-5 rounded-2xl border border-slate-800 hover:border-cyan-500/30 transition flex flex-col justify-between space-y-4">
      <div>
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center space-x-1.5 text-xs text-slate-300 font-semibold truncate">
            <UserCheck className="w-4 h-4 text-cyan-400 shrink-0" />
            <span className="truncate">{bid.transporter_email || 'Transporter'}</span>
          </div>
          <BidStatusBadge status={bid.status} />
        </div>

        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 mb-3 flex items-center justify-between">
          <span className="text-xs text-slate-400 font-medium">Offered Rate</span>
          <span className="text-lg font-black text-emerald-400">
            {formattedAmount} <span className="text-xs text-emerald-500/80">{bid.currency || 'ETB'}</span>
          </span>
        </div>

        <div className="space-y-2 text-xs text-slate-400">
          {bid.proposed_pickup_date && (
            <div className="flex items-center space-x-1.5">
              <Calendar className="w-3.5 h-3.5 text-slate-500 shrink-0" />
              <span>Pickup: {new Date(bid.proposed_pickup_date).toLocaleDateString()}</span>
            </div>
          )}

          {bid.message && (
            <div className="flex items-start space-x-1.5 pt-1">
              <MessageSquare className="w-3.5 h-3.5 text-slate-500 shrink-0 mt-0.5" />
              <p className="text-[11px] text-slate-300 line-clamp-2 italic">"{bid.message}"</p>
            </div>
          )}
        </div>
      </div>

      <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
        <span className="text-[10px] text-slate-500">Submitted {formattedDate}</span>

        <div className="flex items-center space-x-2">
          {isShipper && bid.status === 'ACTIVE' && (
            <button
              onClick={() => onAccept && onAccept(bid)}
              className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-emerald-600/20 transition"
            >
              Accept Bid
            </button>
          )}

          {!isShipper && bid.status === 'ACTIVE' && onWithdraw && (
            <button
              onClick={() => onWithdraw(bid)}
              className="px-2.5 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 rounded-xl text-xs font-semibold transition"
            >
              Withdraw
            </button>
          )}

          <button
            onClick={() => navigate(`/bids/${bid.id}`)}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold flex items-center space-x-1 transition"
          >
            <span>Details</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
