import { create } from 'zustand';
import { studentService } from '../services/students';

export const useStudentStore = create((set, get) => ({
  students: [],
  currentStudent: null,
  isLoading: false,
  error: null,
  
  fetchStudents: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response = await studentService.getAll(params);
      const data = Array.isArray(response) ? response : (response.results || []);
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
      const data = await studentService.getById(id);
      set({ currentStudent: data, isLoading: false });
      return data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  createStudent: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const result = await studentService.create(data);
      set({ isLoading: false });
      await get().fetchStudents();
      return result;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  updateStudent: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const result = await studentService.update(id, data);
      set({ isLoading: false });
      await get().fetchStudents();
      return result;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  deleteStudent: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await studentService.delete(id);
      set({ isLoading: false });
      await get().fetchStudents();
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  clearError: () => set({ error: null }),
  clearCurrent: () => set({ currentStudent: null })
}));
