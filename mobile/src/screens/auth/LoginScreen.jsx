import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { useAuth } from '../../hooks/useAuth.js';

export function LoginScreen() {
  const { login } = useAuth();
  const [phone, setPhone] = useState('+251911223344');
  const [password, setPassword] = useState('TradeFlow2026!');
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleLogin = async () => {
    if (!phone || !password) {
      setErrorMsg('Please enter both phone number and password');
      return;
    }
    setSubmitting(true);
    setErrorMsg('');
    try {
      await login(phone, password);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || err.message || 'Driver authentication failed.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.logoText}>TradeFlow</Text>
        <Text style={styles.appSubtitle}>Driver Corridor Portal</Text>

        {errorMsg ? (
          <View style={styles.errorBox}>
            <Text style={styles.errorText}>{errorMsg}</Text>
          </View>
        ) : null}

        <View style={styles.formGroup}>
          <Text style={styles.label}>Driver Phone Number</Text>
          <TextInput
            style={styles.input}
            value={phone}
            onChangeText={setPhone}
            placeholder="+2519..."
            placeholderTextColor="#64748b"
            keyboardType="phone-pad"
            autoCapitalize="none"
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Password</Text>
          <TextInput
            style={styles.input}
            value={password}
            onChangeText={setPassword}
            placeholder="••••••••"
            placeholderTextColor="#64748b"
            secureTextEntry
          />
        </View>

        <TouchableOpacity style={styles.loginBtn} onPress={handleLogin} disabled={submitting}>
          {submitting ? (
            <ActivityIndicator color="#ffffff" />
          ) : (
            <Text style={styles.loginBtnText}>Driver Sign In ➔</Text>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#020617',
    justifyContent: 'center',
    padding: 20,
  },
  card: {
    backgroundColor: '#0f172a',
    borderRadius: 20,
    padding: 24,
    borderWidth: 1,
    borderColor: '#1e293b',
  },
  logoText: {
    fontSize: 28,
    fontWeight: '900',
    color: '#00f2fe',
    textAlign: 'center',
  },
  appSubtitle: {
    fontSize: 13,
    color: '#94a3b8',
    textAlign: 'center',
    marginBottom: 20,
    fontWeight: '600',
  },
  errorBox: {
    backgroundColor: 'rgba(244, 63, 94, 0.15)',
    padding: 10,
    borderRadius: 10,
    borderColor: 'rgba(244, 63, 94, 0.3)',
    borderWidth: 1,
    marginBottom: 14,
  },
  errorText: {
    color: '#fda4af',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  formGroup: {
    marginBottom: 14,
  },
  label: {
    color: '#cbd5e1',
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 6,
  },
  input: {
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 14,
    color: '#ffffff',
    fontSize: 14,
    borderWidth: 1,
    borderColor: '#334155',
  },
  loginBtn: {
    backgroundColor: '#0284c7',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  loginBtnText: {
    color: '#ffffff',
    fontSize: 15,
    fontWeight: '800',
  },
});
