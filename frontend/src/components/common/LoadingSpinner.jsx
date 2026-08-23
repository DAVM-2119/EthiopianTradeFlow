import React from 'react';

export const LoadingSpinner = ({ size = 'md', label = 'Loading TradeFlow data...' }) => {
  const sizeClasses = {
    sm: 'w-5 h-5 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  };

  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-3">
      <div className={`animate-spin rounded-full border-cyan-500 border-t-transparent ${sizeClasses[size]}`} />
      {label && <p className="text-sm font-medium text-slate-400 animate-pulse">{label}</p>}
    </div>
  );
};
