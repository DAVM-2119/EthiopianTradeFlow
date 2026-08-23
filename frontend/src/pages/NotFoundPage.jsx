import React from 'react';
import { Link } from 'react-router-dom';
import { Truck, Home } from 'lucide-react';

export const NotFoundPage = () => {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6 text-center">
      <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center mb-4">
        <Truck className="w-10 h-10" />
      </div>
      <h1 className="text-4xl font-extrabold text-white">404 — Page Not Found</h1>
      <p className="text-sm text-slate-400 mt-2 max-w-md">
        The requested route does not exist or has been relocated along the TradeFlow freight network.
      </p>
      <Link
        to="/dashboard"
        className="mt-6 px-5 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold text-xs rounded-xl shadow-lg shadow-cyan-500/25 flex items-center space-x-2"
      >
        <Home className="w-4 h-4" />
        <span>Return to Dashboard</span>
      </Link>
    </div>
  );
};
