/**
 * CITADEL KEBBI - Mobile App for Field Officers
 * React Native - Android & iOS
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
} from 'react-native';
import MapView, { Marker, Circle } from 'react-native-maps';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Location from 'expo-location';
import * as Notifications from 'expo-notifications';

const API_BASE = 'https://divine-daveta-securekebbi-2f64fe25.koyeb.app/api';

// Push notification configuration
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export default function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [user, setUser] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [fires, setFires] = useState([]);
  const [satellites, setSatellites] = useState([]);
  const [loading, setLoading] = useState(false);
  const [location, setLocation] = useState(null);

  // Initialize app
  useEffect(() => {
    checkAuth();
    requestPermissions();
    setupNotifications();
    getCurrentLocation();
  }, []);

  // Request location and notification permissions
  const requestPermissions = async () => {
    const { status: locStatus } = await Location.requestForegroundPermissionsAsync();
    const { status: notifStatus } = await Notifications.requestPermissionsAsync();
    
    if (locStatus !== 'granted') {
      Alert.alert('Permission Required', 'Location needed for threat proximity alerts');
    }
  };

  // Setup push notifications
  const setupNotifications = async () => {
    const token = await Notifications.getExpoPushTokenAsync();
    // Register token with backend
    await fetch(`${API_BASE}/mobile/register-token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: token.data }),
    });

    // Listen for notifications
    Notifications.addNotificationReceivedListener(handleNotification);
  };

  const handleNotification = (notification) => {
    const { title, body, data } = notification.request.content;
    Alert.alert(title, body, [
      { text: 'View', onPress: () => navigateToAlert(data) },
      { text: 'Dismiss', style: 'cancel' },
    ]);
  };

  // Get current GPS location
  const getCurrentLocation = async () => {
    const location = await Location.getCurrentPositionAsync({});
    setLocation(location.coords);
  };

  // Check authentication
  const checkAuth = async () => {
    const token = await AsyncStorage.getItem('auth_token');
    if (token) {
      // Verify token
      fetchUserData(token);
    }
  };

  // Fetch all data
  const loadData = async () => {
    setLoading(true);
    try {
      const [firesRes, satellitesRes, alertsRes] = await Promise.all([
        fetch(`${API_BASE}/dashboard/fires?days=1`),
        fetch(`${API_BASE}/satellite/sentinel/passes?days=1`),
        fetch(`${API_BASE}/intel/feed?max=10`),
      ]);

      const firesData = await firesRes.json();
      const satData = await satellitesRes.json();
      const alertsData = await alertsRes.json();

      setFires(firesData.hotspots?.slice(0, 20) || []);
      setSatellites(satData.upcoming_passes?.slice(0, 5) || []);
      setAlerts(alertsData.reports?.slice(0, 10) || []);
    } catch (e) {
      console.error('Load error:', e);
    }
    setLoading(false);
  };

  // Dashboard View
  const DashboardView = () => (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={loading} onRefresh={loadData} />}
    >
      {/* Threat Level Card */}
      <View style={styles.threatCard}>
        <Text style={styles.threatTitle}>CURRENT THREAT LEVEL</Text>
        <Text style={styles.threatValue}>CRITICAL</Text>
        <Text style={styles.threatSubtitle}>{fires.length} Active Fire Hotspots</Text>
      </View>

      {/* Quick Actions */}
      <View style={styles.quickActions}>
        <TouchableOpacity style={styles.actionBtn} onPress={() => setCurrentView('map')}>
          <Text style={styles.actionText}>🗺️ VIEW MAP</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionBtn} onPress={() => setCurrentView('sitrep')}>
          <Text style={styles.actionText}>📋 SITREP</Text>
        </TouchableOpacity>
      </View>

      {/* Fire Alerts */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🔥 FIRE HOTSPOTS ({fires.length})</Text>
        {fires.slice(0, 5).map((fire, idx) => (
          <View key={idx} style={styles.alertItem}>
            <Text style={styles.alertTitle}>
              {fire.latitude?.toFixed(4)}°N, {fire.longitude?.toFixed(4)}°E
            </Text>
            <Text style={styles.alertMeta}>
              Brightness: {fire.brightness}K | {fire.acq_date}
            </Text>
          </View>
        ))}
      </View>

      {/* Satellite Passes */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🛰️ NEXT SATELLITE PASSES</Text>
        {satellites.map((pass, idx) => (
          <View key={idx} style={styles.satItem}>
            <Text style={styles.satName}>{pass.satellite}</Text>
            <Text style={styles.satTime}>
              {Math.floor(pass.seconds_until / 3600)}h {Math.floor((pass.seconds_until % 3600) / 60)}m
            </Text>
          </View>
        ))}
      </View>

      {/* Intel Alerts */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📡 LATEST INTELLIGENCE</Text>
        {alerts.map((alert, idx) => (
          <View key={idx} style={[styles.intelItem, { borderLeftColor: getSeverityColor(alert.severity) }]}>
            <Text style={styles.intelTitle}>{alert.title}</Text>
            <Text style={styles.intelSource}>{alert.source} • {alert.severity}</Text>
          </View>
        ))}
      </View>
    </ScrollView>
  );

  // Map View
  const MapViewComponent = () => (
    <View style={styles.container}>
      <MapView
        style={styles.map}
        initialRegion={{
          latitude: 12.0,
          longitude: 4.0,
          latitudeDelta: 3.0,
          longitudeDelta: 3.0,
        }}
      >
        {/* Current Location */}
        {location && (
          <Marker
            coordinate={{ latitude: location.latitude, longitude: location.longitude }}
            title="Your Position"
            pinColor="blue"
          />
        )}

        {/* Fire Hotspots */}
        {fires.map((fire, idx) => (
          <Circle
            key={`fire-${idx}`}
            center={{ latitude: fire.latitude, longitude: fire.longitude }}
            radius={500}
            fillColor="rgba(255, 0, 0, 0.3)"
            strokeColor="red"
          />
        ))}
      </MapView>

      <TouchableOpacity style={styles.backBtn} onPress={() => setCurrentView('dashboard')}>
        <Text style={styles.backText}>← BACK</Text>
      </TouchableOpacity>
    </View>
  );

  // SITREP View
  const SitrepView = () => (
    <View style={styles.container}>
      <Text style={styles.header}>SITREP GENERATOR</Text>
      <TouchableOpacity style={styles.generateBtn}>
        <Text style={styles.generateText}>GENERATE FIELD REPORT</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.backBtn} onPress={() => setCurrentView('dashboard')}>
        <Text style={styles.backText}>← BACK</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      {currentView === 'dashboard' && <DashboardView />}
      {currentView === 'map' && <MapViewComponent />}
      {currentView === 'sitrep' && <SitrepView />}
    </SafeAreaView>
  );
}

