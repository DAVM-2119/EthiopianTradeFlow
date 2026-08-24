import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from './endpoints.js';
import { storage } from '../storage/asyncStorage.js';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

apiClient.interceptors.request.use(
  async (config) => {
    const tokens = await storage.getItem('@tradeflow_tokens');
    if (tokens?.access) {
      config.headers.Authorization = `Bearer ${tokens.access}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const tokens = await storage.getItem('@tradeflow_tokens');
        if (tokens?.refresh) {
          const res = await axios.post(`${API_BASE_URL}${API_ENDPOINTS.REFRESH_TOKEN}`, {
            refresh: tokens.refresh,
          });
          const newAccess = res.data?.access || res.data?.data?.access;
          if (newAccess) {
            const updatedTokens = { ...tokens, access: newAccess };
            await storage.setItem('@tradeflow_tokens', updatedTokens);
            originalRequest.headers.Authorization = `Bearer ${newAccess}`;
            return apiClient(originalRequest);
          }
        }
      } catch (refreshErr) {
        await storage.removeItem('@tradeflow_tokens');
        await storage.removeItem('@tradeflow_user');
      }
    }
    return Promise.reject(error);
  }
);
