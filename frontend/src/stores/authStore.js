import { create } from 'zustand';
import { authService } from '../services/auth';

export const useAuthStore = create((set, get) => ({
  user: null,
  isLoading: false,
  error: null,
  isAuthenticated: false,
  
  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      await authService.login(email, password);
      const user = await authService.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
      return true;
    } catch (error) {
      set({ 
        error: error.response?.data?.detail || 'فشل تسجيل الدخول', 
        isLoading: false 
      });
      return false;
    }
  },
  
  logout: () => {
    authService.logout();
    set({ user: null, isAuthenticated: false, error: null });
  },
  
  fetchUser: async () => {
    if (!authService.isAuthenticated()) return;
    
    set({ isLoading: true });
    try {
      const user = await authService.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ user: null, isAuthenticated: false, isLoading: false });
      authService.logout();
    }
  },
  
  clearError: () => set({ error: null })
}));
