import React from 'react';
import { View, Text, TouchableOpacity, TextInput, Modal, StyleSheet } from 'react-native';

export function ProofOfDeliveryModal({ visible, onClose, onSubmit, submitting }) {
  const [receiverName, setReceiverName] = useState('');
  const [signatureText, setSignatureText] = useState('');

  const handlePressSubmit = () => {
    onSubmit({
      receiver_name: receiverName || 'Modjo Dry Port Warehouse Manager',
      signature: signatureText || 'Digital Signature Verified #POD-9021',
      notes: 'Cargo received in intact container state with verified seals.',
      latitude: 8.591,
      longitude: 39.124,
      timestamp: new Date().toISOString(),
    });
    setReceiverName('');
    setSignatureText('');
  };

  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.overlay}>
        <View style={styles.content}>
          <Text style={styles.title}>Digital Proof of Delivery (POD)</Text>
          <Text style={styles.subtitle}>Capture recipient confirmation and signature details:</Text>

          <View style={styles.formGroup}>
            <Text style={styles.label}>Recipient Full Name / Manager</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g. Abebe Bekele (Warehouse Mgr)"
              placeholderTextColor="#64748b"
              value={receiverName}
              onChangeText={setReceiverName}
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.label}>Digital Signature / Confirmation Ref</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g. SIG-AB-89012"
              placeholderTextColor="#64748b"
              value={signatureText}
              onChangeText={setSignatureText}
            />
          </View>

          <View style={styles.infoBadge}>
            <Text style={styles.infoBadgeText}>
              ✓ Automatic GPS Location & Timestamp snapshot captured upon submission.
            </Text>
          </View>

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
                {submitting ? 'Submitting...' : 'Complete Delivery'}
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
    color: '#10b981',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 12,
    color: '#94a3b8',
    marginBottom: 14,
  },
  formGroup: {
    marginBottom: 12,
  },
  label: {
    fontSize: 12,
    fontWeight: '600',
    color: '#cbd5e1',
    marginBottom: 4,
  },
  input: {
    backgroundColor: '#1e293b',
    borderRadius: 10,
    padding: 12,
    color: '#ffffff',
    fontSize: 13,
    borderWidth: 1,
    borderColor: '#334155',
  },
  infoBadge: {
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    borderRadius: 10,
    padding: 10,
    borderWidth: 1,
    borderColor: 'rgba(16, 185, 129, 0.2)',
    marginBottom: 16,
  },
  infoBadgeText: {
    color: '#6ee7b7',
    fontSize: 11,
    fontWeight: '600',
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
    backgroundColor: '#059669',
  },
  submitBtnText: {
    color: '#ffffff',
    fontSize: 13,
    fontWeight: '700',
  },
});
