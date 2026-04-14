import { create } from 'zustand';
import { paymentsApi } from '../services/cbvApi';

export const useCBVPaymentStore = create((set, get) => ({
  payments: [],
  statistics: null,
  currentPayment: null,
  isLoading: false,
  error: null,
  
  fetchPayments: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response = await paymentsApi.getAll(params);
      const data = response.data.results || response.data || [];
      set({ payments: data, isLoading: false });
      return data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  fetchStatistics: async () => {
    try {
      const response = await paymentsApi.getStatistics();
      set({ statistics: response.data });
      return response.data;
    } catch (error) {
      console.error('Error fetching payment statistics:', error);
      return null;
    }
  },
  
  getPayment: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const response = await paymentsApi.getById(id);
      set({ currentPayment: response.data, isLoading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  createPayment: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await paymentsApi.create(data);
      set({ isLoading: false });
      await get().fetchPayments();
      await get().fetchStatistics();
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  deletePayment: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await paymentsApi.delete(id);
      set({ isLoading: false });
      await get().fetchPayments();
      await get().fetchStatistics();
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  clearError: () => set({ error: null }),
  clearCurrent: () => set({ currentPayment: null })
}));
