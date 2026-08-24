import React from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { trackingService } from '../../services/trackingService.js';

export function RiskAlertsScreen() {
  const { data, isLoading } = useQuery({
    queryKey: ['security-alerts'],
    queryFn: async () => {
      const res = await trackingService.getSecurityAlerts().catch(() => null);
      return Array.isArray(res) ? res : res?.results || [];
    },
  });

  const alerts = data || [
    {
      id: '1',
      title: 'Djibouti-Galafi Security Advisory',
      description: 'Heavy fog and rain reported near Galafi border crossing. Maintain safe distance.',
      severity: 'MEDIUM',
      created_at: new Date().toISOString(),
    },
    {
      id: '2',
      title: 'Modjo Checkpoint Weight Scale Maintenance',
      description: 'Single lane operating at Modjo Dry Port scales due to scheduled calibration.',
      severity: 'LOW',
      created_at: new Date().toISOString(),
    },
  ];

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Corridor Security & Risk Alerts</Text>
        <Text style={styles.headerSubtitle}>Real-time highway advisories and risk zone flags</Text>
      </View>

      <FlatList
        data={alerts}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.alertCard}>
            <View style={styles.cardHeader}>
              <Text style={styles.alertTitle}>{item.title}</Text>
              <Text style={styles.severityBadge}>{item.severity || 'WARNING'}</Text>
            </View>
            <Text style={styles.alertDescription}>{item.description}</Text>
          </View>
        )}
        contentContainerStyle={styles.listContent}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#020617' },
  header: { padding: 16, borderBottomWidth: 1, borderBottomColor: '#1e293b' },
  headerTitle: { fontSize: 18, fontWeight: '900', color: '#ffffff' },
  headerSubtitle: { fontSize: 12, color: '#94a3b8', marginTop: 2 },
  listContent: { padding: 16 },
  alertCard: { backgroundColor: '#0f172a', borderRadius: 14, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: '#1e293b' },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 },
  alertTitle: { fontSize: 14, fontWeight: '800', color: '#fbbf24', flex: 1, marginRight: 8 },
  severityBadge: { backgroundColor: 'rgba(251, 191, 36, 0.15)', color: '#fbbf24', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 10, fontSize: 10, fontWeight: '800' },
  alertDescription: { fontSize: 12, color: '#94a3b8', lineHeight: 18 },
});
