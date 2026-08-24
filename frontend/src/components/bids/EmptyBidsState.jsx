import React from 'react';
import { DollarSign, Globe } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const EmptyBidsState = ({ isTransporter, message }) => {
  const navigate = useNavigate();

  return (
    <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800 space-y-4 max-w-md mx-auto my-8">
      <div className="w-16 h-16 rounded-2xl bg-slate-900 border border-slate-800 text-emerald-400 flex items-center justify-center mx-auto">
        <DollarSign className="w-8 h-8" />
      </div>
      <div>
        <h3 className="text-base font-bold text-white">No bids recorded</h3>
        <p className="text-xs text-slate-400 mt-1">
          {message || 'No bids submitted or received matching your current criteria.'}
        </p>
      </div>

      {isTransporter && (
        <div className="pt-2">
          <button
            onClick={() => navigate('/marketplace')}
            className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-xl text-xs font-semibold flex items-center space-x-1.5 shadow-lg shadow-cyan-500/20 transition mx-auto"
          >
            <Globe className="w-4 h-4" />
            <span>Browse Freight Marketplace</span>
          </button>
        </div>
      )}
    </div>
  );
};
