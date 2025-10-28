import axios from 'axios';
import { config } from './config';

// Create axios instance with base URL
export const api = axios.create({
  baseURL: config.apiUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper to add auth header
export const apiWithAuth = (token: string) => {
  return axios.create({
    baseURL: config.apiUrl,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });
};

export default api;
