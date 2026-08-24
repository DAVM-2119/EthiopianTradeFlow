import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useAuth } from '../../hooks/useAuth.js';

export function DriverProfileScreen() {
  const { user, logout } = useAuth();

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Driver Profile</Text>
        <Text style={styles.headerSubtitle}>Verification & Account Management</Text>
      </View>

      <View style={styles.profileCard}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>{user?.first_name?.[0] || 'D'}</Text>
        </View>

        <Text style={styles.userName}>
          {user?.first_name ? `${user.first_name} ${user.last_name || ''}` : user?.phone || 'Driver User'}
        </Text>
        <Text style={styles.userRole}>ROLE: {user?.role || 'DRIVER'}</Text>
        <Text style={styles.userPhone}>{user?.phone || '+251 911 223 344'}</Text>

        <View style={styles.statsRow}>
          <View style={styles.statBox}>
            <Text style={styles.statNum}>4.9 ★</Text>
            <Text style={styles.statLabel}>Rating</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statNum}>98%</Text>
            <Text style={styles.statLabel}>On-Time</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statNum}>Tier 1</Text>
            <Text style={styles.statLabel}>Carrier</Text>
          </View>
        </View>
      </View>

      <TouchableOpacity style={styles.logoutBtn} onPress={logout}>
        <Text style={styles.logoutBtnText}>Sign Out of Mobile App</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#020617', padding: 16 },
  header: { marginBottom: 16 },
  headerTitle: { fontSize: 20, fontWeight: '900', color: '#ffffff' },
  headerSubtitle: { fontSize: 12, color: '#94a3b8', marginTop: 2 },
  profileCard: { backgroundColor: '#0f172a', borderRadius: 20, padding: 24, alignItems: 'center', borderWidth: 1, borderColor: '#1e293b' },
  avatar: { width: 64, height: 64, borderRadius: 32, backgroundColor: 'rgba(0, 242, 254, 0.2)', borderWidth: 2, borderColor: '#00f2fe', justifyContent: 'center', alignItems: 'center', marginBottom: 12 },
  avatarText: { fontSize: 24, fontWeight: '900', color: '#00f2fe' },
  userName: { fontSize: 18, fontWeight: '800', color: '#ffffff' },
  userRole: { fontSize: 11, fontWeight: '800', color: '#34d399', marginVertical: 4 },
  userPhone: { fontSize: 13, color: '#94a3b8', marginBottom: 16 },
  statsRow: { flexDirection: 'row', justifyContent: 'space-around', width: '100%', paddingTop: 16, borderTopWidth: 1, borderTopColor: '#1e293b' },
  statBox: { alignItems: 'center' },
  statNum: { fontSize: 16, fontWeight: '900', color: '#ffffff' },
  statLabel: { fontSize: 11, color: '#64748b', marginTop: 2 },
  logoutBtn: { backgroundColor: 'rgba(244, 63, 94, 0.15)', borderWidth: 1, borderColor: 'rgba(244, 63, 94, 0.3)', padding: 14, borderRadius: 12, alignItems: 'center', marginTop: 20 },
  logoutBtnText: { color: '#fda4af', fontSize: 14, fontWeight: '800' },
});
