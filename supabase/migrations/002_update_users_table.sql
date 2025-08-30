-- 更新用户表结构，添加投标价格模拟器所需字段
-- 创建时间: 2024-01-15

-- 添加缺失的字段到users表
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255),
ADD COLUMN IF NOT EXISTS user_type VARCHAR(20) DEFAULT 'basic';

-- 添加约束检查（先检查是否存在）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'check_user_type' 
        AND conrelid = 'users'::regclass
    ) THEN
        ALTER TABLE users ADD CONSTRAINT check_user_type 
        CHECK (user_type IN ('basic', 'enterprise', 'admin'));
    END IF;
END $$;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_type ON users(user_type);

-- 创建项目表
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50) NOT NULL,
    budget DECIMAL(15,2) NOT NULL,
    region VARCHAR(100) NOT NULL,
    competitors INTEGER DEFAULT 3,
    cost_structure JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建项目表索引
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_type ON projects(type);
CREATE INDEX IF NOT EXISTS idx_projects_region ON projects(region);

-- 创建模拟记录表
CREATE TABLE IF NOT EXISTS simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    strategy_type VARCHAR(50) NOT NULL,
    price_range JSONB NOT NULL,
    parameters JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建模拟记录表索引
CREATE INDEX IF NOT EXISTS idx_simulations_project_id ON simulations(project_id);
CREATE INDEX IF NOT EXISTS idx_simulations_created_at ON simulations(created_at DESC);

-- 创建模拟结果表
CREATE TABLE IF NOT EXISTS simulation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_id UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    bid_price DECIMAL(15,2) NOT NULL,
    win_probability DECIMAL(5,4) NOT NULL,
    expected_profit DECIMAL(15,2) NOT NULL,
    risk_score DECIMAL(5,4) NOT NULL
);

-- 创建模拟结果表索引
CREATE INDEX IF NOT EXISTS idx_simulation_results_simulation_id ON simulation_results(simulation_id);
CREATE INDEX IF NOT EXISTS idx_simulation_results_win_probability ON simulation_results(win_probability DESC);

-- 设置表权限
GRANT SELECT ON users TO anon;
GRANT ALL PRIVILEGES ON users TO authenticated;

GRANT SELECT ON projects TO anon;
GRANT ALL PRIVILEGES ON projects TO authenticated;

GRANT SELECT ON simulations TO anon;
GRANT ALL PRIVILEGES ON simulations TO authenticated;

GRANT SELECT ON simulation_results TO anon;
GRANT ALL PRIVILEGES ON simulation_results TO authenticated;

-- 更新现有用户数据（如果需要）
UPDATE users SET 
    password_hash = '$2b$10$example_hash_default',
    user_type = 'basic'
WHERE password_hash IS NULL;

-- 插入示例数据
INSERT INTO users (email, password_hash, name, user_type) VALUES
('admin@bidding.com', '$2b$10$example_hash_admin', '系统管理员', 'admin'),
('demo@bidding.com', '$2b$10$example_hash_demo', '演示用户', 'basic')
ON CONFLICT (email) DO NOTHING;

-- 插入示例项目
INSERT INTO projects (user_id, name, type, budget, region, competitors, cost_structure)
SELECT 
    (SELECT id FROM users WHERE email = 'demo@bidding.com'),
    '示例建筑项目',
    '建筑工程',
    5000000.00,
    '北京',
    5,
    '{"material_cost": 0.6, "labor_cost": 0.25, "overhead": 0.1, "profit_margin": 0.05}'::jsonb
WHERE EXISTS (SELECT 1 FROM users WHERE email = 'demo@bidding.com')
AND NOT EXISTS (
    SELECT 1 FROM projects 
    WHERE name = '示例建筑项目' 
    AND user_id = (SELECT id FROM users WHERE email = 'demo@bidding.com')
);