// src/api.js
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000
});

export async function predictImage(file) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('include_recommendations', 'true');

  const response = await api.post('/predict/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });

  return response.data;
}

export async function predictText(text) {
  const formData = new FormData();
  formData.append('text', text);
  formData.append('include_recommendations', 'true');

  const response = await api.post('/predict/text', formData);

  return response.data;
}

export async function getRecommendation(diseaseClass, confidence = 0.95) {
  const response = await api.get(`/recommend/${encodeURIComponent(diseaseClass)}`, {
    params: { confidence }
  });
  return response.data;
}

export async function submitFeedback({ disease, recommendationId, rating, wasHelpful, comment }) {
  const data = new URLSearchParams();
  data.append('disease_class', disease);
  data.append('recommendation_id', recommendationId);
  data.append('rating', rating);
  data.append('was_helpful', wasHelpful);
  if (comment) {
    data.append('user_comment', comment);
  }
  await api.post('/feedback', data.toString(), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
}

export async function getAnalytics() {
  const response = await api.get('/analytics');
  return response.data;
}

export async function getPopularDiseases() {
  const response = await api.get('/analytics/popular');
  return response.data;
}

export async function clearCache() {
  const response = await api.post('/cache/clear');
  return response.data;
}

export async function saveKnowledgeBase() {
  const response = await api.post('/recommend/save');
  return response.data;
}

export default api;
