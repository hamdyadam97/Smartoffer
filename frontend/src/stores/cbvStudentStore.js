import { create } from 'zustand';
import { studentsApi } from '../services/cbvApi';

export const useCBVStudentStore = create((set, get) => ({
  students: [],
  currentStudent: null,
  isLoading: false,
  error: null,
  
  fetchStudents: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response = await studentsApi.getAll(params);
      const data = response.data.results || response.data || [];
      set({ students: data, isLoading: false });
      return data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  getStudent: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const response = await studentsApi.getById(id);
      set({ currentStudent: response.data, isLoading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  createStudent: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await studentsApi.create(data);
      set({ isLoading: false });
      await get().fetchStudents();
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  updateStudent: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await studentsApi.update(id, data);
      set({ isLoading: false });
      await get().fetchStudents();
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  deleteStudent: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await studentsApi.delete(id);
      set({ isLoading: false });
      await get().fetchStudents();
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  getStudentCourses: async (id) => {
    try {
      const response = await studentsApi.getCourses(id);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  clearError: () => set({ error: null }),
  clearCurrent: () => set({ currentStudent: null })
}));
