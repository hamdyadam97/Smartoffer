import api from './api';

export const accountService = {
  getAll: async (params = {}) => {
    const response = await api.get('/accounts/', { params });
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/accounts/${id}/`);
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/accounts/', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/accounts/${id}/`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/accounts/${id}/`);
    return response.data;
  },
  
  getByCourse: async (courseId) => {
    const response = await api.get('/accounts/by_course/', { params: { course_id: courseId } });
    return response.data;
  },
  
  getByStudent: async (studentId) => {
    const response = await api.get('/accounts/by_student/', { params: { student_id: studentId } });
    return response.data;
  }
};
