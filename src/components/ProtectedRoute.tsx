import { ReactNode, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

interface ProtectedRouteProps {
  children: ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, token, logout } = useAuthStore();
  const location = useLocation();

  useEffect(() => {
    // 如果有token但未认证，可能是页面刷新后的状态
    if (token && !isAuthenticated) {
      // 这里可以添加token验证逻辑
      // 暂时假设有token就是已认证
      return;
    }

    // 如果没有token或认证失败，清除状态
    if (!token || !isAuthenticated) {
      logout();
    }
  }, [token, isAuthenticated, logout]);

  // 如果未认证，重定向到登录页面，并保存当前路径
  if (!isAuthenticated || !token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}