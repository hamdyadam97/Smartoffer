import api from './api';

export const paymentService = {
  getAll: async (params = {}) => {
    const response = await api.get('/payments/', { params });
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/payments/${id}/`);
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/payments/', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/payments/${id}/`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/payments/${id}/`);
    return response.data;
  }
};

export const offerService = {
  getAll: async (params = {}) => {
    const response = await api.get('/offers/', { params });
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/offers/${id}/`);
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/offers/', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/offers/${id}/`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/offers/${id}/`);
    return response.data;
  },
  
  getByBranch: async (branchId) => {
    const response = await api.get('/offers/by_branch/', { params: { branch_id: branchId } });
    return response.data;
  }
};