// Helper functions
const getSeverityColor = (severity) => {
  const colors = {
    critical: '#ff0040',
    high: '#ff6600',
    medium: '#f0ff00',
    low: '#00ff80',
  };
  return colors[severity] || '#00ff80';
};

const navigateToAlert = (data) => {
  // Navigate to specific alert on map
};

// Styles
const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#0a0f1c' },
  container: { flex: 1, backgroundColor: '#0a0f1c' },
  threatCard: {
    backgroundColor: '#ff004022',
    borderWidth: 1,
    borderColor: '#ff0040',
    margin: 16,
    padding: 20,
    borderRadius: 8,
  },
  threatTitle: { color: '#ff0040', fontSize: 12, fontWeight: 'bold' },
  threatValue: { color: '#ff0040', fontSize: 32, fontWeight: 'bold', marginVertical: 8 },
  threatSubtitle: { color: '#8a94a6', fontSize: 14 },
  quickActions: { flexDirection: 'row', justifyContent: 'space-around', marginHorizontal: 16, marginBottom: 16 },
  actionBtn: {
    backgroundColor: '#00f0ff22',
    borderWidth: 1,
    borderColor: '#00f0ff',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 4,
    flex: 1,
    marginHorizontal: 8,
  },
  actionText: { color: '#00f0ff', textAlign: 'center', fontWeight: 'bold' },
  section: { margin: 16, marginTop: 8 },
  sectionTitle: { color: '#00f0ff', fontSize: 12, fontWeight: 'bold', marginBottom: 8 },
  alertItem: {
    backgroundColor: '#ffffff08',
    padding: 12,
    marginBottom: 8,
    borderRadius: 4,
    borderLeftWidth: 3,
    borderLeftColor: '#ff0040',
  },
  alertTitle: { color: '#fff', fontSize: 14 },
  alertMeta: { color: '#8a94a6', fontSize: 12, marginTop: 4 },
  satItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#ffffff08',
    padding: 12,
    marginBottom: 8,
    borderRadius: 4,
  },
  satName: { color: '#00f0ff', fontSize: 14 },
  satTime: { color: '#00ff80', fontSize: 14, fontWeight: 'bold' },
  intelItem: {
    backgroundColor: '#ffffff08',
    padding: 12,
    marginBottom: 8,
    borderRadius: 4,
    borderLeftWidth: 3,
  },
  intelTitle: { color: '#fff', fontSize: 13 },
  intelSource: { color: '#8a94a6', fontSize: 11, marginTop: 4 },
  map: { flex: 1 },
  backBtn: {
    position: 'absolute',
    top: 16,
    left: 16,
    backgroundColor: '#000000cc',
    padding: 12,
    borderRadius: 4,
  },
  backText: { color: '#fff', fontWeight: 'bold' },
  header: { color: '#00f0ff', fontSize: 20, fontWeight: 'bold', textAlign: 'center', marginTop: 20 },
  generateBtn: {
    backgroundColor: '#00f0ff',
    margin: 20,
    padding: 16,
    borderRadius: 4,
    alignItems: 'center',
  },
  generateText: { color: '#000', fontWeight: 'bold', fontSize: 16 },
});
