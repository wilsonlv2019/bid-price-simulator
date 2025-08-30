import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api, { type ApiResponse } from '@/lib/api';

export interface User {
  id: string;
  email: string;
  name: string;
  user_type: 'normal' | 'enterprise' | 'admin';
  created_at: string;
  updated_at: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isInitialized: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
  checkAuth: () => Promise<boolean>;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isInitialized: false,
      login: (user: User, token: string) => {
        set({ user, token, isAuthenticated: true });
      },
      logout: () => {
        set({ user: null, token: null, isAuthenticated: false });
        // 清除localStorage中的token
        localStorage.removeItem('auth-storage');
      },
      updateUser: (userData: Partial<User>) => {
        const currentUser = get().user;
        if (currentUser) {
          set({ user: { ...currentUser, ...userData } });
        }
      },
      checkAuth: async () => {
        const { token } = get();
        if (!token) {
          return false;
        }

        try {
          // 验证token是否有效
          const response = await api.get<ApiResponse<{ user: User }>>('/auth/me', {
            headers: {
              Authorization: `Bearer ${token}`
            }
          });

          if (response.data.success && response.data.data) {
            const { user } = response.data.data;
            set({ user, isAuthenticated: true });
            return true;
          } else {
            // token无效，清除状态
            get().logout();
            return false;
          }
        } catch (error) {
          console.error('Token validation failed:', error);
          // token验证失败，清除状态
          get().logout();
          return false;
        }
      },
      initialize: async () => {
        const { token } = get();
        if (token) {
          try {
            await get().checkAuth();
          } catch (error) {
            console.warn('Auth check failed during initialization, continuing without authentication:', error);
            // 如果API不可用，清除认证状态但继续初始化
            set({ user: null, token: null, isAuthenticated: false });
          }
        }
        set({ isInitialized: true });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);