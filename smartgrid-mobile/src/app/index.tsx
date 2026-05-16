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
} from 'react-native';

const API_BASE = 'http://192.168.1.3:8000/api';
const COST_PER_KWH = 25;

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

type TabType = 'dashboard' | 'alerts' | 'renewable';
type RuleType = 'voltage_high' | 'voltage_low' | 'power_high';
type RenewableType = 'SOLAR' | 'WIND' | 'HYDRO' | 'OTHER';

// ============== HELPER FUNCTIONS ==============
/**
 * Fetch helper with error handling and status checking
 */
async function fetchWithErrorHandling<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data as T;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    console.error(`Fetch error at ${url}:`, errorMessage);
    throw error;
  }
}

// ============== MAIN COMPONENT ==============
export default function SmartGridApp() {
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

  // ========== DATA FETCHING FUNCTIONS ==========

  /**
   * Fetch latest grid data from API
   */
  const fetchLatestData = async (): Promise<void> => {
    try {
      const response = await fetchWithErrorHandling<ApiResponse<GridData>>(
        `${API_BASE}/data/latest/`
      );
      
      if (response.data) {
        setPower(response.data.power || 0);
        setVoltage(response.data.voltage || 0);
        setCurrent(response.data.current || 0);
      }
    } catch (error) {
      console.error('Failed to fetch latest data:', error);
      Alert.alert('Error', 'Failed to fetch grid data. Please check your connection.');
    }
  };

  /**
   * Calculate daily and monthly costs based on power consumption
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
   * Refresh all data from APIs
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
    try {
      setLoading(true);
      const response = await fetchWithErrorHandling<ApiResponse<unknown>>(
        `${API_BASE}/device/on/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        }
      );
      
      if (response.success) {
        setDeviceStatus('ON');
        Alert.alert('Success', 'Device turned ON');
      } else {
        Alert.alert('Error', response.message || 'Failed to turn device on');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to turn device on. Please try again.');
      console.error('Turn ON error:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Turn device OFF
   */
  const turnDeviceOff = async (): Promise<void> => {
    try {
      setLoading(true);
      const response = await fetchWithErrorHandling<ApiResponse<unknown>>(
        `${API_BASE}/device/off/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        }
      );
      
      if (response.success) {
        setDeviceStatus('OFF');
        Alert.alert('Success', 'Device turned OFF');
      } else {
        Alert.alert('Error', response.message || 'Failed to turn device off');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to turn device off. Please try again.');
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
    if (!email) {
      Alert.alert('Error', 'Please enter email address');
      return;
    }
    
    try {
      setLoading(true);
      const response = await fetchWithErrorHandling<ApiResponse<unknown>>(
        `${API_BASE}/notifications/register-contact/`,
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
        Alert.alert('Success', 'Contact registered successfully');
        setEmail('');
        setPhone('');
      } else {
        Alert.alert('Error', response.message || 'Failed to register contact');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to register contact. Please try again.');
      console.error('Register contact error:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Create a new alert rule
   */
  const createAlertRule = async (): Promise<void> => {
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
        `${API_BASE}/notifications/create-rule/`,
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
        Alert.alert('Success', 'Alert rule created successfully');
        setRuleName('');
        setRuleThreshold('');
        await getAlertRules();
      } else {
        Alert.alert('Error', response.message || 'Failed to create alert rule');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to create alert rule. Please try again.');
      console.error('Create rule error:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Fetch all alert rules
   */
  const getAlertRules = async (): Promise<void> => {
    try {
      const response = await fetchWithErrorHandling<ApiResponse<AlertRule[]>>(
        `${API_BASE}/notifications/get-rules/`
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
    if (!email) {
      Alert.alert('Error', 'Please enter your email first');
      return;
    }
    
    try {
      setLoading(true);
      const response = await fetchWithErrorHandling<ApiResponse<unknown>>(
        `${API_BASE}/notifications/test-email/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email }),
        }
      );
      
      if (response.success) {
        Alert.alert('Success', 'Test email sent successfully');
      } else {
        Alert.alert('Error', response.message || 'Failed to send test email');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to send test email. Please try again.');
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
        `${API_BASE}/renewable/add-source/`,
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
        Alert.alert('Success', 'Renewable source added successfully');
        setRenewableName('');
        setRenewableCapacity('');
        setRenewableLocation('');
        await getRenewableSources();
      } else {
        Alert.alert('Error', response.message || 'Failed to add renewable source');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to add renewable source. Please try again.');
      console.error('Add renewable source error:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Fetch all renewable sources
   */
  const getRenewableSources = async (): Promise<void> => {
    try {
      const response = await fetchWithErrorHandling<ApiResponse<RenewableSource[]>>(
        `${API_BASE}/renewable/sources/`
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
    // Fetch initial data
    fetchLatestData();
    calculateCosts();
    getAlertRules();
    getRenewableSources();

    // Set up auto-refresh interval (every 30 seconds)
    const interval = setInterval(() => {
      fetchLatestData();
      calculateCosts();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  /**
   * Recalculate costs when power changes
   */
  useEffect(() => {
    calculateCosts();
  }, [power]);

  // ========== RENDER FUNCTIONS ==========

  const renderRuleItem = (rule: AlertRule): JSX.Element => (
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

  const renderSourceItem = (source: RenewableSource): JSX.Element => (
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
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Smart Grid</Text>
        <Text style={styles.headerSubtitle}>Energy Management System</Text>
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
                style={[styles.button, styles.buttonOn]}
                onPress={turnDeviceOn}
                disabled={loading}
              >
                {loading ? <ActivityIndicator color="white" /> : <Text style={styles.buttonText}>Turn ON</Text>}
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.button, styles.buttonOff]}
                onPress={turnDeviceOff}
                disabled={loading}
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
              editable={!loading}
            />

            <TextInput
              style={styles.input}
              placeholder="Phone Number (Optional)"
              placeholderTextColor="#999"
              value={phone}
              onChangeText={setPhone}
              keyboardType="phone-pad"
              editable={!loading}
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
              style={[styles.button, styles.buttonPrimary]}
              onPress={registerContact}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="white" />
              ) : (
                <Text style={styles.buttonText}>Register Contact</Text>
              )}
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.button, styles.buttonSecondary]}
              onPress={testEmail}
              disabled={loading}
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
              editable={!loading}
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
              editable={!loading}
            />

            <TouchableOpacity
              style={[styles.button, styles.buttonPrimary]}
              onPress={createAlertRule}
              disabled={loading}
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
              editable={!loading}
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
              editable={!loading}
            />

            <TextInput
              style={styles.input}
              placeholder="Location (Optional)"
              placeholderTextColor="#999"
              value={renewableLocation}
              onChangeText={setRenewableLocation}
              editable={!loading}
            />

            <TouchableOpacity
              style={[styles.button, styles.buttonPrimary]}
              onPress={addRenewableSource}
              disabled={loading}
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
  );
}

// ============== STYLES ==============
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0e27',
  },
  header: {
    backgroundColor: '#667eea',
    padding: 20,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.1)',
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
});
