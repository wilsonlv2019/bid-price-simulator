import { useAuthStore } from '@/stores/authStore';
import { useNavigate } from 'react-router-dom';
import api, { type LoginRequest, type ApiResponse, type User } from '@/lib/api';
import { toast } from 'sonner';
import Layout from '@/components/Layout';

export default function TestPage() {
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const token = useAuthStore((state) => state.token);
  const login = useAuthStore((state) => state.login);
  const navigate = useNavigate();

  const handleGoToDashboard = () => {
    console.log('手动跳转到Dashboard');
    navigate('/dashboard');
  };

  const handleGoToLogin = () => {
    console.log('跳转到登录页');
    navigate('/login');
  };

  const handleTestLogin = async () => {
    console.log('开始测试登录...');
    try {
      const response = await api.post<ApiResponse<{ user: User; token: string }>>(
        '/auth/login',
        { email: 'demo@example.com', password: 'password123' } as LoginRequest
      );
      
      console.log('登录响应:', response.data);
      
      if (response.data.success && response.data.data) {
        const { user, token } = response.data.data;
        console.log('登录成功，用户信息:', user);
        login(user, token);
        toast.success('测试登录成功！');
        console.log('准备跳转到 /dashboard');
        navigate('/dashboard');
        console.log('跳转命令已执行');
      } else {
        console.log('登录失败:', response.data.message);
        toast.error(response.data.message || '登录失败');
      }
    } catch (error: any) {
      console.error('测试登录错误:', error);
      toast.error(error.response?.data?.message || '登录失败');
    }
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto p-8">
        <h1 className="text-3xl font-bold mb-8">调试测试页面</h1>
        
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">认证状态</h2>
          <div className="space-y-2">
            <p><strong>是否已认证:</strong> {isAuthenticated ? '是' : '否'}</p>
            <p><strong>用户信息:</strong> {user ? JSON.stringify(user, null, 2) : '无'}</p>
            <p><strong>Token:</strong> {token ? '存在' : '不存在'}</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">路由测试</h2>
          <div className="space-x-4">
            <button 
              onClick={handleGoToDashboard}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              跳转到Dashboard
            </button>
            <button 
              onClick={handleGoToLogin}
              className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
            >
              跳转到登录页
            </button>
            <button
          onClick={handleTestLogin}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          测试登录
        </button>
        
        <button
          onClick={() => navigate('/dashboard')}
          className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
        >
          直接跳转到Dashboard
        </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">本地存储</h2>
          <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
            {JSON.stringify({
              localStorage: {
                'auth-storage': localStorage.getItem('auth-storage')
              }
            }, null, 2)}
          </pre>
        </div>
      </div>
    </Layout>
  );
}