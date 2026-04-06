import { create } from 'zustand';
import { offerService } from '../services/finance';

export const useOfferStore = create((set, get) => ({
  offers: [],
  currentOffer: null,
  isLoading: false,
  error: null,
  
  fetchOffers: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response = await offerService.getAll(params);
      const data = Array.isArray(response) ? response : (response.results || []);
      set({ offers: data, isLoading: false });
      return data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  getOffer: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const data = await offerService.getById(id);
      set({ currentOffer: data, isLoading: false });
      return data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  createOffer: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const result = await offerService.create(data);
      set({ isLoading: false });
      await get().fetchOffers();
      return result;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  updateOffer: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const result = await offerService.update(id, data);
      set({ isLoading: false });
      await get().fetchOffers();
      return result;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  deleteOffer: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await offerService.delete(id);
      set({ isLoading: false });
      await get().fetchOffers();
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  clearError: () => set({ error: null }),
  clearCurrent: () => set({ currentOffer: null })
}));
