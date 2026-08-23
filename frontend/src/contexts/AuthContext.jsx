import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/axios';
import { API_ENDPOINTS } from '../api/endpoints';
import { storage } from '../utils/storage';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(storage.getUser());
  const [loading, setLoading] = useState(true);

  const fetchProfile = async () => {
    try {
      const res = await apiClient.get(API_ENDPOINTS.ME);
      const userData = res.data?.data || res.data;
      setUser(userData);
      storage.setUser(userData);
      return userData;
    } catch (err) {
      storage.clearAuth();
      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = storage.getAccessToken();
    if (token) {
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const res = await apiClient.post(API_ENDPOINTS.LOGIN, { email, password });
    const authData = res.data?.data || res.data;

    storage.setAccessToken(authData.access);
    storage.setRefreshToken(authData.refresh);
    
    if (authData.user) {
      setUser(authData.user);
      storage.setUser(authData.user);
    } else {
      await fetchProfile();
    }
    return authData;
  };

  const register = async (userData) => {
    const res = await apiClient.post(API_ENDPOINTS.REGISTER, userData);
    const registeredData = res.data?.data || res.data;

    if (registeredData.access) {
      storage.setAccessToken(registeredData.access);
      storage.setRefreshToken(registeredData.refresh);
      if (registeredData.user) {
        setUser(registeredData.user);
        storage.setUser(registeredData.user);
      } else {
        await fetchProfile();
      }
    }
    return registeredData;
  };

  const logout = async () => {
    try {
      const refresh = storage.getRefreshToken();
      if (refresh) {
        await apiClient.post(API_ENDPOINTS.LOGOUT, { refresh });
      }
    } catch {
      // Ignore logout backend errors
    } finally {
      storage.clearAuth();
      setUser(null);
    }
  };

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    fetchProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
