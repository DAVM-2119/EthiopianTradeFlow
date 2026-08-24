import { useState, useEffect, useCallback } from 'react';
import { offlineQueue } from '../storage/offlineQueue.js';
import { syncService } from '../services/syncService.js';

export function useOfflineSync() {
  const [isOnline, setIsOnline] = useState(true);
  const [queueCount, setQueueCount] = useState(0);
  const [isSyncing, setIsSyncing] = useState(false);

  const refreshQueueCount = useCallback(async () => {
    const count = await offlineQueue.count();
    setQueueCount(count);
  }, []);

  useEffect(() => {
    refreshQueueCount();
    const interval = setInterval(() => {
      refreshQueueCount();
    }, 5000);
    return () => clearInterval(interval);
  }, [refreshQueueCount]);

  const triggerSync = async () => {
    if (isSyncing || queueCount === 0) return;
    setIsSyncing(true);
    try {
      const res = await syncService.processOfflineQueue();
      await refreshQueueCount();
      return res;
    } finally {
      setIsSyncing(false);
    }
  };

  const toggleConnectionState = () => {
    setIsOnline((prev) => !prev);
  };

  return {
    isOnline,
    queueCount,
    isSyncing,
    triggerSync,
    toggleConnectionState,
    refreshQueueCount,
  };
}
