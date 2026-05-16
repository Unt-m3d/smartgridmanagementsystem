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

export default function SmartGridApp() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(false);

  // Dashboard State
  const [power, setPower] = useState(0);
  const [voltage, setVoltage] = useState(0);
  const [current, setCurrent] = useState(0);
  const [deviceStatus, setDeviceStatus] = useState('ON');
  const [dailyCost, setDailyCost] = useState(0);
  const [monthlyCost, setMonthlyCost] = useState(0);
  const [dailyKwh, setDailyKwh] = useState(0);

  // Alert State
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [smsAlerts, setSmsAlerts] = useState(false);
  const [alertRules, setAlertRules] = useState([]);
  const [ruleName, setRuleName] = useState('');
  const [ruleType, setRuleType] = useState('voltage_high');
  const [ruleThreshold, setRuleThreshold] = useState('');

  // Renewable State
  const [renewableSources, setRenewableSources] = useState([]);
  const [renewableName, setRenewableName] = useState('');
  const [renewableType, setRenewableType] = useState('SOLAR');
  const [renewableCapacity, setRenewableCapacity] = useState('');
  const [renewableLocation, setRenewableLocation] = useState('');

  // Fetch latest data
  const fetchLatestData = async () => {
    try {
      const response = await fetch(`${API_BASE}/data/latest/`);
      const jsonData = await response.json();
      if (jsonData.data) {
        setPower(jsonData.data.power || 0);
        setVoltage(jsonData.data.voltage || 0);
        setCurrent(jsonData.data.current || 0);
      }
    } catch (error) {
      console.log('Error fetching data:', error);
    }
  };

  // Calculate costs
  const calculateCosts = () => {
    const avgPowerW = power || 2500;
    const dailyEnergy = (avgPowerW / 1000) * 24;
    const daily = dailyEnergy * COST_PER_KWH;
    const monthly = daily * 30;
    setDailyKwh(dailyEnergy);
    setDailyCost(daily);
    setMonthlyCost(monthly);
  };

  // Refresh all data
  const onRefresh = async () => {
    setRefreshing(true);
    await fetchLatestData();
    calculateCosts();
    await getAlertRules();
    await getRenewableSources();
    setRefreshing(false);
  };

  // Device Control
  const turnDeviceOn = async () => {
    try {
      const response = await fetch(`${API_BASE}/device/on/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const jsonData = await response.json();
      if (jsonData.success) {
        setDeviceStatus('ON');
        Alert.alert('Success', 'Device turned ON');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to turn device on');
    }
  };

  const turnDeviceOff = async () => {
    try {
      const response = await fetch(`${API_BASE}/device/off/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const jsonData = await response.json();
      if (jsonData.success) {
        setDeviceStatus('OFF');
        Alert.alert('Success', 'Device turned OFF');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to turn device off');
    }
  };

  // Alerts Functions
  const registerContact = async () => {
    if (!email) {
      Alert.alert('Error', 'Please enter email');
      return;
    }
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/notifications/register-contact/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_email: email,
          user_phone: phone,
          receive_email_alerts: emailAlerts,
          receive_sms_alerts: smsAlerts,
        }),
      });
      const jsonData = await response.json();
      if (jsonData.success) {
        Alert.alert('Success', 'Contact registered');
        setEmail('');
        setPhone('');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to register contact');
    } finally {
      setLoading(false);
    }
  };

  const createAlertRule = async () => {
    if (!ruleName || !ruleThreshold) {
      Alert.alert('Error', 'Please fill all fields');
      return;
    }
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/notifications/create-rule/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: ruleName,
          alert_type: ruleType,
          threshold: parseFloat(ruleThreshold),
        }),
      });
      const jsonData = await response.json();
      if (jsonData.success) {
        Alert.alert('Success', 'Alert rule created');
        setRuleName('');
        setRuleThreshold('');
        await getAlertRules();
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to create alert rule');
    } finally {
      setLoading(false);
    }
  };

  const getAlertRules = async () => {
    try {
      const response = await fetch(`${API_BASE}/notifications/get-rules/`);
      const jsonData = await response.json();
      if (jsonData.success && jsonData.data) {
        setAlertRules(jsonData.data);
      }
    } catch (error) {
      console.log('Error fetching alert rules:', error);
    }
  };

  const testEmail = async () => {
    if (!email) {
      Alert.alert('Error', 'Please enter your email first');
      return;
    }
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/notifications/test-email/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email }),
      });
      const jsonData = await response.json();
      if (jsonData.success) {
        Alert.alert('Success', 'Test email sent');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to send test email');
    } finally {
      setLoading(false);
    }
  };

  // Renewable Functions
  const addRenewableSource = async () => {
    if (!renewableName || !renewableCapacity) {
      Alert.alert('Error', 'Please fill all fields');
      return;
    }
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/renewable/add-source/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: renewableName,
          source_type: renewableType,
          capacity_kw: parseFloat(renewableCapacity),
          location: renewableLocation,
        }),
      });
      const jsonData = await response.json();
      if (jsonData.success) {
        Alert.alert('Success', 'Renewable source added');
        setRenewableName('');
        setRenewableCapacity('');
        setRenewableLocation('');
        await getRenewableSources();
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to add renewable source');
    } finally {
      setLoading(false);
    }
  };

  const getRenewableSources = async () => {
    try {
      const response = await fetch(`${API_BASE}/renewable/sources/`);
      const jsonData = await response.json();
      if (jsonData.success && jsonData.data) {
        setRenewableSources(jsonData.data);
      }
    } catch (error) {
      console.log('Error fetching renewable sources:', error);
    }
  };

  // Load initial data
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
  }, []);

  const renderRuleItem = (rule: any) => (
    <View key={Math.random()} style={styles.ruleItem}>
      <Text style={styles.ruleName}>{rule.name}</Text>
      <Text style={styles.ruleType}>{rule.alert_type}</Text>
      <Text style={styles.ruleThreshold}>Threshold: {rule.threshold}</Text>
    </View>
  );

  const renderSourceItem = (source: any) => (
    <View key={Math.random()} style={styles.sourceItem}>
      <Text style={styles.sourceName}>{source.name}</Text>
      <Text style={styles.sourceType}>{source.source_type}</Text>
      <Text style={styles.sourceCapacity}>Capacity: {source.capacity_kw} kW</Text>
      {source.location && (
        <Text style={styles.sourceLocation}>Location: {source.location}</Text>
      )}
    </View>
  );

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
              <TouchableOpacity style={[styles.button, styles.buttonOn]} onPress={turnDeviceOn}>
                <Text style={styles.buttonText}>Turn ON</Text>
              </TouchableOpacity>

              <TouchableOpacity style={[styles.button, styles.buttonOff]} onPress={turnDeviceOff}>
                <Text style={styles.buttonText}>Turn OFF</Text>
              </TouchableOpacity>

              <TouchableOpacity style={[styles.button, styles.buttonRefresh]} onPress={onRefresh}>
                <Text style={styles.buttonText}>Refresh</Text>
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
            />

            <TextInput
              style={styles.input}
              placeholder="Phone Number"
              placeholderTextColor="#999"
              value={phone}
              onChangeText={setPhone}
              keyboardType="phone-pad"
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
              <Text style={styles.buttonText}>Test Email</Text>
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
              alertRules.map((rule: any) => renderRuleItem(rule))
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
            />

            <TextInput
              style={styles.input}
              placeholder="Location"
              placeholderTextColor="#999"
              value={renewableLocation}
              onChangeText={setRenewableLocation}
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
              renewableSources.map((source: any) => renderSourceItem(source))
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
