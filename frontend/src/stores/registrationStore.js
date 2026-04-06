import { create } from 'zustand';
import { accountService } from '../services/registrations';

export const useRegistrationStore = create((set, get) => ({
  registrations: [],
  currentRegistration: null,
  isLoading: false,
  error: null,
  
  fetchRegistrations: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response = await accountService.getAll(params);
      const data = Array.isArray(response) ? response : (response.results || []);
      set({ registrations: data, isLoading: false });
      return data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  getRegistration: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const data = await accountService.getById(id);
      set({ currentRegistration: data, isLoading: false });
      return data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  createRegistration: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const result = await accountService.create(data);
      set({ isLoading: false });
      await get().fetchRegistrations();
      return result;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  updateRegistration: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const result = await accountService.update(id, data);
      set({ isLoading: false });
      await get().fetchRegistrations();
      return result;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  deleteRegistration: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await accountService.delete(id);
      set({ isLoading: false });
      await get().fetchRegistrations();
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  clearError: () => set({ error: null }),
  clearCurrent: () => set({ currentRegistration: null })
}));
