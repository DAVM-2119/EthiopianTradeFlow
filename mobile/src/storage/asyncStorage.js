let AsyncStorageNative;
try {
  AsyncStorageNative = require('@react-native-async-storage/async-storage').default;
} catch (e) {
  // Node test environment fallback
  const mockStore = {};
  AsyncStorageNative = {
    getItem: async (key) => mockStore[key] || null,
    setItem: async (key, val) => {
      mockStore[key] = val;
    },
    removeItem: async (key) => {
      delete mockStore[key];
    },
  };
}

export const storage = {
  async getItem(key) {
    try {
      const value = await AsyncStorageNative.getItem(key);
      return value ? JSON.parse(value) : null;
    } catch (e) {
      console.warn(`Storage getItem error for key ${key}:`, e);
      return null;
    }
  },

  async setItem(key, value) {
    try {
      await AsyncStorageNative.setItem(key, JSON.stringify(value));
    } catch (e) {
      console.warn(`Storage setItem error for key ${key}:`, e);
    }
  },

  async removeItem(key) {
    try {
      await AsyncStorageNative.removeItem(key);
    } catch (e) {
      console.warn(`Storage removeItem error for key ${key}:`, e);
    }
  },
};
