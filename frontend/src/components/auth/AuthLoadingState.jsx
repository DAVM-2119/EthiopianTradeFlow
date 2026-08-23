import React from 'react';
import { Truck } from 'lucide-react';

export const AuthLoadingState = () => {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6 text-center">
      <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-xl shadow-cyan-500/20 mb-4 animate-bounce">
        <Truck className="w-9 h-9 text-white" />
      </div>
      <h2 className="text-xl font-extrabold text-white tracking-wide">TradeFlow Ethiopia</h2>
      <p className="text-xs text-cyan-400 font-semibold mt-1 animate-pulse">
        Authenticating session & establishing secure corridor connection...
      </p>
    </div>
  );
};
