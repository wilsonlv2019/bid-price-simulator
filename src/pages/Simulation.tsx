import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Play, TrendingUp, DollarSign, Target, AlertTriangle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import api, { type ApiResponse, type Project, type CreateSimulationRequest, type SimulationResult } from '@/lib/api';
import { toast } from 'sonner';
import Layout from '@/components/Layout';

export default function Simulation() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [formData, setFormData] = useState({
    basePrice: '100000',
    competitorCount: '3',
    marketConditions: 'normal',
    riskLevel: 'medium'
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);

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
        setProject(response.data.data.project);
        // 设置默认基础价格为项目预算的80%
        setFormData(prev => ({
          ...prev,
          basePrice: (response.data.data!.project.budget * 0.8).toString()
        }));
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

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!project) return;

    // 表单验证
    const basePrice = parseFloat(formData.basePrice);
    if (isNaN(basePrice) || basePrice <= 0) {
      toast.error('请输入有效的基础价格');
      return;
    }

    if (basePrice > project.budget) {
      toast.error('基础价格不能超过项目预算');
      return;
    }

    const competitorCount = parseInt(formData.competitorCount);
    if (isNaN(competitorCount) || competitorCount < 0 || competitorCount > 20) {
      toast.error('竞争对手数量必须在0-20之间');
      return;
    }

    setIsSimulating(true);
    try {
      const simulationData: CreateSimulationRequest = {
        project_id: project.id,
        base_price: basePrice,
        competitor_count: competitorCount,
        market_conditions: formData.marketConditions as 'excellent' | 'good' | 'fair' | 'poor',
        risk_level: formData.riskLevel as 'low' | 'medium' | 'high'
      };

      const response = await api.post<ApiResponse<{ simulation: any; result: SimulationResult }>>(
        '/simulations',
        simulationData
      );

      if (response.data.success && response.data.data) {
        setSimulationResult(response.data.data.result);
        toast.success('模拟完成！');
      } else {
        toast.error(response.data.message || '模拟失败');
      }
    } catch (error: any) {
      console.error('Failed to run simulation:', error);
      toast.error(error.response?.data?.message || '模拟失败，请检查网络连接');
    } finally {
      setIsSimulating(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY'
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getMarketConditionsText = (conditions: string) => {
    switch (conditions) {
      case 'good':
        return '良好';
      case 'normal':
        return '一般';
      case 'poor':
        return '较差';
      default:
        return '未知';
    }
  };

  const getRiskLevelText = (level: string) => {
    switch (level) {
      case 'low':
        return '低风险';
      case 'medium':
        return '中风险';
      case 'high':
        return '高风险';
      default:
        return '未知';
    }
  };

  const getRiskColor = (score: number) => {
    if (score <= 0.3) return 'text-green-600';
    if (score <= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getProfitColor = (margin: number) => {
    if (margin >= 0.2) return 'text-green-600';
    if (margin >= 0.1) return 'text-yellow-600';
    return 'text-red-600';
  };

  // 生成图表数据
  const generateChartData = () => {
    if (!simulationResult) return [];
    
    const basePrice = parseFloat(formData.basePrice);
    const data = [];
    
    for (let i = -20; i <= 20; i += 5) {
      const price = basePrice * (1 + i / 100);
      const winProb = Math.max(0, Math.min(1, simulationResult.win_probability + (i * -0.02)));
      const profit = Math.max(0, simulationResult.profit_margin + (i * 0.01));
      
      data.push({
        priceChange: `${i > 0 ? '+' : ''}${i}%`,
        price: price,
        winProbability: winProb * 100,
        profitMargin: profit * 100
      });
    }
    
    return data;
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
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 模拟参数设置 */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">模拟参数</h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* 基础价格 */}
                <div>
                  <label htmlFor="basePrice" className="block text-sm font-medium text-gray-700 mb-2">
                    基础价格 (CNY)
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">¥</span>
                    <input
                      id="basePrice"
                      name="basePrice"
                      type="number"
                      min="0"
                      max={project.budget}
                      step="0.01"
                      value={formData.basePrice}
                      onChange={handleInputChange}
                      className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="0.00"
                      required
                    />
                  </div>
                  <p className="text-sm text-gray-500 mt-1">最大值: {formatCurrency(project.budget)}</p>
                </div>

                {/* 竞争对手数量 */}
                <div>
                  <label htmlFor="competitorCount" className="block text-sm font-medium text-gray-700 mb-2">
                    竞争对手数量
                  </label>
                  <input
                    id="competitorCount"
                    name="competitorCount"
                    type="number"
                    min="0"
                    max="20"
                    value={formData.competitorCount}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                  <p className="text-sm text-gray-500 mt-1">范围: 0-20</p>
                </div>

                {/* 市场条件 */}
                <div>
                  <label htmlFor="marketConditions" className="block text-sm font-medium text-gray-700 mb-2">
                    市场条件
                  </label>
                  <select
                    id="marketConditions"
                    name="marketConditions"
                    value={formData.marketConditions}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="good">良好</option>
                    <option value="normal">一般</option>
                    <option value="poor">较差</option>
                  </select>
                </div>

                {/* 风险等级 */}
                <div>
                  <label htmlFor="riskLevel" className="block text-sm font-medium text-gray-700 mb-2">
                    风险等级
                  </label>
                  <select
                    id="riskLevel"
                    name="riskLevel"
                    value={formData.riskLevel}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="low">低风险</option>
                    <option value="medium">中风险</option>
                    <option value="high">高风险</option>
                  </select>
                </div>

                <button
                  type="submit"
                  disabled={isSimulating}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                >
                  <Play className="w-4 h-4" />
                  {isSimulating ? '模拟中...' : '开始模拟'}
                </button>
              </form>
            </div>
          </div>

          {/* 模拟结果 */}
          <div className="lg:col-span-2">
            {simulationResult ? (
              <div className="space-y-6">
                {/* 关键指标 */}
                <div className="bg-white rounded-lg shadow p-4 sm:p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">模拟结果</h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <DollarSign className="w-5 h-5 text-blue-600" />
                        <span className="text-sm font-medium text-blue-600">推荐价格</span>
                      </div>
                      <p className="text-lg sm:text-2xl font-bold text-blue-900 truncate">
                        {formatCurrency(simulationResult.recommended_price)}
                      </p>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Target className="w-5 h-5 text-green-600" />
                        <span className="text-sm font-medium text-green-600">中标概率</span>
                      </div>
                      <p className="text-lg sm:text-2xl font-bold text-green-900">
                        {formatPercentage(simulationResult.win_probability)}
                      </p>
                    </div>
                    <div className="bg-yellow-50 p-4 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="w-5 h-5 text-yellow-600" />
                        <span className="text-sm font-medium text-yellow-600">利润率</span>
                      </div>
                      <p className={`text-lg sm:text-2xl font-bold ${getProfitColor(simulationResult.profit_margin)}`}>
                        {formatPercentage(simulationResult.profit_margin)}
                      </p>
                    </div>
                    <div className="bg-red-50 p-4 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertTriangle className="w-5 h-5 text-red-600" />
                        <span className="text-sm font-medium text-red-600">风险评分</span>
                      </div>
                      <p className={`text-2xl font-bold ${getRiskColor(simulationResult.risk_score)}`}>
                        {(simulationResult.risk_score * 100).toFixed(1)}
                      </p>
                    </div>
                  </div>
                </div>

                {/* 价格敏感性分析图表 */}
                <div className="bg-white rounded-lg shadow p-4 sm:p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">价格敏感性分析</h3>
                  <div className="h-64 sm:h-80 overflow-hidden">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={generateChartData()} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="priceChange" 
                          tick={{ fontSize: 12 }}
                        />
                        <YAxis yAxisId="left" orientation="left" tick={{ fontSize: 12 }} />
                        <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12 }} />
                        <Tooltip 
                          contentStyle={{ fontSize: '12px' }}
                          labelStyle={{ fontSize: '12px' }}
                          formatter={(value: any, name: string) => {
                            if (name === 'winProbability') {
                              return [`${value.toFixed(1)}%`, '中标概率'];
                            }
                            if (name === 'profitMargin') {
                              return [`${value.toFixed(1)}%`, '利润率'];
                            }
                            return [value, name];
                          }}
                          labelFormatter={(label) => `价格变化: ${label}`}
                        />
                        <Legend wrapperStyle={{ fontSize: '12px' }} />
                        <Line 
                          yAxisId="left"
                          type="monotone" 
                          dataKey="winProbability" 
                          stroke="#10b981" 
                          strokeWidth={2}
                          name="中标概率"
                          dot={{ r: 3 }}
                        />
                        <Line 
                          yAxisId="right"
                          type="monotone" 
                          dataKey="profitMargin" 
                          stroke="#f59e0b" 
                          strokeWidth={2}
                          name="利润率"
                          dot={{ r: 3 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* 模拟参数总结 */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">模拟参数</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">基础价格:</span>
                      <p className="font-semibold">{formatCurrency(parseFloat(formData.basePrice))}</p>
                    </div>
                    <div>
                      <span className="text-gray-600">竞争对手:</span>
                      <p className="font-semibold">{formData.competitorCount} 个</p>
                    </div>
                    <div>
                      <span className="text-gray-600">市场条件:</span>
                      <p className="font-semibold">{getMarketConditionsText(formData.marketConditions)}</p>
                    </div>
                    <div>
                      <span className="text-gray-600">风险等级:</span>
                      <p className="font-semibold">{getRiskLevelText(formData.riskLevel)}</p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-8 text-center">
                <TrendingUp className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">开始价格模拟</h3>
                <p className="text-gray-600">设置模拟参数并点击"开始模拟"按钮来分析最优投标价格</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}