import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService.js';
import { storage } from '../storage/asyncStorage.js';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function restoreSession() {
      try {
        const currentUser = await storage.getItem('@tradeflow_user');
        const tokens = await storage.getItem('@tradeflow_tokens');
        if (currentUser && tokens?.access) {
          setUser(currentUser);
        }
      } catch (e) {
        console.warn('Session restoration failed:', e);
      } finally {
        setLoading(false);
      }
    }
    restoreSession();
  }, []);

  const login = async (phone, password) => {
    const { user: loggedInUser } = await authService.login(phone, password);
    setUser(loggedInUser);
    return loggedInUser;
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
