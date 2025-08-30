import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Save } from 'lucide-react';
import api, { type CreateProjectRequest, type ApiResponse, type Project } from '@/lib/api';
import { toast } from 'sonner';
import Layout from '@/components/Layout';

export default function NewProject() {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    budget: '',
    deadline: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 表单验证
    if (!formData.name || !formData.budget || !formData.deadline) {
      toast.error('请填写所有必填字段');
      return;
    }

    const budget = parseFloat(formData.budget);
    if (isNaN(budget) || budget <= 0) {
      toast.error('请输入有效的预算金额');
      return;
    }

    const deadline = new Date(formData.deadline);
    if (deadline <= new Date()) {
      toast.error('截止日期必须是未来的日期');
      return;
    }

    setIsLoading(true);
    try {
      const projectData: CreateProjectRequest = {
        name: formData.name,
        description: formData.description || undefined,
        budget: budget,
        deadline: formData.deadline
      };

      const response = await api.post<ApiResponse<{ project: Project }>>(
        '/projects',
        projectData
      );

      if (response.data.success && response.data.data) {
        toast.success('项目创建成功！');
        navigate(`/projects/${response.data.data.project.id}`);
      } else {
        toast.error(response.data.message || '创建失败');
      }
    } catch (error: any) {
      console.error('Failed to create project:', error);
      toast.error(error.response?.data?.message || '创建失败，请检查网络连接');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow">
          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            {/* 项目名称 */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                项目名称 <span className="text-red-500">*</span>
              </label>
              <input
                id="name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入项目名称"
                required
              />
            </div>

            {/* 项目描述 */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                项目描述
              </label>
              <textarea
                id="description"
                name="description"
                rows={4}
                value={formData.description}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入项目描述（可选）"
              />
            </div>

            {/* 预算金额 */}
            <div>
              <label htmlFor="budget" className="block text-sm font-medium text-gray-700 mb-2">
                预算金额 (CNY) <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">¥</span>
                <input
                  id="budget"
                  name="budget"
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.budget}
                  onChange={handleInputChange}
                  className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="0.00"
                  required
                />
              </div>
              <p className="text-sm text-gray-500 mt-1">请输入项目的总预算金额</p>
            </div>

            {/* 截止日期 */}
            <div>
              <label htmlFor="deadline" className="block text-sm font-medium text-gray-700 mb-2">
                截止日期 <span className="text-red-500">*</span>
              </label>
              <input
                id="deadline"
                name="deadline"
                type="date"
                value={formData.deadline}
                onChange={handleInputChange}
                min={new Date().toISOString().split('T')[0]}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <p className="text-sm text-gray-500 mt-1">项目的截止日期</p>
            </div>

            {/* 提交按钮 */}
            <div className="flex justify-end gap-4 pt-6 border-t border-gray-200">
              <Link
                to="/projects"
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                取消
              </Link>
              <button
                type="submit"
                disabled={isLoading}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
                {isLoading ? '创建中...' : '创建项目'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
}