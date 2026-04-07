import axios, { AxiosError } from 'axios';
import type { ApiError } from '../types/index';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
axiosInstance.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.data?.detail) {
      const apiError = new Error(error.response.data.detail);
      return Promise.reject(apiError);
    }
    if (error.message === 'Network Error') {
      return Promise.reject(new Error('Network error. Unable to reach the server.'));
    }
    return Promise.reject(
      new Error(error.message || 'An unexpected error occurred')
    );
  }
);

export default axiosInstance;
