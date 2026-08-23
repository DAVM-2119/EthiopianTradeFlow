import React from 'react';
import { PackageSearch, Plus, RotateCcw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const EmptyLoadsState = ({ isShipper, onResetFilters }) => {
  const navigate = useNavigate();

  return (
    <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800 space-y-4 max-w-md mx-auto my-8">
      <div className="w-16 h-16 rounded-2xl bg-slate-900 border border-slate-800 text-cyan-400 flex items-center justify-center mx-auto">
        <PackageSearch className="w-8 h-8" />
      </div>
      <div>
        <h3 className="text-base font-bold text-white">No loads found</h3>
        <p className="text-xs text-slate-400 mt-1">
          There are no freight loads matching your current search parameters or marketplace criteria.
        </p>
      </div>

      <div className="flex items-center justify-center space-x-3 pt-2">
        {onResetFilters && (
          <button
            onClick={onResetFilters}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Reset Filters</span>
          </button>
        )}

        {isShipper && (
          <button
            onClick={() => navigate('/loads/create')}
            className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-xl text-xs font-semibold flex items-center space-x-1.5 shadow-lg shadow-cyan-500/20 transition"
          >
            <Plus className="w-4 h-4" />
            <span>Post New Load</span>
          </button>
        )}
      </div>
    </div>
  );
};
