import React, { useState, useEffect } from 'react';
import { WifiOff, RefreshCw } from 'lucide-react';

export const OfflineState = () => {
  const [isOffline, setIsOffline] = useState(!navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!isOffline) return null;

  return (
    <div className="bg-gradient-to-r from-amber-600/90 to-rose-600/90 text-white px-4 py-2.5 shadow-lg flex items-center justify-between text-xs border-b border-amber-500/30 sticky top-16 z-20">
      <div className="flex items-center space-x-2">
        <WifiOff className="w-4 h-4 text-amber-200 animate-pulse shrink-0" />
        <span className="font-semibold">
          Intermittent Corridor Connectivity Detected: TradeFlow is operating in Offline Cache Mode.
        </span>
      </div>
      <button
        onClick={() => window.location.reload()}
        className="px-2.5 py-1 bg-white/20 hover:bg-white/30 rounded-lg font-semibold flex items-center space-x-1 transition shrink-0"
      >
        <RefreshCw className="w-3 h-3" />
        <span>Sync</span>
      </button>
    </div>
  );
};
