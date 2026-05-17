
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  TextInput,
  Alert,
  ActivityIndicator,
  Modal,
  SafeAreaView,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// ============== TYPE DEFINITIONS ==============
interface GridData {
  power?: number;
  voltage?: number;
  current?: number;
}

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
}

interface AlertRule {
  id?: number;
  name: string;
  alert_type: string;
  threshold: number;
}

interface RenewableSource {
  id?: number;
  name: string;
  source_type: 'SOLAR' | 'WIND' | 'HYDRO' | 'OTHER';
  capacity_kw: number;
  location?: string;
}

interface ConnectionStatus {
  isConnected: boolean;
  apiUrl: string;
  lastError?: string;
}

type TabType = 'dashboard' | 'alerts' | 'renewable';
type RuleType = 'voltage_high' | 'voltage_low' | 'power_high';
type RenewableType = 'SOLAR' | 'WIND' | 'HYDRO' | 'OTHER';

const DEFAULT_API_URL = 'http://192.168.1.4:8000/api';
const COST_PER_KWH = 25;
const REQUEST_TIMEOUT = 10000; // 10 seconds

// ============== HELPER FUNCTIONS ==============
/**
 * Fetch helper with error handling, timeout, and status checking
 */
async function fetchWithErrorHandling<T>(
  url: string,
  options?: RequestInit,
  timeout: number = REQUEST_TIMEOUT
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return data as T;
  } catch (error) {
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error(`Request timeout after ${timeout}ms`);
      }
      throw error;
    }
    throw new Error('Unknown error occurred');
  } finally {
    clearTimeout(timeoutId);
  }
}

