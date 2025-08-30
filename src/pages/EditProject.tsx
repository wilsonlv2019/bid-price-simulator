import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Save } from 'lucide-react';
import api, { type Project, type ApiResponse, type UpdateProjectRequest } from '@/lib/api';
import { toast } from 'sonner';
import Layout from '@/components/Layout';

export default function EditProject() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    budget: '',
    deadline: '',
    status: 'active'
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (id) {
      fetchProject();
    }
  }, [id]);

  const fetchProject = async () => {
    if (!id) return;
    
    setIsLoading(true);
    try {
      const response = await api.get<ApiResponse<{ project: Project }>>(`/projects/${id}`);
      if (response.data.success && response.data.data) {
        const project = response.data.data.project;
        setFormData({
          name: project.name,
          description: project.description || '',
          budget: project.budget.toString(),
          deadline: project.deadline.split('T')[0], // 只取日期部分
          status: project.status
        });
      } else {
        toast.error('获取项目信息失败');
        navigate('/projects');
      }
    } catch (error: any) {
      console.error('Failed to fetch project:', error);
      toast.error('获取项目信息失败');
      navigate('/projects');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
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

    setIsSaving(true);
    try {
      const updateData: UpdateProjectRequest = {
        name: formData.name,
        description: formData.description || undefined,
        budget: budget,
        deadline: formData.deadline,
        status: formData.status as 'active' | 'completed' | 'cancelled'
      };

      const response = await api.put<ApiResponse<{ project: Project }>>(
        `/projects/${id}`,
        updateData
      );

      if (response.data.success) {
        toast.success('项目更新成功！');
        navigate(`/projects/${id}`);
      } else {
        toast.error(response.data.message || '更新失败');
      }
    } catch (error: any) {
      console.error('Failed to update project:', error);
      toast.error(error.response?.data?.message || '更新失败，请检查网络连接');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

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

            {/* 项目状态 */}
            <div>
              <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-2">
                项目状态 <span className="text-red-500">*</span>
              </label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="active">进行中</option>
                <option value="completed">已完成</option>
                <option value="cancelled">已取消</option>
              </select>
              <p className="text-sm text-gray-500 mt-1">选择项目的当前状态</p>
            </div>

            {/* 提交按钮 */}
            <div className="flex justify-end gap-4 pt-6 border-t border-gray-200">
              <Link
                to={`/projects/${id}`}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                取消
              </Link>
              <button
                type="submit"
                disabled={isSaving}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
                {isSaving ? '保存中...' : '保存更改'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
}