import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { shipmentService } from '../../services/shipmentService.js';
import { trackingService } from '../../services/trackingService.js';
import { useDriverLocation } from '../../hooks/useDriverLocation.js';
import { IncidentReportModal } from '../../components/incidents/IncidentReportModal.jsx';
import { ProofOfDeliveryModal } from '../../components/delivery/ProofOfDeliveryModal.jsx';

export function DriverShipmentDetailsScreen({ shipmentId, onBack }) {
  const queryClient = useQueryClient();
  const [showIncidentModal, setShowIncidentModal] = useState(false);
  const [showPodModal, setShowPodModal] = useState(false);
  const [actionNotice, setActionNotice] = useState('');

  const { currentLocation, broadcasting } = useDriverLocation(shipmentId, { enabled: true });

  const { data: shipment, isLoading } = useQuery({
    queryKey: ['driver-shipment-detail', shipmentId],
    queryFn: () => shipmentService.getShipmentDetail(shipmentId),
  });

  const transitionMutation = useMutation({
    mutationFn: (targetStatus) => shipmentService.transitionStatus(shipmentId, targetStatus),
    onSuccess: (data) => {
      if (data?.offline) {
        setActionNotice('Action queued in offline store.');
      } else {
        setActionNotice('Status updated successfully.');
      }
      queryClient.invalidateQueries(['driver-shipment-detail', shipmentId]);
    },
    onError: (err) => {
      setActionNotice(err.message || 'Failed to update status.');
    },
  });

  const incidentMutation = useMutation({
    mutationFn: ({ incidentType, description }) =>
      trackingService.reportIncident(shipmentId, {
        incidentType,
        description,
        latitude: currentLocation.latitude,
        longitude: currentLocation.longitude,
      }),
    onSuccess: (data) => {
      setShowIncidentModal(false);
      setActionNotice(data?.offline ? 'Incident report queued offline.' : 'Incident reported to dispatch.');
    },
  });

  const podMutation = useMutation({
    mutationFn: (proofData) => shipmentService.submitProofOfDelivery(shipmentId, proofData),
    onSuccess: (data) => {
      setShowPodModal(false);
      setActionNotice(data?.offline ? 'Proof of delivery queued offline.' : 'Delivery completed.');
      queryClient.invalidateQueries(['driver-shipment-detail', shipmentId]);
    },
  });

  if (isLoading || !shipment) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#00f2fe" />
      </View>
    );
  }

  const load = shipment.load_data || shipment.load_detail || {};

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
      <TouchableOpacity style={styles.backBtn} onPress={onBack}>
        <Text style={styles.backBtnText}>← Back to Shipments</Text>
      </TouchableOpacity>

      {actionNotice ? (
        <View style={styles.noticeBox}>
          <Text style={styles.noticeText}>{actionNotice}</Text>
        </View>
      ) : null}

      <View style={styles.card}>
        <Text style={styles.refText}>Shipment #{shipment.id?.substring(0, 8)}</Text>
        <Text style={styles.routeText}>
          {shipment.origin_city || load.origin_city || 'Djibouti Port'} ➔ {shipment.destination_city || load.destination_city || 'Modjo Dry Port'}
        </Text>
        <Text style={styles.statusPill}>Status: {shipment.status}</Text>
      </View>

      {/* GPS Telemetry Banner */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Live GPS Telemetry</Text>
        <Text style={styles.gpsText}>
          Lat: {currentLocation.latitude.toFixed(4)}° | Lng: {currentLocation.longitude.toFixed(4)}°
        </Text>
        <Text style={styles.speedText}>Speed: {currentLocation.speed} km/h (N1 Corridor)</Text>
      </View>

      {/* Driver Actions */}
      <View style={styles.actionsContainer}>
        <Text style={styles.sectionTitle}>Driver Actions</Text>

        <TouchableOpacity
          style={styles.actionBtnPrimary}
          onPress={() => transitionMutation.mutate('IN_TRANSIT')}
        >
          <Text style={styles.actionBtnText}>Start Trip (IN TRANSIT)</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionBtnAmber}
          onPress={() => transitionMutation.mutate('CUSTOMS_PROCESSING')}
        >
          <Text style={styles.actionBtnText}>Customs Checkpoint</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionBtnDanger}
          onPress={() => setShowIncidentModal(true)}
        >
          <Text style={styles.actionBtnText}>Report Incident</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionBtnSuccess}
          onPress={() => setShowPodModal(true)}
        >
          <Text style={styles.actionBtnText}>Capture Proof of Delivery</Text>
        </TouchableOpacity>
      </View>

      <IncidentReportModal
        visible={showIncidentModal}
        onClose={() => setShowIncidentModal(false)}
        onSubmit={(data) => incidentMutation.mutate(data)}
        submitting={incidentMutation.isPending}
      />

      <ProofOfDeliveryModal
        visible={showPodModal}
        onClose={() => setShowPodModal(false)}
        onSubmit={(data) => podMutation.mutate(data)}
        submitting={podMutation.isPending}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#020617' },
  scrollContent: { padding: 16 },
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#020617' },
  backBtn: { marginBottom: 14 },
  backBtnText: { color: '#38bdf8', fontSize: 14, fontWeight: '700' },
  noticeBox: { backgroundColor: 'rgba(6, 182, 212, 0.15)', padding: 12, borderRadius: 10, marginBottom: 14 },
  noticeText: { color: '#22d3ee', fontSize: 12, fontWeight: '700', textAlign: 'center' },
  card: { backgroundColor: '#0f172a', borderRadius: 16, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: '#1e293b' },
  cardTitle: { color: '#94a3b8', fontSize: 12, fontWeight: '700', marginBottom: 6 },
  refText: { fontSize: 12, color: '#00f2fe', fontWeight: '800' },
  routeText: { fontSize: 18, color: '#ffffff', fontWeight: '900', marginVertical: 6 },
  statusPill: { color: '#34d399', fontSize: 12, fontWeight: '700' },
  gpsText: { color: '#00f2fe', fontSize: 14, fontWeight: '700', fontFamily: 'monospace' },
  speedText: { color: '#cbd5e1', fontSize: 12, marginTop: 4 },
  actionsContainer: { marginTop: 8, gap: 10 },
  sectionTitle: { color: '#ffffff', fontSize: 15, fontWeight: '800', marginBottom: 6 },
  actionBtnPrimary: { backgroundColor: '#0284c7', padding: 14, borderRadius: 12, alignItems: 'center' },
  actionBtnAmber: { backgroundColor: '#d97706', padding: 14, borderRadius: 12, alignItems: 'center' },
  actionBtnDanger: { backgroundColor: '#e11d48', padding: 14, borderRadius: 12, alignItems: 'center' },
  actionBtnSuccess: { backgroundColor: '#059669', padding: 14, borderRadius: 12, alignItems: 'center' },
  actionBtnText: { color: '#ffffff', fontSize: 14, fontWeight: '800' },
});
