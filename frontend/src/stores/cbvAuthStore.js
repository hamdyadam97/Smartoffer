import { create } from 'zustand';
import { authApi } from '../services/cbvApi';

export const useCBVAuthStore = create((set, get) => ({
  user: null,
  isLoading: false,
  error: null,
  isAuthenticated: false,
  
  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authApi.login({ email, password });
      localStorage.setItem('accessToken', response.data.access);
      localStorage.setItem('refreshToken', response.data.refresh);
      set({ user: response.data.user, isAuthenticated: true, isLoading: false });
      return true;
    } catch (error) {
      set({ 
        error: error.response?.data?.detail || 'فشل تسجيل الدخول', 
        isLoading: false 
      });
      return false;
    }
  },
  
  logout: async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        await authApi.logout({ refresh: refreshToken });
      }
    } catch (error) {
      console.error('Logout error:', error);
    }
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    set({ user: null, isAuthenticated: false, error: null });
  },
  
  fetchUser: async () => {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      set({ user: null, isAuthenticated: false, isLoading: false });
      return;
    }
    
    set({ isLoading: true });
    try {
      const response = await authApi.getMe();
      set({ user: response.data, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ user: null, isAuthenticated: false, isLoading: false });
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    }
  },
  
  clearError: () => set({ error: null })
}));
