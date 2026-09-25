import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 90000,
});

// Request interceptor: attach active access token if present
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('lms_access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: handle normalized errors and 401s
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // If unauthorized, clear stale credentials
      if (localStorage.getItem('lms_access_token')) {
        localStorage.removeItem('lms_access_token');
        localStorage.removeItem('lms_refresh_token');
        localStorage.removeItem('lms_user');
      }
    }

    const customError = {
      message: error.response?.data?.detail || error.message || 'An unexpected error occurred',
      status: error.response?.status,
      data: error.response?.data,
    };
    return Promise.reject(customError);
  }
);
