import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('accessToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================================
// Authentication
// ============================================================
export const authApi = {
  login: (data) => api.post('/auth/login/', data),
  logout: (data) => api.post('/auth/logout/', data),
  getMe: () => api.get('/persons/me/'),
};

// ============================================================
// Persons (Users)
// ============================================================
export const personsApi = {
  getAll: (params) => api.get('/persons/', { params }),
  getById: (id) => api.get(`/persons/${id}/`),
  create: (data) => api.post('/persons/', data),
  update: (id, data) => api.put(`/persons/${id}/`, data),
  patch: (id, data) => api.patch(`/persons/${id}/`, data),
  delete: (id) => api.delete(`/persons/${id}/`),
};

// ============================================================
// Branches
// ============================================================
export const branchesApi = {
  getAll: (params) => api.get('/branches/', { params }),
  getActive: () => api.get('/branches/active/'),
  getById: (id) => api.get(`/branches/${id}/`),
  create: (data) => api.post('/branches/', data),
  update: (id, data) => api.put(`/branches/${id}/`, data),
  delete: (id) => api.delete(`/branches/${id}/`),
  getStatistics: (id) => api.get(`/branches/${id}/statistics/`),
};

// ============================================================
// Students
// ============================================================
export const studentsApi = {
  getAll: (params) => api.get('/students/', { params }),
  getById: (id) => api.get(`/students/${id}/`),
  create: (data) => api.post('/students/', data),
  update: (id, data) => api.put(`/students/${id}/`, data),
  delete: (id) => api.delete(`/students/${id}/`),
  getCourses: (id) => api.get(`/students/${id}/courses/`),
};

// ============================================================
// Courses
// ============================================================
export const coursesApi = {
  getAll: (params) => api.get('/courses/', { params }),
  getById: (id) => api.get(`/courses/${id}/`),
  create: (data) => api.post('/courses/', data),
  update: (id, data) => api.put(`/courses/${id}/`, data),
  delete: (id) => api.delete(`/courses/${id}/`),
  getStudents: (id) => api.get(`/courses/${id}/students/`),
  getStatistics: (id) => api.get(`/courses/${id}/statistics/`),
};

// ============================================================
// Accounts (Registrations)
// ============================================================
export const accountsApi = {
  getAll: (params) => api.get('/accounts/', { params }),
  getSummary: () => api.get('/accounts/summary/'),
  getById: (id) => api.get(`/accounts/${id}/`),
  create: (data) => api.post('/accounts/', data),
  update: (id, data) => api.put(`/accounts/${id}/`, data),
  delete: (id) => api.delete(`/accounts/${id}/`),
  getPayments: (id) => api.get(`/accounts/${id}/payments/`),
};

// ============================================================
// Payments
// ============================================================
export const paymentsApi = {
  getAll: (params) => api.get('/payments/', { params }),
  getStatistics: () => api.get('/payments/statistics/'),
  getById: (id) => api.get(`/payments/${id}/`),
  create: (data) => api.post('/payments/', data),
};

// ============================================================
// Offers
// ============================================================
export const offersApi = {
  getAll: (params) => api.get('/offers/', { params }),
  getById: (id) => api.get(`/offers/${id}/`),
  create: (data) => api.post('/offers/', data),
  update: (id, data) => api.put(`/offers/${id}/`, data),
  delete: (id) => api.delete(`/offers/${id}/`),
  convert: (id) => api.post(`/offers/${id}/convert/`),
};

export default api;
