import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:3002/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理认证错误
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token过期或无效，清除认证状态
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// API接口类型定义
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  user_type: 'normal' | 'enterprise' | 'admin';
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  user_type?: 'normal' | 'enterprise';
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  budget: number;
  deadline: string;
  status: 'active' | 'completed' | 'cancelled';
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  budget: number;
  deadline: string;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  budget?: number;
  deadline?: string;
  status?: 'active' | 'completed' | 'cancelled';
}

export interface Simulation {
  id: string;
  project_id: string;
  base_price: number;
  competitor_count: number;
  market_conditions: 'excellent' | 'good' | 'fair' | 'poor';
  risk_level: 'low' | 'medium' | 'high';
  created_at: string;
}

export interface SimulationResult {
  id: string;
  simulation_id: string;
  recommended_price: number;
  win_probability: number;
  profit_margin: number;
  risk_score: number;
  created_at: string;
}

export interface CreateSimulationRequest {
  project_id: string;
  base_price: number;
  competitor_count: number;
  market_conditions: 'excellent' | 'good' | 'fair' | 'poor';
  risk_level: 'low' | 'medium' | 'high';
}