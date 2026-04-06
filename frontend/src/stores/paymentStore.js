import { create } from 'zustand';
import { paymentService } from '../services/finance';

export const usePaymentStore = create((set, get) => ({
  payments: [],
  currentPayment: null,
  isLoading: false,
  error: null,
  
  fetchPayments: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response = await paymentService.getAll(params);
      const data = Array.isArray(response) ? response : (response.results || []);
      set({ payments: data, isLoading: false });
      return data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  getPayment: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const data = await paymentService.getById(id);
      set({ currentPayment: data, isLoading: false });
      return data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  createPayment: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const result = await paymentService.create(data);
      set({ isLoading: false });
      await get().fetchPayments();
      return result;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  updatePayment: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const result = await paymentService.update(id, data);
      set({ isLoading: false });
      await get().fetchPayments();
      return result;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  deletePayment: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await paymentService.delete(id);
      set({ isLoading: false });
      await get().fetchPayments();
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  clearError: () => set({ error: null }),
  clearCurrent: () => set({ currentPayment: null })
}));
