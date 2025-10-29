import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Reviews
  getReviews: (params = {}) => api.get('/reviews/', { params }),
  createReview: (data) => api.post('/reviews/', data),
  
  // Products
  getProducts: (params = {}) => api.get('/products/', { params }),
  getProduct: (id) => api.get(`/products/${id}`),
  createProduct: (data) => api.post('/products/', data),
  
  // Sentiment Analysis
  analyzeSentiment: (data) => api.post('/analyze-sentiment/', data),
  
  // Recommendations
  getCollaborativeRecommendations: (userId, topN = 10) => 
    api.get(`/recommendations/collaborative/${userId}`, { params: { top_n: topN } }),
  getContentRecommendations: (userId, topN = 10) => 
    api.get(`/recommendations/content/${userId}`, { params: { top_n: topN } }),
  getHybridRecommendations: (userId, topN = 10) => 
    api.get(`/recommendations/hybrid/${userId}`, { params: { top_n: topN } }),
  getTrendingProducts: (category = null, topN = 10) => 
    api.get('/recommendations/trending/', { params: { category, top_n: topN } }),
  
  // Stats
  getDashboardStats: () => api.get('/stats/dashboard/'),
};

export default api;