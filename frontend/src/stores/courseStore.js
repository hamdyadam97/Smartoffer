import { create } from 'zustand';
import { courseService, masterService } from '../services/courses';

export const useCourseStore = create((set, get) => ({
  courses: [],
  masters: [],
  currentCourse: null,
  currentMaster: null,
  isLoading: false,
  error: null,
  
  // Courses
  fetchCourses: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const data = await courseService.getAll(params);
      set({ courses: data, isLoading: false });
      return data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  getCourse: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const data = await courseService.getById(id);
      set({ currentCourse: data, isLoading: false });
      return data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  createCourse: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const result = await courseService.create(data);
      set({ isLoading: false });
      await get().fetchCourses();
      return result;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  updateCourse: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const result = await courseService.update(id, data);
      set({ isLoading: false });
      await get().fetchCourses();
      return result;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  deleteCourse: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await courseService.delete(id);
      set({ isLoading: false });
      await get().fetchCourses();
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  // Masters
  fetchMasters: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response = await masterService.getAll(params);
      const data = Array.isArray(response) ? response : (response.results || []);
      set({ masters: data, isLoading: false });
      return data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  getMaster: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const data = await masterService.getById(id);
      set({ currentMaster: data, isLoading: false });
      return data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  createMaster: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const result = await masterService.create(data);
      set({ isLoading: false });
      await get().fetchMasters();
      return result;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  updateMaster: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const result = await masterService.update(id, data);
      set({ isLoading: false });
      await get().fetchMasters();
      return result;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  deleteMaster: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await masterService.delete(id);
      set({ isLoading: false });
      await get().fetchMasters();
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  clearError: () => set({ error: null }),
  clearCurrent: () => set({ currentCourse: null, currentMaster: null })
}));
