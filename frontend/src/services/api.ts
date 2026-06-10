import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
  me: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  }
};

export const chatAPI = {
  sendMessage: async (message: string, sessionId: string, language: string = 'en') => {
    const response = await api.post('/chat', { message, session_id: sessionId, language });
    return response.data;
  }
};

export const networkAPI = {
  getGraph: async (crimeId?: number, criminalName?: string) => {
    const response = await api.post('/network/graph', { crime_id: crimeId, criminal_name: criminalName });
    return response.data;
  }
};

export const predictionsAPI = {
  getForecast: async (district: string, days: number = 30) => {
    const response = await api.get(`/predictions/forecast?district=${district}&days=${days}`);
    return response.data;
  },
  getHotspots: async (crimeType: string) => {
    const response = await api.get(`/predictions/hotspots?crime_type=${crimeType}`);
    return response.data;
  },
  getAlerts: async () => {
    const response = await api.get('/predictions/alerts');
    return response.data;
  }
};

export const exportAPI = {
  generatePDF: async (chatHistory: any[], userId: number, role: string) => {
    const response = await api.post('/export/pdf', { chat_history: chatHistory, user_id: userId, role }, { responseType: 'blob' });
    
    // Auto download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'drishti_report.pdf');
    document.body.appendChild(link);
    link.click();
    link.remove();
  }
};
