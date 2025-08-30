import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Edit, Trash2, Play, Calendar, DollarSign, User, Clock, TrendingUp } from 'lucide-react';
import api, { type Project, type Simulation, type ApiResponse } from '@/lib/api';
import { toast } from 'sonner';
import Layout from '@/components/Layout';

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [simulations, setSimulations] = useState<Simulation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (id) {
      fetchProjectData();
    }
  }, [id]);

  const fetchProjectData = async () => {
    if (!id) return;
    
    setIsLoading(true);
    try {
      // 获取项目详情
      const projectResponse = await api.get<ApiResponse<{ project: Project }>>(`/projects/${id}`);
      if (projectResponse.data.success && projectResponse.data.data) {
        setProject(projectResponse.data.data.project);
      }

      // 获取项目的模拟记录
      const simulationsResponse = await api.get<ApiResponse<{ simulations: Simulation[] }>>(
        `/simulations?projectId=${id}`
      );
      if (simulationsResponse.data.success && simulationsResponse.data.data) {
        setSimulations(simulationsResponse.data.data.simulations);
      }
    } catch (error: any) {
      console.error('Failed to fetch project data:', error);
      toast.error('获取项目信息失败');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteProject = async () => {
    if (!project || !confirm('确定要删除这个项目吗？此操作不可恢复。')) {
      return;
    }

    setIsDeleting(true);
    try {
      const response = await api.delete<ApiResponse<{}>>(`/projects/${project.id}`);
      if (response.data.success) {
        toast.success('项目删除成功');
        navigate('/projects');
      } else {
        toast.error(response.data.message || '删除失败');
      }
    } catch (error: any) {
      console.error('Failed to delete project:', error);
      toast.error(error.response?.data?.message || '删除失败');
    } finally {
      setIsDeleting(false);
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

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">项目不存在</h2>
          <p className="text-gray-600 mb-4">请检查项目ID是否正确</p>
          <Link
            to="/projects"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            返回项目列表
          </Link>
        </div>
      </div>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
          {/* 项目信息 */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-4 sm:p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">项目信息</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <DollarSign className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">预算</p>
                    <p className="text-lg font-semibold text-gray-900">{formatCurrency(project.budget)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Calendar className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">截止日期</p>
                    <p className="text-lg font-semibold text-gray-900">{formatDate(project.deadline)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Clock className="w-5 h-5 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">状态</p>
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(project.status)}`}>
                      {getStatusText(project.status)}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-orange-100 rounded-lg">
                    <TrendingUp className="w-5 h-5 text-orange-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">模拟次数</p>
                    <p className="text-lg font-semibold text-gray-900">{simulations.length}</p>
                  </div>
                </div>
              </div>
              {project.description && (
                <div className="mt-6">
                  <h3 className="text-sm font-medium text-gray-900 mb-2">项目描述</h3>
                  <p className="text-gray-600">{project.description}</p>
                </div>
              )}
            </div>
          </div>

          {/* 快速操作 */}
          <div>
            <div className="bg-white rounded-lg shadow p-4 sm:p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">快速操作</h2>
              <div className="space-y-3">
                <Link
                  to={`/projects/${project.id}/simulation`}
                  className="w-full bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                >
                  <Play className="w-4 h-4" />
                  开始新模拟
                </Link>
                <Link
                  to={`/projects/${project.id}/edit`}
                  className="w-full bg-gray-100 text-gray-700 px-4 py-3 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
                >
                  <Edit className="w-4 h-4" />
                  编辑项目
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* 模拟历史 */}
        <div className="mt-6 lg:mt-8">
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 sm:p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">模拟历史</h2>
            </div>
            {simulations.length === 0 ? (
              <div className="p-8 text-center">
                <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">暂无模拟记录</h3>
                <p className="text-gray-600 mb-4">开始您的第一次价格模拟分析</p>
                <Link
                  to={`/projects/${project.id}/simulation`}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
                >
                  <Play className="w-4 h-4" />
                  开始模拟
                </Link>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        基础价格
                      </th>
                      <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        竞争对手数量
                      </th>
                      <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        市场条件
                      </th>
                      <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        风险等级
                      </th>
                      <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        创建时间
                      </th>
                      <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        操作
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {simulations.map((simulation) => (
                      <tr key={simulation.id} className="hover:bg-gray-50">
                        <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <div className="break-all">{formatCurrency(simulation.base_price)}</div>
                        </td>
                        <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {simulation.competitor_count}
                        </td>
                        <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <div className="break-words">{simulation.market_conditions}</div>
                        </td>
                        <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {simulation.risk_level}
                        </td>
                        <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDate(simulation.created_at)}
                        </td>
                        <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <Link
                            to={`/simulations/${simulation.id}`}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            查看结果
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}