import React from 'react';
import { AlertCircle } from 'lucide-react';

export const ErrorMessage = ({ title = 'An error occurred', message, onRetry }) => {
  return (
    <div className="glass-card p-5 border-l-4 border-rose-500 rounded-lg flex items-start space-x-4 my-4">
      <AlertCircle className="w-6 h-6 text-rose-400 shrink-0 mt-0.5" />
      <div className="flex-1">
        <h4 className="text-sm font-semibold text-rose-300">{title}</h4>
        <p className="text-sm text-slate-300 mt-1">{message || 'Unable to complete the requested operational action.'}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-3 px-3 py-1.5 bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 rounded text-xs font-semibold transition"
          >
            Retry Request
          </button>
        )}
      </div>
    </div>
  );
};