// ============== MAIN COMPONENT ==============
export default function SmartGridApp() {
  // ========== API & CONNECTION STATE ==========
  const [apiUrl, setApiUrl] = useState<string>(DEFAULT_API_URL);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    isConnected: false,
    apiUrl: DEFAULT_API_URL,
  });
  const [showSettings, setShowSettings] = useState(false);
  const [tempApiUrl, setTempApiUrl] = useState(DEFAULT_API_URL);
  const [testingConnection, setTestingConnection] = useState(false);

  // ========== TAB STATE ==========
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(false);

  // ========== DASHBOARD STATE ==========
  const [power, setPower] = useState<number>(0);
  const [voltage, setVoltage] = useState<number>(0);
  const [current, setCurrent] = useState<number>(0);
  const [deviceStatus, setDeviceStatus] = useState<'ON' | 'OFF'>('ON');
  const [dailyCost, setDailyCost] = useState<number>(0);
  const [monthlyCost, setMonthlyCost] = useState<number>(0);
  const [dailyKwh, setDailyKwh] = useState<number>(0);

  // ========== ALERT STATE ==========
  const [email, setEmail] = useState<string>('');
  const [phone, setPhone] = useState<string>('');
  const [emailAlerts, setEmailAlerts] = useState<boolean>(true);
  const [smsAlerts, setSmsAlerts] = useState<boolean>(false);
  const [alertRules, setAlertRules] = useState<AlertRule[]>([]);
  const [ruleName, setRuleName] = useState<string>('');
  const [ruleType, setRuleType] = useState<RuleType>('voltage_high');
  const [ruleThreshold, setRuleThreshold] = useState<string>('');

  // ========== RENEWABLE STATE ==========
  const [renewableSources, setRenewableSources] = useState<RenewableSource[]>([]);
  const [renewableName, setRenewableName] = useState<string>('');
  const [renewableType, setRenewableType] = useState<RenewableType>('SOLAR');
  const [renewableCapacity, setRenewableCapacity] = useState<string>('');
  const [renewableLocation, setRenewableLocation] = useState<string>('');

  // ========== INITIALIZATION & SETTINGS ==========

  /**
   * Load API URL from storage on app start
   */
  useEffect(() => {
    loadApiUrl();
  }, []);

  const loadApiUrl = async () => {
    try {
      const savedUrl = await AsyncStorage.getItem('API_URL');
      if (savedUrl) {
        setApiUrl(savedUrl);
        setTempApiUrl(savedUrl);
        setConnectionStatus((prev) => ({ ...prev, apiUrl: savedUrl }));
      }
    } catch (error) {
      console.error('Failed to load API URL from storage:', error);
    }
  };

  /**
   * Test connection to API
   */
  const testApiConnection = async (url: string): Promise<boolean> => {
    try {
      setTestingConnection(true);
      const response = await fetchWithErrorHandling<ApiResponse<GridData>>(
        `${url}/data/latest/`,
        undefined,
        5000 // 5 second timeout for test
      );

      if (response.success !== false) {
        return true;
      }
      return false;
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    } finally {
      setTestingConnection(false);
    }
  };

  /**
   * Update API URL with connection test
   */
  const updateApiUrl = async () => {
    if (!tempApiUrl) {
      Alert.alert('Error', 'Please enter an API URL');
      return;
    }

    if (!tempApiUrl.startsWith('http')) {
      Alert.alert('Error', 'URL must start with http:// or https://');
      return;
    }

    const isConnected = await testApiConnection(tempApiUrl);

    if (isConnected) {
      setApiUrl(tempApiUrl);
      await AsyncStorage.setItem('API_URL', tempApiUrl);
      setConnectionStatus({
        isConnected: true,
        apiUrl: tempApiUrl,
      });
      Alert.alert('Success', `✅ Connected to ${tempApiUrl}`);
      setShowSettings(false);
    } else {
      Alert.alert(
        'Connection Failed',
        `Could not connect to ${tempApiUrl}\n\nMake sure:\n1. Backend is running\n2. Phone is on same WiFi\n3. IP address is correct`
      );
      setConnectionStatus((prev) => ({
        ...prev,
        isConnected: false,
        lastError: `Cannot reach ${tempApiUrl}`,
      }));
    }
  };

  // ========== AUTO-CHECK CONNECTION ==========

  /**
   * Check connection status periodically
   */
  useEffect(() => {
    const checkConnection = async () => {
      const isConnected = await testApiConnection(apiUrl);
      setConnectionStatus((prev) => ({
        ...prev,
        isConnected,
        apiUrl,
      }));
    };

    checkConnection();
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, [apiUrl]);

  // ========== DATA FETCHING FUNCTIONS ==========

  /**
   * Fetch latest grid data from API
   */
  const fetchLatestData = async (): Promise<void> => {
    if (!connectionStatus.isConnected) {
      console.warn('Not connected to API');
      return;
    }

    try {
      const response = await fetchWithErrorHandling<ApiResponse<GridData>>(
        `${apiUrl}/data/latest/`
      );

      if (response.data) {
        setPower(response.data.power || 0);
        setVoltage(response.data.voltage || 0);
        setCurrent(response.data.current || 0);
      }
    } catch (error) {
      console.error('Failed to fetch latest data:', error);
      Alert.alert('Error', '⚠️ Failed to fetch grid data');
    }
  };

  /**
   * Calculate daily and monthly costs
   */
  const calculateCosts = (): void => {
    const avgPowerW = power || 2500;
    const dailyEnergy = (avgPowerW / 1000) * 24;
    const daily = dailyEnergy * COST_PER_KWH;
    const monthly = daily * 30;

    setDailyKwh(dailyEnergy);
    setDailyCost(daily);
    setMonthlyCost(monthly);
  };

  /**
   * Refresh all data
   */
  const onRefresh = async (): Promise<void> => {
    setRefreshing(true);
    try {
      await fetchLatestData();
      calculateCosts();
      await getAlertRules();
      await getRenewableSources();
    } catch (error) {
      console.error('Refresh failed:', error);
    } finally {
      setRefreshing(false);
    }
  };

  // ========== DEVICE CONTROL FUNCTIONS ==========

  /**
   * Turn device ON
   */
  const turnDeviceOn = async (): Promise<void> => {
    if (!connectionStatus.isConnected) {
      Alert.alert('Error', 'Not connected to API');
      return;
    }

    try {
      setLoading(true);
      const response = await fetchWithErrorHandling<ApiResponse<unknown>>(
        `${apiUrl}/device/on/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        }
      );

      if (response.success) {
        setDeviceStatus('ON');
        Alert.alert('Success', '✅ Device turned ON');
      } else {
        Alert.alert('Error', response.message || 'Failed to turn device on');
      }
    } catch (error) {
      Alert.alert('Error', '⚠️ Failed to turn device on');
      console.error('Turn ON error:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Turn device OFF
   */
  const turnDeviceOff = async (): Promise<void> => {
    if (!connectionStatus.isConnected) {
      Alert.alert('Error', 'Not connected to API');
      return;
    }

    try {
      setLoading(true);
      const response = await fetchWithErrorHandling<ApiResponse<unknown>>(
        `${apiUrl}/device/off/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        }
      );

      if (response.success) {
        setDeviceStatus('OFF');
        Alert.alert('Success', '✅ Device turned OFF');
      } else {
        Alert.alert('Error', response.message || 'Failed to turn device off');
      }
    } catch (error) {
      Alert.alert('Error', '⚠️ Failed to turn device off');
      console.error('Turn OFF error:', error);
    } finally {
      setLoading(false);
    }
  };

  // ========== ALERT MANAGEMENT FUNCTIONS ==========

  /**
   * Register contact for notifications
   */
  const registerContact = async (): Promise<void> => {
    if (!connectionStatus.isConnected) {
      Alert.alert('Error', 'Not connected to API');
      return;
    }

    if (!email) {
      Alert.alert('Error', 'Please enter email address');
      return;
    }

    try {
      setLoading(true);
      const response = await fetchWithErrorHandling<ApiResponse<unknown>>(
        `${apiUrl}/notifications/register-contact/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_email: email,
            user_phone: phone || null,
            receive_email_alerts: emailAlerts,
            receive_sms_alerts: smsAlerts,
          }),
        }
      );

      if (response.success) {
        Alert.alert('Success', '✅ Contact registered successfully');
        setEmail('');
        setPhone('');
      } else {
        Alert.alert('Error', response.message || 'Failed to register contact');
      }
    } catch (error) {
      Alert.alert('Error', '⚠️ Failed to register contact');
      console.error('Register contact error:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Create a new alert rule
   */
  const createAlertRule = async (): Promise<void> => {
    if (!connectionStatus.isConnected) {
      Alert.alert('Error', 'Not connected to API');
      return;
    }

    if (!ruleName || !ruleThreshold) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    const thresholdNum = parseFloat(ruleThreshold);
    if (isNaN(thresholdNum)) {
      Alert.alert('Error', 'Threshold must be a valid number');
      return;
    }

    try {
      setLoading(true);
      const response = await fetchWithErrorHandling<ApiResponse<AlertRule>>(
        `${apiUrl}/notifications/create-rule/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: ruleName,
            alert_type: ruleType,
            threshold: thresholdNum,
          }),
        }
      );

      if (response.success) {
        Alert.alert('Success', '✅ Alert rule created successfully');
        setRuleName('');
        setRuleThreshold('');
        await getAlertRules();
      } else {
        Alert.alert('Error', response.message || 'Failed to create alert rule');
      }
    } catch (error) {
      Alert.alert('Error', '⚠️ Failed to create alert rule');
      console.error('Create rule error:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Fetch all alert rules
   */
  const getAlertRules = async (): Promise<void> => {
    if (!connectionStatus.isConnected) return;

    try {
      const response = await fetchWithErrorHandling<ApiResponse<AlertRule[]>>(
        `${apiUrl}/notifications/get-rules/`
      );

      if (response.success && Array.isArray(response.data)) {
        setAlertRules(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch alert rules:', error);
    }
  };

  /**
   * Send test email
   */
  const testEmail = async (): Promise<void> => {
    if (!connectionStatus.isConnected) {
      Alert.alert('Error', 'Not connected to API');
      return;
    }

    if (!email) {
      Alert.alert('Error', 'Please enter your email first');
      return;
    }

    try {
      setLoading(true);
      const response = await fetchWithErrorHandling<ApiResponse<unknown>>(
        `${apiUrl}/notifications/test-email/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email }),
        }
      );

      if (response.success) {
        Alert.alert('Success', '✅ Test email sent successfully');
      } else {
        Alert.alert('Error', response.message || 'Failed to send test email');
      }
    } catch (error) {
      Alert.alert('Error', '⚠️ Failed to send test email');
      console.error('Test email error:', error);
    } finally {
      setLoading(false);
    }
  };

  // ========== RENEWABLE SOURCE FUNCTIONS ==========

  /**
   * Add a new renewable energy source
   */
  const addRenewableSource = async (): Promise<void> => {
    if (!connectionStatus.isConnected) {
      Alert.alert('Error', 'Not connected to API');
      return;
    }

    if (!renewableName || !renewableCapacity) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    const capacityNum = parseFloat(renewableCapacity);
    if (isNaN(capacityNum) || capacityNum <= 0) {
      Alert.alert('Error', 'Capacity must be a positive number');
      return;
    }

    try {
      setLoading(true);
      const response = await fetchWithErrorHandling<ApiResponse<RenewableSource>>(
        `${apiUrl}/renewable/add-source/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: renewableName,
            source_type: renewableType,
            capacity_kw: capacityNum,
            location: renewableLocation || null,
          }),
        }
      );

      if (response.success) {
        Alert.alert('Success', '✅ Renewable source added successfully');
        setRenewableName('');
        setRenewableCapacity('');
        setRenewableLocation('');
        await getRenewableSources();
      } else {
        Alert.alert('Error', response.message || 'Failed to add renewable source');
      }
    } catch (error) {
      Alert.alert('Error', '⚠️ Failed to add renewable source');
      console.error('Add renewable source error:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Fetch all renewable sources
   */
  const getRenewableSources = async (): Promise<void> => {
    if (!connectionStatus.isConnected) return;

    try {
      const response = await fetchWithErrorHandling<ApiResponse<RenewableSource[]>>(
        `${apiUrl}/renewable/sources/`
      );

      if (response.success && Array.isArray(response.data)) {
        setRenewableSources(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch renewable sources:', error);
    }
  };

  // ========== LIFECYCLE EFFECTS ==========

  /**
   * Initialize data on component mount
   */
  useEffect(() => {
    fetchLatestData();
    calculateCosts();
    getAlertRules();
    getRenewableSources();

    const interval = setInterval(() => {
      fetchLatestData();
      calculateCosts();
    }, 30000);

    return () => clearInterval(interval);
  }, [apiUrl, connectionStatus.isConnected]);

  /**
   * Recalculate costs when power changes
   */
  useEffect(() => {
    calculateCosts();
  }, [power]);

  // ========== RENDER FUNCTIONS ==========

  const renderRuleItem = (rule: AlertRule): React.ReactElement => (
    <View key={rule.id || Math.random()} style={styles.ruleItem}>
      <Text style={styles.ruleName}>{rule.name}</Text>
      <Text style={styles.ruleType}>
        {rule.alert_type === 'voltage_high'
          ? 'High Voltage'
          : rule.alert_type === 'voltage_low'
          ? 'Low Voltage'
          : 'High Power'}
      </Text>
      <Text style={styles.ruleThreshold}>Threshold: {rule.threshold}</Text>
    </View>
  );

  const renderSourceItem = (source: RenewableSource): React.ReactElement => (
    <View key={source.id || Math.random()} style={styles.sourceItem}>
      <Text style={styles.sourceName}>{source.name}</Text>
      <Text style={styles.sourceType}>{source.source_type}</Text>
      <Text style={styles.sourceCapacity}>Capacity: {source.capacity_kw} kW</Text>
      {source.location && (
        <Text style={styles.sourceLocation}>Location: {source.location}</Text>
      )}
    </View>
  );

  // ========== MAIN RENDER ==========

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#0a0e27' }}>
      {/* Connection Status Banner */}
      {!connectionStatus.isConnected && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorBannerText}>
            🔴 Not Connected - Tap ⚙️ to Configure API
          </Text>
        </View>
      )}

      <ScrollView
        style={styles.container}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerContent}>
            <View>
              <Text style={styles.headerTitle}>Smart Grid</Text>
              <Text style={styles.headerSubtitle}>Energy Management System</Text>
            </View>
            <TouchableOpacity
              style={styles.settingsButton}
              onPress={() => {
                setShowSettings(true);
                setTempApiUrl(apiUrl);
              }}
            >
              <Text style={styles.settingsButtonText}>⚙️</Text>
            </TouchableOpacity>
          </View>
          {connectionStatus.isConnected && (
            <Text style={styles.connectedIndicator}>✅ Connected</Text>
          )}
        </View>

        {/* Navigation Tabs */}
        <View style={styles.tabsContainer}>
          <TouchableOpacity
            style={[styles.tab, activeTab === 'dashboard' && styles.activeTab]}
            onPress={() => setActiveTab('dashboard')}
          >
            <Text style={[styles.tabText, activeTab === 'dashboard' && styles.activeTabText]}>
              Dashboard
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.tab, activeTab === 'alerts' && styles.activeTab]}
            onPress={() => setActiveTab('alerts')}
          >
            <Text style={[styles.tabText, activeTab === 'alerts' && styles.activeTabText]}>
              Alerts
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.tab, activeTab === 'renewable' && styles.activeTab]}
            onPress={() => setActiveTab('renewable')}
          >
            <Text style={[styles.tabText, activeTab === 'renewable' && styles.activeTabText]}>
              Renewable
            </Text>
          </TouchableOpacity>
        </View>

        {/* DASHBOARD TAB */}
        {activeTab === 'dashboard' && (
          <View style={styles.tabContent}>
            <View style={styles.card}>
              <Text style={styles.cardTitle}>Real Time Status</Text>

              <View style={styles.metric}>
                <Text style={styles.metricLabel}>Current Power:</Text>
                <Text style={styles.metricValue}>{power.toFixed(2)} W</Text>
              </View>

              <View style={styles.metric}>
                <Text style={styles.metricLabel}>Voltage:</Text>
                <Text style={styles.metricValue}>{voltage.toFixed(2)} V</Text>
              </View>

              <View style={styles.metric}>
                <Text style={styles.metricLabel}>Current:</Text>
                <Text style={styles.metricValue}>{current.toFixed(2)} A</Text>
              </View>

              <View style={styles.metric}>
                <Text style={styles.metricLabel}>Device Status:</Text>
                <Text
                  style={[
                    styles.metricValue,
                    { color: deviceStatus === 'ON' ? '#10b981' : '#ef4444' },
                  ]}
                >
                  {deviceStatus}
                </Text>
              </View>

              <View style={styles.buttonGroup}>
                <TouchableOpacity
                  style={[styles.button, styles.buttonOn, !connectionStatus.isConnected && styles.buttonDisabled]}
                  onPress={turnDeviceOn}
                  disabled={loading || !connectionStatus.isConnected}
                >
                  {loading ? <ActivityIndicator color="white" /> : <Text style={styles.buttonText}>Turn ON</Text>}
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.button, styles.buttonOff, !connectionStatus.isConnected && styles.buttonDisabled]}
                  onPress={turnDeviceOff}
                  disabled={loading || !connectionStatus.isConnected}
                >
                  {loading ? <ActivityIndicator color="white" /> : <Text style={styles.buttonText}>Turn OFF</Text>}
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.button, styles.buttonRefresh]}
                  onPress={onRefresh}
                  disabled={refreshing}
                >
                  {refreshing ? <ActivityIndicator color="white" /> : <Text style={styles.buttonText}>Refresh</Text>}
                </TouchableOpacity>
              </View>
            </View>

            <View style={styles.card}>
              <Text style={styles.cardTitle}>Energy Cost Calculator</Text>

              <View style={styles.costSection}>
                <Text style={styles.costLabel}>Daily Cost (KES)</Text>
                <Text style={styles.costValue}>{dailyCost.toFixed(2)}</Text>
              </View>

              <View style={styles.costSection}>
                <Text style={styles.costLabel}>Monthly Cost (KES)</Text>
                <Text style={styles.costValue}>{monthlyCost.toFixed(2)}</Text>
              </View>

              <View style={styles.costSection}>
                <Text style={styles.costLabel}>Energy Used Today (kWh)</Text>
                <Text style={styles.costValue}>{dailyKwh.toFixed(2)}</Text>
              </View>

              <View style={styles.costSection}>
                <Text style={styles.costLabel}>Rate</Text>
                <Text style={styles.costValue}>{COST_PER_KWH} KES/kWh</Text>
              </View>
            </View>

            <View style={styles.card}>
              <Text style={styles.cardTitle}>Statistics (7 Days)</Text>

              <View style={styles.metric}>
                <Text style={styles.metricLabel}>Average Power:</Text>
                <Text style={styles.metricValue}>2500 W</Text>
              </View>

              <View style={styles.metric}>
                <Text style={styles.metricLabel}>Peak Power:</Text>
                <Text style={styles.metricValue}>4800 W</Text>
              </View>

              <View style={styles.metric}>
                <Text style={styles.metricLabel}>Data Points:</Text>
                <Text style={styles.metricValue}>672</Text>
              </View>
            </View>
          </View>
        )}

        {/* ALERTS TAB */}
        {activeTab === 'alerts' && (
          <View style={styles.tabContent}>
            <View style={styles.card}>
              <Text style={styles.cardTitle}>Register Contact</Text>

              <TextInput
                style={styles.input}
                placeholder="Email Address"
                placeholderTextColor="#999"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                editable={!loading && connectionStatus.isConnected}
              />

              <TextInput
                style={styles.input}
                placeholder="Phone Number (Optional)"
                placeholderTextColor="#999"
                value={phone}
                onChangeText={setPhone}
                keyboardType="phone-pad"
                editable={!loading && connectionStatus.isConnected}
              />

              <View style={styles.checkboxContainer}>
                <TouchableOpacity
                  style={[styles.checkbox, emailAlerts && styles.checkboxChecked]}
                  onPress={() => setEmailAlerts(!emailAlerts)}
                >
                  {emailAlerts && <Text style={styles.checkmark}>✓</Text>}
                </TouchableOpacity>
                <Text style={styles.checkboxLabel}>Receive Email Alerts</Text>
              </View>

              <View style={styles.checkboxContainer}>
                <TouchableOpacity
                  style={[styles.checkbox, smsAlerts && styles.checkboxChecked]}
                  onPress={() => setSmsAlerts(!smsAlerts)}
                >
                  {smsAlerts && <Text style={styles.checkmark}>✓</Text>}
                </TouchableOpacity>
                <Text style={styles.checkboxLabel}>Receive SMS Alerts</Text>
              </View>

              <TouchableOpacity
                style={[styles.button, styles.buttonPrimary, (!connectionStatus.isConnected || loading) && styles.buttonDisabled]}
                onPress={registerContact}
                disabled={loading || !connectionStatus.isConnected}
              >
                {loading ? (
                  <ActivityIndicator color="white" />
                ) : (
                  <Text style={styles.buttonText}>Register Contact</Text>
                )}
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.button, styles.buttonSecondary, (!connectionStatus.isConnected || loading) && styles.buttonDisabled]}
                onPress={testEmail}
                disabled={loading || !connectionStatus.isConnected}
              >
                {loading ? (
                  <ActivityIndicator color="white" />
                ) : (
                  <Text style={styles.buttonText}>Test Email</Text>
                )}
              </TouchableOpacity>
            </View>

            <View style={styles.card}>
              <Text style={styles.cardTitle}>Create Alert Rule</Text>

              <TextInput
                style={styles.input}
                placeholder="Rule Name"
                placeholderTextColor="#999"
                value={ruleName}
                onChangeText={setRuleName}
                editable={!loading && connectionStatus.isConnected}
              />

              <View style={styles.selectContainer}>
                <TouchableOpacity
                  style={styles.selectButton}
                  onPress={() => {
                    Alert.alert('Select Alert Type', 'Choose one', [
                      {
                        text: 'High Voltage (>250V)',
                        onPress: () => setRuleType('voltage_high'),
                      },
                      {
                        text: 'Low Voltage (<200V)',
                        onPress: () => setRuleType('voltage_low'),
                      },
                      {
                        text: 'High Power (>5000W)',
                        onPress: () => setRuleType('power_high'),
                      },
                    ]);
                  }}
                >
                  <Text style={styles.selectText}>
                    {ruleType === 'voltage_high'
                      ? 'High Voltage'
                      : ruleType === 'voltage_low'
                      ? 'Low Voltage'
                      : 'High Power'}
                  </Text>
                </TouchableOpacity>
              </View>

              <TextInput
                style={styles.input}
                placeholder="Threshold Value"
                placeholderTextColor="#999"
                value={ruleThreshold}
                onChangeText={setRuleThreshold}
                keyboardType="decimal-pad"
                editable={!loading && connectionStatus.isConnected}
              />

              <TouchableOpacity
                style={[styles.button, styles.buttonPrimary, (!connectionStatus.isConnected || loading) && styles.buttonDisabled]}
                onPress={createAlertRule}
                disabled={loading || !connectionStatus.isConnected}
              >
                {loading ? (
                  <ActivityIndicator color="white" />
                ) : (
                  <Text style={styles.buttonText}>Create Rule</Text>
                )}
              </TouchableOpacity>
            </View>

            <View style={styles.card}>
              <Text style={styles.cardTitle}>Active Alert Rules</Text>

              {alertRules.length > 0 ? (
                alertRules.map((rule) => renderRuleItem(rule))
              ) : (
                <Text style={styles.noDataText}>No alert rules created yet</Text>
              )}
            </View>
          </View>
        )}

        {/* RENEWABLE TAB */}
        {activeTab === 'renewable' && (
          <View style={styles.tabContent}>
            <View style={styles.card}>
              <Text style={styles.cardTitle}>Add Renewable Source</Text>

              <TextInput
                style={styles.input}
                placeholder="Source Name (e.g., Rooftop Solar)"
                placeholderTextColor="#999"
                value={renewableName}
                onChangeText={setRenewableName}
                editable={!loading && connectionStatus.isConnected}
              />

              <View style={styles.selectContainer}>
                <TouchableOpacity
                  style={styles.selectButton}
                  onPress={() => {
                    Alert.alert('Select Source Type', 'Choose one', [
                      { text: 'SOLAR', onPress: () => setRenewableType('SOLAR') },
                      { text: 'WIND', onPress: () => setRenewableType('WIND') },
                      { text: 'HYDRO', onPress: () => setRenewableType('HYDRO') },
                      { text: 'OTHER', onPress: () => setRenewableType('OTHER') },
                    ]);
                  }}
                >
                  <Text style={styles.selectText}>{renewableType}</Text>
                </TouchableOpacity>
              </View>

              <TextInput
                style={styles.input}
                placeholder="Capacity (kW)"
                placeholderTextColor="#999"
                value={renewableCapacity}
                onChangeText={setRenewableCapacity}
                keyboardType="decimal-pad"
                editable={!loading && connectionStatus.isConnected}
              />

              <TextInput
                style={styles.input}
                placeholder="Location (Optional)"
                placeholderTextColor="#999"
                value={renewableLocation}
                onChangeText={setRenewableLocation}
                editable={!loading && connectionStatus.isConnected}
              />

              <TouchableOpacity
                style={[styles.button, styles.buttonPrimary, (!connectionStatus.isConnected || loading) && styles.buttonDisabled]}
                onPress={addRenewableSource}
                disabled={loading || !connectionStatus.isConnected}
              >
                {loading ? (
                  <ActivityIndicator color="white" />
                ) : (
                  <Text style={styles.buttonText}>Add Source</Text>
                )}
              </TouchableOpacity>
            </View>

            <View style={styles.card}>
              <Text style={styles.cardTitle}>Renewable Sources</Text>

              {renewableSources.length > 0 ? (
                renewableSources.map((source) => renderSourceItem(source))
              ) : (
                <Text style={styles.noDataText}>No renewable sources added yet</Text>
              )}
            </View>
          </View>
        )}

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>Smart Grid Management System v1.0</Text>
          <Text style={styles.footerText}>Student Project - Group 2</Text>
        </View>
      </ScrollView>

      {/* Settings Modal */}
      <Modal visible={showSettings} animationType="slide" transparent={false}>
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setShowSettings(false)}>
              <Text style={styles.modalCloseButton}>✕ Close</Text>
            </TouchableOpacity>
            <Text style={styles.modalTitle}>⚙️ API Settings</Text>
            <View style={{ width: 100 }} />
          </View>

          <ScrollView style={styles.modalContent}>
            <View style={styles.settingsSection}>
              <Text style={styles.settingsSectionTitle}>API Configuration</Text>
              <Text style={styles.settingsLabel}>Current Status:</Text>
              <View
                style={[
                  styles.statusIndicator,
                  connectionStatus.isConnected ? styles.statusConnected : styles.statusDisconnected,
                ]}
              >
                <Text style={styles.statusText}>
                  {connectionStatus.isConnected ? '✅ Connected' : '🔴 Disconnected'}
                </Text>
              </View>

              <Text style={styles.settingsLabel}>API Base URL:</Text>
              <TextInput
                style={styles.settingsInput}
                placeholder="http://192.168.1.4:8000/api"
                placeholderTextColor="#666"
                value={tempApiUrl}
                onChangeText={setTempApiUrl}
              />

              <TouchableOpacity
                style={[styles.button, styles.buttonPrimary, testingConnection && styles.buttonDisabled]}
                onPress={updateApiUrl}
                disabled={testingConnection}
              >
                {testingConnection ? (
                  <View style={styles.loadingContainer}>
                    <ActivityIndicator color="white" />
                    <Text style={styles.buttonText}>Testing...</Text>
                  </View>
                ) : (
                  <Text style={styles.buttonText}>Test & Save Connection</Text>
                )}
              </TouchableOpacity>
            </View>

            <View style={styles.settingsSection}>
              <Text style={styles.settingsSectionTitle}>📋 Help</Text>
              <Text style={styles.helpText}>
                <Text style={{ fontWeight: 'bold' }}>How to find your backend IP:</Text>
                {'\n\n'}
                <Text style={{ fontWeight: 'bold' }}>Windows:</Text>
                {'\n'}1. Open Command Prompt{'\n'}
                2. Type: ipconfig{'\n'}
                3. Look for "IPv4 Address" (e.g., 192.168.1.4){'\n\n'}
                <Text style={{ fontWeight: 'bold' }}>Mac/Linux:</Text>
                {'\n'}1. Open Terminal{'\n'}
                2. Type: ifconfig{'\n'}
                3. Look for "inet" address{'\n\n'}
                <Text style={{ fontWeight: 'bold' }}>Important:</Text>
                {'\n'}• Phone and computer must be on same WiFi{'\n'}
                • Backend must be running: python manage.py runserver 0.0.0.0:8000{'\n'}
                • URL format: http://YOUR_IP:8000/api
              </Text>
            </View>

            <View style={styles.settingsSection}>
              <Text style={styles.settingsSectionTitle}>📊 Debug Info</Text>
              <View style={styles.debugCard}>
                <Text style={styles.debugText}>API URL: {apiUrl}</Text>
                <Text style={styles.debugText}>Connected: {connectionStatus.isConnected ? 'Yes' : 'No'}</Text>
                {connectionStatus.lastError && (
                  <Text style={styles.debugError}>Error: {connectionStatus.lastError}</Text>
                )}
              </View>
            </View>
          </ScrollView>
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
}

