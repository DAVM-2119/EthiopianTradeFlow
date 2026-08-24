import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, SafeAreaView } from 'react-native';
import { AssignedShipmentsScreen } from '../screens/shipments/AssignedShipmentsScreen.jsx';
import { DriverShipmentDetailsScreen } from '../screens/shipments/DriverShipmentDetailsScreen.jsx';
import { RiskAlertsScreen } from '../screens/alerts/RiskAlertsScreen.jsx';
import { DriverProfileScreen } from '../screens/profile/DriverProfileScreen.jsx';

export function DriverTabs() {
  const [activeTab, setActiveTab] = useState('shipments');
  const [selectedShipmentId, setSelectedShipmentId] = useState(null);

  const renderContent = () => {
    if (selectedShipmentId) {
      return (
        <DriverShipmentDetailsScreen
          shipmentId={selectedShipmentId}
          onBack={() => setSelectedShipmentId(null)}
        />
      );
    }

    switch (activeTab) {
      case 'shipments':
        return <AssignedShipmentsScreen onSelectShipment={setSelectedShipmentId} />;
      case 'alerts':
        return <RiskAlertsScreen />;
      case 'profile':
        return <DriverProfileScreen />;
      default:
        return <AssignedShipmentsScreen onSelectShipment={setSelectedShipmentId} />;
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        {renderContent()}

        {!selectedShipmentId && (
          <View style={styles.tabBar}>
            <TouchableOpacity
              style={[styles.tabItem, activeTab === 'shipments' && styles.tabActive]}
              onPress={() => setActiveTab('shipments')}
            >
              <Text style={[styles.tabText, activeTab === 'shipments' && styles.tabTextActive]}>
                Shipments
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.tabItem, activeTab === 'alerts' && styles.tabActive]}
              onPress={() => setActiveTab('alerts')}
            >
              <Text style={[styles.tabText, activeTab === 'alerts' && styles.tabTextActive]}>
                Risk Alerts
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.tabItem, activeTab === 'profile' && styles.tabActive]}
              onPress={() => setActiveTab('profile')}
            >
              <Text style={[styles.tabText, activeTab === 'profile' && styles.tabTextActive]}>
                Profile
              </Text>
            </TouchableOpacity>
          </View>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#020617' },
  container: { flex: 1, backgroundColor: '#020617' },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#0f172a',
    borderTopWidth: 1,
    borderTopColor: '#1e293b',
    paddingVertical: 10,
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 8,
  },
  tabActive: {
    borderTopWidth: 2,
    borderTopColor: '#00f2fe',
  },
  tabText: {
    color: '#64748b',
    fontSize: 12,
    fontWeight: '700',
  },
  tabTextActive: {
    color: '#00f2fe',
    fontWeight: '900',
  },
});
