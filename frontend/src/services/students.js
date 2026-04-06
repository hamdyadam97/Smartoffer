import api from './api';

export const studentService = {
  getAll: async (params = {}) => {
    const response = await api.get('/students/', { params });
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/students/${id}/`);
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/students/', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/students/${id}/`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/students/${id}/`);
    return response.data;
  },
  
  searchByMobile: async (mobile) => {
    const response = await api.get('/students/by_mobile/', { params: { mobile } });
    return response.data;
  }
};
