import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
});

export const uploadImages = async (files, onUploadProgress) => {
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));

  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress,
  });
  return response.data;
};

export const calibrateSession = async (sessionId) => {
  const response = await api.post(`/calibrate/${sessionId}`);
  return response.data;
};

export const startReconstruction = async (sessionId) => {
  const response = await api.post(`/reconstruct/${sessionId}`);
  return response.data;
};

export const generateMesh = async (sessionId, scale) => {
  const response = await api.post(`/mesh/${sessionId}?scale_px_per_cm=${scale}`);
  return response.data;
};

export const getPipelineStatus = async (sessionId) => {
  const response = await api.get(`/results/${sessionId}`);
  return response.data;
};

export const exportCsvUrl = (sessionId) => {
  return `${api.defaults.baseURL}/export/${sessionId}/csv`;
};
