import { useAuthStore } from '@/stores/authStore';
import { Link } from 'react-router-dom';
import { Plus, FolderOpen } from 'lucide-react';
import Layout from '@/components/Layout';

export default function SimpleDashboard() {
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  console.log('SimpleDashboard 渲染');
  console.log('用户信息:', user);
  console.log('认证状态:', isAuthenticated);

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 简化的内容 */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Dashboard 测试页面</h2>
          
          <div className="space-y-4">
            <div>
              <strong>认证状态:</strong> {isAuthenticated ? '已认证' : '未认证'}
            </div>
            
            {user && (
              <div>
                <strong>用户信息:</strong>
                <pre className="bg-gray-100 p-2 rounded mt-2 text-sm">
                  {JSON.stringify(user, null, 2)}
                </pre>
              </div>
            )}
            
            <div className="pt-4">
              <p className="text-green-600 font-medium">✅ Dashboard 页面成功加载！</p>
              <p className="text-sm text-gray-600 mt-2">
                如果您看到这个页面，说明登录后的路由跳转是正常工作的。
              </p>
            </div>
            
            <div className="flex gap-4 pt-4">
              <Link
                to="/test"
                className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
              >
                返回测试页面
              </Link>
              <Link
                to="/login"
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                返回登录页
              </Link>
            </div>
          </div>
        </div>
        
        {/* 空项目状态 */}
        <div className="bg-white rounded-lg shadow mt-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">项目列表</h2>
          </div>
          <div className="p-6 text-center">
            <FolderOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">您还没有创建任何项目</p>
            <Link
              to="/projects/new"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              创建第一个项目
            </Link>
          </div>
        </div>
      </div>
    </Layout>
  );
}