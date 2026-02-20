import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
});

export const getCompanies = () => api.get('/companies');
export const getStats = () => api.get('/scoring/stats');
export const scoreCompany = (id) => api.post(`/scoring/company/${id}/score`);

export default api;
