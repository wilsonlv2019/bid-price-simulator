// 内存数据存储层 - 替代Supabase数据库连接
import bcrypt from 'bcryptjs';

// 数据接口定义
export interface User {
  id: string;
  email: string;
  password: string;
  name: string;
  user_type: 'normal' | 'enterprise' | 'admin';
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: string;
  user_id: string;
  name: string;
  description: string;
  budget: number;
  deadline: string;
  status: 'active' | 'completed' | 'cancelled';
  created_at: string;
  updated_at: string;
}

export interface Simulation {
  id: string;
  project_id: string;
  user_id: string;
  name: string;
  base_price: number;
  competitor_count: number;
  market_conditions: string;
  risk_level: string;
  created_at: string;
  updated_at: string;
}

export interface SimulationResult {
  id: string;
  simulation_id: string;
  recommended_price: number;
  win_probability: number;
  profit_margin: number;
  risk_score: number;
  analysis_data: any;
  created_at: string;
}

// 内存数据存储
class MockDataStore {
  private users: User[] = [];
  private projects: Project[] = [];
  private simulations: Simulation[] = [];
  private simulationResults: SimulationResult[] = [];
  private nextId = 1;

  constructor() {
    this.initializeData();
  }

  // 生成唯一ID
  private generateId(): string {
    return (this.nextId++).toString();
  }

