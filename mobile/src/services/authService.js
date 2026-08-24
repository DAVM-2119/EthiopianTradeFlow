import { apiClient } from '../api/axios.js';
import { API_ENDPOINTS } from '../api/endpoints.js';
import { storage } from '../storage/asyncStorage.js';

export const authService = {
  async login(phone, password) {
    const res = await apiClient.post(API_ENDPOINTS.LOGIN, { phone, password });
    const data = res.data?.data || res.data;
    const tokens = { access: data.access, refresh: data.refresh };
    const user = data.user || data;

    await storage.setItem('@tradeflow_tokens', tokens);
    await storage.setItem('@tradeflow_user', user);
    return { tokens, user };
  },

  async getCurrentUser() {
    return await storage.getItem('@tradeflow_user');
  },

  async logout() {
    try {
      const tokens = await storage.getItem('@tradeflow_tokens');
      if (tokens?.refresh) {
        await apiClient.post(API_ENDPOINTS.LOGOUT, { refresh_token: tokens.refresh }).catch(() => {});
      }
    } finally {
      await storage.removeItem('@tradeflow_tokens');
      await storage.removeItem('@tradeflow_user');
    }
  },
};
