import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Filter, Edit, Trash2, Eye, Calendar, DollarSign } from 'lucide-react';
import api, { type Project, type ApiResponse } from '@/lib/api';
import { toast } from 'sonner';
import Layout from '@/components/Layout';

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    fetchProjects();
  }, [currentPage, searchTerm, statusFilter]);

  const fetchProjects = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: itemsPerPage.toString(),
        ...(searchTerm && { search: searchTerm }),
        ...(statusFilter !== 'all' && { status: statusFilter })
      });

      const response = await api.get<ApiResponse<{ projects: Project[]; total: number }>>(
        `/projects?${params}`
      );
      
      if (response.data.success && response.data.data) {
        setProjects(response.data.data.projects);
        setTotalPages(Math.ceil(response.data.data.total / itemsPerPage));
      }
    } catch (error: any) {
      console.error('Failed to fetch projects:', error);
      toast.error('获取项目列表失败');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (projectId: string) => {
    if (!confirm('确定要删除这个项目吗？此操作不可撤销。')) {
      return;
    }

    try {
      const response = await api.delete<ApiResponse>(`/projects/${projectId}`);
      if (response.data.success) {
        toast.success('项目删除成功');
        fetchProjects();
      } else {
        toast.error(response.data.message || '删除失败');
      }
    } catch (error: any) {
      console.error('Failed to delete project:', error);
      toast.error(error.response?.data?.message || '删除失败');
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-CN');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return '进行中';
      case 'completed':
        return '已完成';
      case 'cancelled':
        return '已取消';
      default:
        return '未知';
    }
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="搜索项目名称..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-400" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">全部状态</option>
                <option value="active">进行中</option>
                <option value="completed">已完成</option>
                <option value="cancelled">已取消</option>
              </select>
            </div>
          </div>
        </div>

        {/* Projects List */}
        <div className="bg-white rounded-lg shadow">
          {isLoading ? (
            <div className="p-8 text-center text-gray-500">加载中...</div>
          ) : projects.length === 0 ? (
            <div className="p-8 text-center">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Plus className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">暂无项目</h3>
              <p className="text-gray-500 mb-4">开始创建您的第一个投标项目</p>
              <Link
                to="/projects/new"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                新建项目
              </Link>
            </div>
          ) : (
            <>
              {/* Desktop Table View */}
              <div className="hidden md:block">
                <div className="divide-y divide-gray-200">
                  {projects.map((project) => (
                    <div key={project.id} className="p-6 hover:bg-gray-50 transition-colors">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-lg font-medium text-gray-900">
                              {project.name}
                            </h3>
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(project.status)}`}>
                              {getStatusText(project.status)}
                            </span>
                          </div>
                          {project.description && (
                            <p className="text-gray-600 mb-3">{project.description}</p>
                          )}
                          <div className="flex items-center gap-6 text-sm text-gray-500">
                            <div className="flex items-center gap-1">
                              <DollarSign className="w-4 h-4" />
                              预算：{formatCurrency(project.budget)}
                            </div>
                            <div className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              截止：{formatDate(project.deadline)}
                            </div>
                            <div>
                              创建：{formatDate(project.created_at)}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Link
                            to={`/projects/${project.id}`}
                            className="text-blue-600 hover:text-blue-500 text-sm font-medium px-3 py-1 rounded border border-blue-200 hover:border-blue-300 transition-colors"
                          >
                            查看详情
                          </Link>
                          <Link
                            to={`/projects/${project.id}/edit`}
                            className="text-gray-600 hover:text-gray-500 p-2 rounded hover:bg-gray-100 transition-colors"
                            title="编辑项目"
                          >
                            <Edit className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => handleDelete(project.id)}
                            className="text-red-600 hover:text-red-500 p-2 rounded hover:bg-red-50 transition-colors"
                            title="删除项目"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                          <Link
                            to={`/projects/${project.id}/simulation`}
                            className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors"
                          >
                            开始模拟
                          </Link>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Mobile Card View */}
              <div className="md:hidden divide-y divide-gray-200">
                {projects.map((project) => (
                  <div key={project.id} className="p-4">
                    <div className="space-y-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="text-lg font-medium text-gray-900 mb-1">
                            {project.name}
                          </h3>
                          <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(project.status)}`}>
                            {getStatusText(project.status)}
                          </span>
                        </div>
                      </div>
                      
                      {project.description && (
                        <p className="text-gray-600 text-sm">{project.description}</p>
                      )}
                      
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                          <DollarSign className="w-4 h-4" />
                          <span>预算：{formatCurrency(project.budget)}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                          <Calendar className="w-4 h-4" />
                          <span>截止：{formatDate(project.deadline)}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                        <Link
                          to={`/projects/${project.id}`}
                          className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                        >
                          查看详情
                        </Link>
                        <div className="flex items-center gap-2">
                          <Link
                            to={`/projects/${project.id}/edit`}
                            className="text-gray-600 hover:text-gray-700 p-2 rounded hover:bg-gray-100"
                          >
                            <Edit className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => handleDelete(project.id)}
                            className="text-red-600 hover:text-red-700 p-2 rounded hover:bg-red-50"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="px-6 py-4 border-t border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-500">
                      第 {currentPage} 页，共 {totalPages} 页
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                        disabled={currentPage === 1}
                        className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        上一页
                      </button>
                      <button
                        onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                        disabled={currentPage === totalPages}
                        className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        下一页
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </Layout>
  );
}