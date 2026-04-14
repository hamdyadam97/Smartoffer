import { create } from 'zustand';
import { offersApi } from '../services/cbvApi';

export const useCBVOfferStore = create((set, get) => ({
  offers: [],
  currentOffer: null,
  isLoading: false,
  error: null,
  
  fetchOffers: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response = await offersApi.getAll(params);
      const data = response.data.results || response.data || [];
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
      const response = await offersApi.getById(id);
      set({ currentOffer: response.data, isLoading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  createOffer: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await offersApi.create(data);
      set({ isLoading: false });
      await get().fetchOffers();
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  updateOffer: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await offersApi.update(id, data);
      set({ isLoading: false });
      await get().fetchOffers();
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  deleteOffer: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await offersApi.delete(id);
      set({ isLoading: false });
      await get().fetchOffers();
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  convertOffer: async (id) => {
    try {
      const response = await offersApi.convert(id);
      await get().fetchOffers();
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  clearError: () => set({ error: null }),
  clearCurrent: () => set({ currentOffer: null })
}));
