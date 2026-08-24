import React from 'react';
import { BidStatusBadge } from './BidStatusBadge';
import { DollarSign, Calendar, UserCheck, CheckCircle2, Award, ShieldCheck } from 'lucide-react';

export const BidComparison = ({ bids = [], onAcceptBid }) => {
  if (!bids || bids.length === 0) return null;

  // Find lowest bid amount
  const lowestAmount = Math.min(...bids.map((b) => Number(b.amount) || Infinity));

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Award className="w-4 h-4 text-cyan-400" />
            <span>Transporter Bid Comparison Matrix</span>
          </h3>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Evaluate price offer, proposed timeline, and reliability metrics side-by-side.
          </p>
        </div>
        <span className="text-xs font-semibold text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/20">
          {bids.length} Active {bids.length === 1 ? 'Bid' : 'Bids'}
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400">
              <th className="py-2.5 px-3 font-semibold">Transporter</th>
              <th className="py-2.5 px-3 font-semibold">Bid Amount (ETB)</th>
              <th className="py-2.5 px-3 font-semibold">Proposed Pickup</th>
              <th className="py-2.5 px-3 font-semibold">Estimated Delivery</th>
              <th className="py-2.5 px-3 font-semibold">Status</th>
              <th className="py-2.5 px-3 font-semibold text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {bids.map((bid) => {
              const amount = Number(bid.amount);
              const isLowest = amount === lowestAmount && bids.length > 1;

              return (
                <tr key={bid.id} className="hover:bg-slate-900/40 transition">
                  <td className="py-3 px-3">
                    <div className="flex items-center space-x-2">
                      <div className="w-7 h-7 rounded-lg bg-slate-800 flex items-center justify-center text-cyan-400 shrink-0 font-bold text-xs">
                        {bid.transporter_email?.charAt(0).toUpperCase() || 'T'}
                      </div>
                      <div>
                        <p className="font-semibold text-slate-200">{bid.transporter_email || 'Transporter'}</p>
                        <span className="text-[10px] text-emerald-400 flex items-center space-x-0.5">
                          <ShieldCheck className="w-3 h-3 inline" />
                          <span>Verified Carrier</span>
                        </span>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-3">
                    <div className="flex items-center space-x-1.5">
                      <span className="font-black text-white text-sm">
                        {amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                      </span>
                      {isLowest && (
                        <span className="px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 text-[10px] font-bold rounded border border-emerald-500/20">
                          Lowest Rate
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-3 text-slate-300">
                    {bid.proposed_pickup_date ? new Date(bid.proposed_pickup_date).toLocaleDateString() : 'Immediate'}
                  </td>
                  <td className="py-3 px-3 text-slate-300">
                    {bid.estimated_delivery_date ? new Date(bid.estimated_delivery_date).toLocaleDateString() : 'Standard'}
                  </td>
                  <td className="py-3 px-3">
                    <BidStatusBadge status={bid.status} />
                  </td>
                  <td className="py-3 px-3 text-right">
                    {bid.status === 'ACTIVE' && (
                      <button
                        onClick={() => onAcceptBid(bid)}
                        className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-emerald-600/20 transition inline-flex items-center space-x-1"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Accept</span>
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
