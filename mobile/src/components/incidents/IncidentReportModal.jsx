import React, { useState } from 'react';
import { View, Text, TouchableOpacity, TextInput, Modal, StyleSheet } from 'react-native';

export function IncidentReportModal({ visible, onClose, onSubmit, submitting }) {
  const [incidentType, setIncidentType] = useState('ROAD_PROBLEM');
  const [description, setDescription] = useState('');

  const handlePressSubmit = () => {
    onSubmit({ incidentType, description });
    setDescription('');
  };

  const incidentOptions = [
    { label: 'Accident / Breakdown', value: 'ACCIDENT' },
    { label: 'Customs Checkpoint Delay', value: 'CHECKPOINT_DELAY' },
    { label: 'Fuel Shortage', value: 'FUEL_UNAVAILABLE' },
    { label: 'Road Problem / Blockage', value: 'ROAD_PROBLEM' },
    { label: 'Security Incident Alert', value: 'SECURITY_INCIDENT' },
  ];

  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.overlay}>
        <View style={styles.content}>
          <Text style={styles.title}>Report Corridor Incident</Text>
          <Text style={styles.subtitle}>Select incident category for instant dispatch notification:</Text>

          <View style={styles.optionsList}>
            {incidentOptions.map((opt) => (
              <TouchableOpacity
                key={opt.value}
                style={[
                  styles.optionCard,
                  incidentType === opt.value && styles.optionCardSelected,
                ]}
                onPress={() => setIncidentType(opt.value)}
              >
                <Text
                  style={[
                    styles.optionText,
                    incidentType === opt.value && styles.optionTextSelected,
                  ]}
                >
                  {opt.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <TextInput
            style={styles.textInput}
            placeholder="Optional incident details or highway milepost location..."
            placeholderTextColor="#64748b"
            value={description}
            onChangeText={setDescription}
            multiline
            numberOfLines={2}
          />

          <View style={styles.buttonRow}>
            <TouchableOpacity style={styles.cancelBtn} onPress={onClose}>
              <Text style={styles.cancelBtnText}>Cancel</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.submitBtn}
              onPress={handlePressSubmit}
              disabled={submitting}
            >
              <Text style={styles.submitBtnText}>
                {submitting ? 'Sending...' : 'Report Incident'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(2, 6, 23, 0.85)',
    justifyContent: 'center',
    padding: 16,
  },
  content: {
    backgroundColor: '#0f172a',
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: '#1e293b',
  },
  title: {
    fontSize: 18,
    fontWeight: '800',
    color: '#f43f5e',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 12,
    color: '#94a3b8',
    marginBottom: 14,
  },
  optionsList: {
    gap: 8,
    marginBottom: 14,
  },
  optionCard: {
    paddingVertical: 12,
    paddingHorizontal: 14,
    borderRadius: 10,
    backgroundColor: '#1e293b',
    borderWidth: 1,
    borderColor: '#334155',
  },
  optionCardSelected: {
    backgroundColor: 'rgba(244, 63, 94, 0.2)',
    borderColor: '#f43f5e',
  },
  optionText: {
    color: '#cbd5e1',
    fontSize: 13,
    fontWeight: '600',
  },
  optionTextSelected: {
    color: '#fda4af',
    fontWeight: '700',
  },
  textInput: {
    backgroundColor: '#1e293b',
    borderRadius: 10,
    padding: 12,
    color: '#ffffff',
    fontSize: 13,
    borderWidth: 1,
    borderColor: '#334155',
    marginBottom: 16,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 10,
  },
  cancelBtn: {
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 10,
    backgroundColor: '#334155',
  },
  cancelBtnText: {
    color: '#94a3b8',
    fontSize: 13,
    fontWeight: '700',
  },
  submitBtn: {
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 10,
    backgroundColor: '#e11d48',
  },
  submitBtnText: {
    color: '#ffffff',
    fontSize: 13,
    fontWeight: '700',
  },
});