// ============== STYLES ==============
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0e27',
  },
  errorBanner: {
    backgroundColor: '#ef4444',
    paddingVertical: 10,
    paddingHorizontal: 15,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorBannerText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 14,
    textAlign: 'center',
  },
  header: {
    backgroundColor: '#667eea',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.1)',
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
    marginTop: 5,
  },
  connectedIndicator: {
    color: '#10b981',
    fontSize: 12,
    marginTop: 10,
    fontWeight: 'bold',
  },
  settingsButton: {
    width: 50,
    height: 50,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
  },
  settingsButtonText: {
    fontSize: 24,
  },
  tabsContainer: {
    flexDirection: 'row',
    backgroundColor: 'rgba(0,0,0,0.3)',
    padding: 10,
    justifyContent: 'space-around',
  },
  tab: {
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderRadius: 8,
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  activeTab: {
    backgroundColor: '#667eea',
  },
  tabText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 12,
  },
  activeTabText: {
    color: 'white',
    fontWeight: 'bold',
  },
  tabContent: {
    padding: 10,
  },
  card: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 15,
    padding: 15,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#667eea',
    marginBottom: 15,
  },
  metric: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.1)',
  },
  metricLabel: {
    color: '#aaa',
    fontWeight: '600',
  },
  metricValue: {
    color: '#00d4ff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  buttonGroup: {
    flexDirection: 'row',
    gap: 10,
    marginTop: 15,
    flexWrap: 'wrap',
  },
  button: {
    paddingVertical: 12,
    paddingHorizontal: 15,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1,
    minWidth: '30%',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonOn: {
    backgroundColor: '#10b981',
  },
  buttonOff: {
    backgroundColor: '#ef4444',
  },
  buttonRefresh: {
    backgroundColor: '#667eea',
  },
  buttonPrimary: {
    backgroundColor: '#667eea',
    marginTop: 10,
  },
  buttonSecondary: {
    backgroundColor: '#764ba2',
    marginTop: 10,
  },
  buttonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 14,
  },
  input: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderWidth: 1,
    borderColor: '#667eea',
    borderRadius: 8,
    padding: 12,
    color: 'white',
    marginBottom: 10,
    fontSize: 14,
  },
  selectContainer: {
    marginBottom: 10,
  },
  selectButton: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderWidth: 1,
    borderColor: '#667eea',
    borderRadius: 8,
    padding: 12,
  },
  selectText: {
    color: 'white',
    fontSize: 14,
  },
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#667eea',
    marginRight: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkboxChecked: {
    backgroundColor: '#667eea',
  },
  checkmark: {
    color: 'white',
    fontWeight: 'bold',
  },
  checkboxLabel: {
    color: 'white',
    fontSize: 14,
  },
  costSection: {
    backgroundColor: 'rgba(102, 126, 234, 0.1)',
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
  },
  costLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5,
  },
  costValue: {
    color: '#10b981',
    fontSize: 22,
    fontWeight: 'bold',
  },
  ruleItem: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#667eea',
  },
  ruleName: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 14,
  },
  ruleType: {
    color: '#aaa',
    fontSize: 12,
    marginTop: 3,
  },
  ruleThreshold: {
    color: '#00d4ff',
    fontSize: 12,
    marginTop: 3,
  },
  sourceItem: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#10b981',
  },
  sourceName: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 14,
  },
  sourceType: {
    color: '#aaa',
    fontSize: 12,
    marginTop: 3,
  },
  sourceCapacity: {
    color: '#00d4ff',
    fontSize: 12,
    marginTop: 3,
  },
  sourceLocation: {
    color: '#667eea',
    fontSize: 12,
    marginTop: 3,
  },
  noDataText: {
    color: '#aaa',
    textAlign: 'center',
    paddingVertical: 20,
  },
  footer: {
    padding: 20,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.1)',
  },
  footerText: {
    color: 'rgba(255,255,255,0.5)',
    fontSize: 12,
  },
  // Settings Modal Styles
  modalContainer: {
    flex: 1,
    backgroundColor: '#0a0e27',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#667eea',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.1)',
  },
  modalCloseButton: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  modalTitle: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  modalContent: {
    flex: 1,
    padding: 15,
  },
  settingsSection: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 15,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  settingsSectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#667eea',
    marginBottom: 12,
  },
  settingsLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 8,
    fontWeight: '600',
  },
  settingsInput: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderWidth: 1,
    borderColor: '#667eea',
    borderRadius: 8,
    padding: 12,
    color: 'white',
    marginBottom: 12,
    fontSize: 14,
  },
  statusIndicator: {
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  statusConnected: {
    backgroundColor: 'rgba(16, 185, 129, 0.2)',
    borderWidth: 1,
    borderColor: '#10b981',
  },
  statusDisconnected: {
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
    borderWidth: 1,
    borderColor: '#ef4444',
  },
  statusText: {
    fontWeight: 'bold',
    fontSize: 14,
    color: 'white',
  },
  helpText: {
    color: '#ccc',
    fontSize: 13,
    lineHeight: 20,
  },
  debugCard: {
    backgroundColor: 'rgba(0,0,0,0.3)',
    borderRadius: 8,
    padding: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  debugText: {
    color: '#00d4ff',
    fontSize: 12,
    marginBottom: 8,
    fontFamily: 'monospace',
  },
  debugError: {
    color: '#ef4444',
    fontSize: 12,
    marginBottom: 8,
    fontFamily: 'monospace',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
});
