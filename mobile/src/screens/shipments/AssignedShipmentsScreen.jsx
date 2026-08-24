import React, { useState } from 'react';
import { View, Text, FlatList, RefreshControl, StyleSheet, ActivityIndicator } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { shipmentService } from '../../services/shipmentService.js';
import { DriverShipmentCard } from '../../components/shipments/DriverShipmentCard.jsx';
import { OfflineBanner } from '../../components/common/OfflineBanner.jsx';
import { useOfflineSync } from '../../hooks/useOfflineSync.js';

export function AssignedShipmentsScreen({ onSelectShipment }) {
  const { isOnline, queueCount, isSyncing, triggerSync, toggleConnectionState } = useOfflineSync();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['driver-assigned-shipments'],
    queryFn: async () => {
      const res = await shipmentService.getAssignedShipments();
      return Array.isArray(res) ? res : res?.results || [];
    },
  });

  const shipments = data || [];

  return (
    <View style={styles.container}>
      <OfflineBanner
        isOnline={isOnline}
        queueCount={queueCount}
        isSyncing={isSyncing}
        onTriggerSync={triggerSync}
        onToggleConnection={toggleConnectionState}
      />

      <View style={styles.header}>
        <Text style={styles.headerTitle}>Assigned Corridor Shipments</Text>
        <Text style={styles.headerSubtitle}>
          {shipments.length} Active Cargo Assignment{shipments.length === 1 ? '' : 's'}
        </Text>
      </View>

      {isLoading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#00f2fe" />
          <Text style={styles.loadingText}>Fetching assigned shipments...</Text>
        </View>
      ) : shipments.length === 0 ? (
        <View style={styles.centerContainer}>
          <Text style={styles.emptyTitle}>No Assigned Shipments</Text>
          <Text style={styles.emptySubtitle}>
            When a transporter assigns a load booking, it will automatically appear here.
          </Text>
        </View>
      ) : (
        <FlatList
          data={shipments}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <DriverShipmentCard
              shipment={item}
              onPress={() => onSelectShipment(item.id)}
            />
          )}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor="#00f2fe" />
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#020617',
  },
  header: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#1e293b',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '900',
    color: '#ffffff',
  },
  headerSubtitle: {
    fontSize: 12,
    color: '#94a3b8',
    marginTop: 2,
  },
  listContent: {
    padding: 16,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  loadingText: {
    marginTop: 12,
    color: '#94a3b8',
    fontSize: 13,
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#ffffff',
    marginBottom: 6,
  },
  emptySubtitle: {
    fontSize: 12,
    color: '#64748b',
    textAlign: 'center',
  },
});
