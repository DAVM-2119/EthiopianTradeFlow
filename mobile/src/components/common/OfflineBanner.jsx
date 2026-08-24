import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

export function OfflineBanner({ isOnline, queueCount, isSyncing, onTriggerSync, onToggleConnection }) {
  return (
    <View style={[styles.container, isOnline ? styles.onlineBg : styles.offlineBg]}>
      <View style={styles.leftRow}>
        <View style={[styles.indicator, isOnline ? styles.onlineIndicator : styles.offlineIndicator]} />
        <Text style={styles.statusText}>
          {isOnline ? 'ONLINE (LIVE)' : 'OFFLINE MODE'}
        </Text>
      </View>

      {queueCount > 0 && (
        <View style={styles.queueBadge}>
          <Text style={styles.queueText}>{queueCount} Queued</Text>
        </View>
      )}

      <View style={styles.actionRow}>
        {queueCount > 0 && isOnline && (
          <TouchableOpacity
            style={styles.syncButton}
            onPress={onTriggerSync}
            disabled={isSyncing}
          >
            <Text style={styles.syncButtonText}>
              {isSyncing ? 'Syncing...' : 'Sync Now'}
            </Text>
          </TouchableOpacity>
        )}

        <TouchableOpacity style={styles.toggleButton} onPress={onToggleConnection}>
          <Text style={styles.toggleText}>{isOnline ? 'Go Offline' : 'Go Online'}</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  onlineBg: {
    backgroundColor: '#064e3b',
  },
  offlineBg: {
    backgroundColor: '#78350f',
  },
  leftRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  indicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  onlineIndicator: {
    backgroundColor: '#34d399',
  },
  offlineIndicator: {
    backgroundColor: '#fbbf24',
  },
  statusText: {
    color: '#ffffff',
    fontSize: 11,
    fontWeight: '700',
  },
  queueBadge: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  queueText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: '700',
  },
  actionRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  syncButton: {
    backgroundColor: '#0284c7',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    marginRight: 6,
  },
  syncButtonText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: '700',
  },
  toggleButton: {
    backgroundColor: 'rgba(0,0,0,0.3)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  toggleText: {
    color: '#e2e8f0',
    fontSize: 10,
    fontWeight: '600',
  },
});
