import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeGitHubProfile = async (username) => {
  const response = await api.post('/api/analyze', { username });
  return response.data;
};

export const getGitHubRepos = async (username) => {
  const response = await api.get(`/api/github/${username}/repos`);
  return response.data;
};

export default api;