  // 初始化示例数据
  private async initializeData() {
    // 创建示例用户
    const hashedPassword = await bcrypt.hash('password123', 10);
    
    const sampleUsers: User[] = [
      {
        id: 'user_1',
        email: 'demo@example.com',
        password: hashedPassword,
        name: 'Demo User',
        user_type: 'normal',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 'user_2',
        email: 'john.doe@company.com',
        password: hashedPassword,
        name: 'John Doe',
        user_type: 'enterprise',
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z'
      },
      {
        id: 'user_3',
        email: 'alice.smith@enterprise.com',
        password: hashedPassword,
        name: 'Alice Smith',
        user_type: 'admin',
        created_at: '2024-01-03T00:00:00Z',
        updated_at: '2024-01-03T00:00:00Z'
      }
    ];

    this.users = sampleUsers;

    // 创建示例项目
    const sampleProjects: Project[] = [
      {
        id: 'project_1',
        user_id: 'user_1',
        name: '办公楼建设项目',
        description: '一个现代化办公楼的建设项目',
        budget: 5000000,
        deadline: '2024-12-31',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 'project_2',
        user_id: 'user_1',
        name: '住宅小区开发',
        description: '高端住宅小区的开发建设项目',
        budget: 12000000,
        deadline: '2025-06-30',
        status: 'active',
        created_at: '2024-01-05T00:00:00Z',
        updated_at: '2024-01-05T00:00:00Z'
      },
      {
        id: 'project_3',
        user_id: 'user_2',
        name: '商业综合体建设',
        description: '集购物、餐饮、娱乐于一体的商业综合体',
        budget: 8000000,
        deadline: '2024-10-15',
        status: 'active',
        created_at: '2024-01-10T00:00:00Z',
        updated_at: '2024-01-10T00:00:00Z'
      },
      {
        id: 'project_4',
        user_id: 'user_2',
        name: '工业园区基础设施',
        description: '工业园区的道路、水电等基础设施建设',
        budget: 3500000,
        deadline: '2024-08-20',
        status: 'completed',
        created_at: '2024-01-15T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z'
      },
      {
        id: 'project_5',
        user_id: 'user_3',
        name: '学校教学楼改造',
        description: '中学教学楼的现代化改造项目',
        budget: 2800000,
        deadline: '2024-09-01',
        status: 'active',
        created_at: '2024-01-20T00:00:00Z',
        updated_at: '2024-01-20T00:00:00Z'
      }
    ];

    this.projects = sampleProjects;

    // 创建示例模拟
    const sampleSimulations: Simulation[] = [
      {
        id: 'sim_1',
        project_id: 'project_1',
        user_id: 'user_1',
        name: '基础价格模拟',
        base_price: 4500000,
        competitor_count: 5,
        market_conditions: 'normal',
        risk_level: 'medium',
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z'
      },
      {
        id: 'sim_2',
        project_id: 'project_1',
        user_id: 'user_1',
        name: '激进策略模拟',
        base_price: 4200000,
        competitor_count: 8,
        market_conditions: 'competitive',
        risk_level: 'high',
        created_at: '2024-01-03T00:00:00Z',
        updated_at: '2024-01-03T00:00:00Z'
      },
      {
        id: 'sim_3',
        project_id: 'project_2',
        user_id: 'user_1',
        name: '保守策略模拟',
        base_price: 11500000,
        competitor_count: 3,
        market_conditions: 'favorable',
        risk_level: 'low',
        created_at: '2024-01-06T00:00:00Z',
        updated_at: '2024-01-06T00:00:00Z'
      },
      {
        id: 'sim_4',
        project_id: 'project_3',
        user_id: 'user_2',
        name: '市场分析模拟',
        base_price: 7800000,
        competitor_count: 6,
        market_conditions: 'normal',
        risk_level: 'medium',
        created_at: '2024-01-12T00:00:00Z',
        updated_at: '2024-01-12T00:00:00Z'
      }
    ];

    this.simulations = sampleSimulations;

    // 创建示例模拟结果
    const sampleResults: SimulationResult[] = [
      {
        id: 'result_1',
        simulation_id: 'sim_1',
        recommended_price: 4350000,
        win_probability: 0.75,
        profit_margin: 0.12,
        risk_score: 0.35,
        analysis_data: {
          competitorPrices: [4800000, 4600000, 4400000, 4700000, 4550000],
          marketTrends: {
            demand: 'stable',
            supply: 'moderate',
            priceDirection: 'neutral'
          },
          riskFactors: [
            { factor: '材料价格波动', impact: 0.15, probability: 0.6 },
            { factor: '工期延误', impact: 0.08, probability: 0.3 },
            { factor: '政策变化', impact: 0.12, probability: 0.2 }
          ]
        },
        created_at: '2024-01-02T00:00:00Z'
      },
      {
        id: 'result_2',
        simulation_id: 'sim_2',
        recommended_price: 4100000,
        win_probability: 0.85,
        profit_margin: 0.08,
        risk_score: 0.65,
        analysis_data: {
          competitorPrices: [4500000, 4300000, 4200000, 4400000, 4350000, 4250000, 4380000, 4150000],
          marketTrends: {
            demand: 'high',
            supply: 'limited',
            priceDirection: 'downward'
          },
          riskFactors: [
            { factor: '激烈竞争', impact: 0.25, probability: 0.8 },
            { factor: '利润压缩', impact: 0.20, probability: 0.7 },
            { factor: '质量风险', impact: 0.20, probability: 0.4 }
          ]
        },
        created_at: '2024-01-03T00:00:00Z'
      },
      {
        id: 'result_3',
        simulation_id: 'sim_3',
        recommended_price: 11200000,
        win_probability: 0.65,
        profit_margin: 0.18,
        risk_score: 0.25,
        analysis_data: {
          competitorPrices: [11800000, 11600000, 11400000],
          marketTrends: {
            demand: 'strong',
            supply: 'adequate',
            priceDirection: 'stable'
          },
          riskFactors: [
            { factor: '市场稳定', impact: 0.05, probability: 0.9 },
            { factor: '资金充足', impact: 0.03, probability: 0.8 }
          ]
        },
        created_at: '2024-01-06T00:00:00Z'
      },
      {
        id: 'result_4',
        simulation_id: 'sim_4',
        recommended_price: 7650000,
        win_probability: 0.70,
        profit_margin: 0.14,
        risk_score: 0.40,
        analysis_data: {
          competitorPrices: [8200000, 7900000, 7700000, 8000000, 7850000, 7750000],
          marketTrends: {
            demand: 'moderate',
            supply: 'balanced',
            priceDirection: 'neutral'
          },
          riskFactors: [
            { factor: '商业地产波动', impact: 0.18, probability: 0.5 },
            { factor: '租赁市场变化', impact: 0.12, probability: 0.4 }
          ]
        },
        created_at: '2024-01-12T00:00:00Z'
      }
    ];

    this.simulationResults = sampleResults;
  }

