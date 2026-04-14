import { create } from 'zustand';
import { accountsApi } from '../services/cbvApi';

export const useCBVRegistrationStore = create((set, get) => ({
  registrations: [],
  summary: null,
  currentRegistration: null,
  isLoading: false,
  error: null,
  
  fetchRegistrations: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response = await accountsApi.getAll(params);
      const data = response.data.results || response.data || [];
      set({ registrations: data, isLoading: false });
      return data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  fetchSummary: async () => {
    try {
      const response = await accountsApi.getSummary();
      set({ summary: response.data });
      return response.data;
    } catch (error) {
      console.error('Error fetching summary:', error);
      return null;
    }
  },
  
  getRegistration: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const response = await accountsApi.getById(id);
      set({ currentRegistration: response.data, isLoading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  createRegistration: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await accountsApi.create(data);
      set({ isLoading: false });
      await get().fetchRegistrations();
      await get().fetchSummary();
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  updateRegistration: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await accountsApi.update(id, data);
      set({ isLoading: false });
      await get().fetchRegistrations();
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  deleteRegistration: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await accountsApi.delete(id);
      set({ isLoading: false });
      await get().fetchRegistrations();
      await get().fetchSummary();
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  getPayments: async (id) => {
    try {
      const response = await accountsApi.getPayments(id);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  clearError: () => set({ error: null }),
  clearCurrent: () => set({ currentRegistration: null })
}));
