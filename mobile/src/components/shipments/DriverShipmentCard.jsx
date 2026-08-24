import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

export function DriverShipmentCard({ shipment, onPress }) {
  const load = shipment.load_data || shipment.load_detail || {};
  const origin = shipment.origin_city || load.origin_city || 'Djibouti Port';
  const destination = shipment.destination_city || load.destination_city || 'Modjo Dry Port';
  const status = shipment.status || 'BOOKED';

  const getStatusColor = (st) => {
    switch (st) {
      case 'IN_TRANSIT':
        return { bg: 'rgba(6, 182, 212, 0.15)', text: '#22d3ee', border: 'rgba(6, 182, 212, 0.3)' };
      case 'DELIVERED':
      case 'COMPLETED':
        return { bg: 'rgba(16, 185, 129, 0.15)', text: '#34d399', border: 'rgba(16, 185, 129, 0.3)' };
      case 'CUSTOMS_PROCESSING':
        return { bg: 'rgba(168, 85, 247, 0.15)', text: '#c084fc', border: 'rgba(168, 85, 247, 0.3)' };
      default:
        return { bg: 'rgba(245, 158, 11, 0.15)', text: '#fbbf24', border: 'rgba(245, 158, 11, 0.3)' };
    }
  };

  const statusStyle = getStatusColor(status);

  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.8}>
      <View style={styles.headerRow}>
        <Text style={styles.refText}>#{shipment.id?.substring(0, 8)}</Text>
        <View style={[styles.badge, { backgroundColor: statusStyle.bg, borderColor: statusStyle.border }]}>
          <Text style={[styles.badgeText, { color: statusStyle.text }]}>{status.replace('_', ' ')}</Text>
        </View>
      </View>

      <Text style={styles.routeText}>
        {origin} <Text style={styles.arrowText}>➔</Text> {destination}
      </Text>

      <View style={styles.metaRow}>
        <Text style={styles.metaText}>
          Cargo: <Text style={styles.metaValue}>{shipment.cargo_type || load.cargo_type || 'General Cargo'}</Text>
        </Text>
        <Text style={styles.metaText}>
          Weight: <Text style={styles.metaValue}>{shipment.weight || load.weight || '30.0'} T</Text>
        </Text>
      </View>

      <View style={styles.footerRow}>
        <Text style={styles.etaText}>Corridor Highway N1</Text>
        <Text style={styles.actionText}>Open Shipment ➔</Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#0f172a',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#1e293b',
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  refText: {
    fontSize: 13,
    fontWeight: '800',
    color: '#00f2fe',
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 20,
    borderWidth: 1,
  },
  badgeText: {
    fontSize: 10,
    fontWeight: '800',
  },
  routeText: {
    fontSize: 16,
    fontWeight: '800',
    color: '#ffffff',
    marginBottom: 10,
  },
  arrowText: {
    color: '#00f2fe',
  },
  metaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#1e293b',
    marginBottom: 10,
  },
  metaText: {
    fontSize: 12,
    color: '#94a3b8',
  },
  metaValue: {
    color: '#e2e8f0',
    fontWeight: '700',
  },
  footerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  etaText: {
    fontSize: 11,
    color: '#64748b',
    fontWeight: '600',
  },
  actionText: {
    fontSize: 12,
    color: '#38bdf8',
    fontWeight: '700',
  },
});