  // 用户相关方法
  async createUser(userData: { email: string; password: string; name: string; user_type?: string }): Promise<User> {
    const user: User = {
      id: this.generateId(),
      email: userData.email,
      password: userData.password,
      name: userData.name,
      user_type: (userData.user_type as 'normal' | 'enterprise' | 'admin') || 'normal',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    this.users.push(user);
    return user;
  }

  async getUserByEmail(email: string): Promise<User | null> {
    return this.users.find(user => user.email === email) || null;
  }

  async getUserById(id: string): Promise<User | null> {
    return this.users.find(user => user.id === id) || null;
  }

  async updateUser(id: string, updates: Partial<User>): Promise<User | null> {
    const userIndex = this.users.findIndex(user => user.id === id);
    if (userIndex === -1) return null;
    
    this.users[userIndex] = {
      ...this.users[userIndex],
      ...updates,
      updated_at: new Date().toISOString()
    };
    return this.users[userIndex];
  }

  // 项目相关方法
  async createProject(projectData: Omit<Project, 'id' | 'created_at' | 'updated_at'>): Promise<Project> {
    const project: Project = {
      id: this.generateId(),
      ...projectData,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    this.projects.push(project);
    return project;
  }

  async getProjectsByUserId(userId: string): Promise<Project[]> {
    return this.projects.filter(project => project.user_id === userId);
  }

  async getProjectById(id: string): Promise<Project | null> {
    return this.projects.find(project => project.id === id) || null;
  }

  async updateProject(id: string, updates: Partial<Project>): Promise<Project | null> {
    const projectIndex = this.projects.findIndex(project => project.id === id);
    if (projectIndex === -1) return null;
    
    this.projects[projectIndex] = {
      ...this.projects[projectIndex],
      ...updates,
      updated_at: new Date().toISOString()
    };
    return this.projects[projectIndex];
  }

  async deleteProject(id: string): Promise<boolean> {
    const projectIndex = this.projects.findIndex(project => project.id === id);
    if (projectIndex === -1) return false;
    
    this.projects.splice(projectIndex, 1);
    // 同时删除相关的模拟
    this.simulations = this.simulations.filter(sim => sim.project_id !== id);
    return true;
  }

  // 模拟相关方法
  async getSimulationsByUserId(userId: string): Promise<Simulation[]> {
    return this.simulations.filter(sim => sim.user_id === userId);
  }

  async getSimulationsByProjectId(projectId: string): Promise<Simulation[]> {
    return this.simulations.filter(sim => sim.project_id === projectId);
  }

  async getSimulationById(id: string): Promise<Simulation | null> {
    return this.simulations.find(sim => sim.id === id) || null;
  }

  async createSimulation(data: Omit<Simulation, 'id' | 'created_at' | 'updated_at' | 'user_id'>): Promise<Simulation> {
    // 获取项目信息来确定用户ID
    const project = await this.getProjectById(data.project_id);
    if (!project) {
      throw new Error('Project not found');
    }

    const simulation: Simulation = {
      id: `sim_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      user_id: project.user_id,
      ...data,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    this.simulations.push(simulation);
    return simulation;
  }

  async deleteSimulation(id: string): Promise<void> {
    // 删除模拟结果
    this.simulationResults = this.simulationResults.filter(result => result.simulation_id !== id);
    // 删除模拟
    this.simulations = this.simulations.filter(sim => sim.id !== id);
  }

  async updateSimulation(id: string, updates: Partial<Simulation>): Promise<Simulation | null> {
    const simIndex = this.simulations.findIndex(sim => sim.id === id);
    if (simIndex === -1) return null;
    
    this.simulations[simIndex] = {
      ...this.simulations[simIndex],
      ...updates,
      updated_at: new Date().toISOString()
    };
    return this.simulations[simIndex];
  }

  // 模拟结果相关方法
  async getSimulationResult(simulationId: string): Promise<SimulationResult | null> {
    return this.simulationResults.find(result => result.simulation_id === simulationId) || null;
  }

  async createSimulationResult(data: Omit<SimulationResult, 'id' | 'created_at'>): Promise<SimulationResult> {
    const result: SimulationResult = {
      id: `result_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      ...data,
      created_at: new Date().toISOString()
    };
    this.simulationResults.push(result);
    return result;
  }

  async getSimulationResultsByUserId(userId: string): Promise<SimulationResult[]> {
    const userSimulations = this.simulations.filter(sim => sim.user_id === userId);
    const simulationIds = userSimulations.map(sim => sim.id);
    return this.simulationResults.filter(result => simulationIds.includes(result.simulation_id));
  }
}

// 导出单例实例
export const mockDataStore = new MockDataStore();
export default mockDataStore;