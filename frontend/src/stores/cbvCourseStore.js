import { create } from 'zustand';
import { coursesApi, branchesApi } from '../services/cbvApi';

export const useCBVCourseStore = create((set, get) => ({
  courses: [],
  masters: [],
  branches: [],
  currentCourse: null,
  isLoading: false,
  error: null,
  
  // Courses
  fetchCourses: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response = await coursesApi.getAll(params);
      const data = response.data.results || response.data || [];
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
      const response = await coursesApi.getById(id);
      set({ currentCourse: response.data, isLoading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  createCourse: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await coursesApi.create(data);
      set({ isLoading: false });
      await get().fetchCourses();
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  updateCourse: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await coursesApi.update(id, data);
      set({ isLoading: false });
      await get().fetchCourses();
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  deleteCourse: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await coursesApi.delete(id);
      set({ isLoading: false });
      await get().fetchCourses();
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  getCourseStudents: async (id) => {
    try {
      const response = await coursesApi.getStudents(id);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  getCourseStatistics: async (id) => {
    try {
      const response = await coursesApi.getStatistics(id);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Branches (for dropdown)
  fetchBranches: async () => {
    try {
      const response = await branchesApi.getAll();
      const data = response.data.results || response.data || [];
      set({ branches: data });
      return data;
    } catch (error) {
      console.error('Error fetching branches:', error);
      return [];
    }
  },
  
  clearError: () => set({ error: null }),
  clearCurrent: () => set({ currentCourse: null })
}));
