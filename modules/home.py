"""主页面模块
展示项目介绍、算法选择菜单和快速开始指南
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from modules.algorithms_config import ALGORITHMS_CONFIG, ALGORITHM_CATEGORIES

def show_home_page():
    """显示主页面"""
    
    # 主标题
    st.markdown('<div class="main-header">🤖 Python数据分类学习小程序</div>', unsafe_allow_html=True)
    
    # 项目介绍部分
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h2 style="color: white; margin-bottom: 1rem;">📚 项目介绍</h2>
        <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 1rem;">
            欢迎使用Python数据分类学习小程序！这是一个交互式机器学习教育工具，
            帮助您理解和比较10种主流分类算法的原理、实现和应用。
        </p>
        <p style="font-size: 1.1rem; line-height: 1.6;">
            通过可视化和实践操作，让您深入理解机器学习算法的工作机制，
            适合学生、数据科学初学者和教育工作者使用。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 功能特色
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🔬 算法原理</h3>
            <p>深入讲解每种算法的数学原理和核心公式，配合可视化图表帮助理解</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 数据生成</h3>
            <p>智能生成各种分布的分类数据集，支持参数调整和实时可视化</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>⚖️ 算法比较</h3>
            <p>并排比较多个算法的性能指标，提供最佳算法推荐建议</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 算法选择菜单
    st.markdown("## 🎯 算法选择菜单")
    st.markdown("选择您想要学习的分类算法，开始您的机器学习之旅！")
    
    # 按类别组织算法
    categories = {}
    for algo_name, config in ALGORITHMS_CONFIG.items():
        category = config.get('category', 'other')
        if category not in categories:
            categories[category] = []
        categories[category].append((algo_name, config))
    
    # 创建算法卡片
    for category, algorithms in categories.items():
        category_name = ALGORITHM_CATEGORIES.get(category, category)
        st.markdown(f"### 📂 {category_name}")
        
        # 每行显示3个算法
        for i in range(0, len(algorithms), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < len(algorithms):
                    algo_name, config = algorithms[i + j]
                    with col:
                        create_algorithm_card(algo_name, config)
    
    st.markdown("---")
    
    # 快速开始指南
    st.markdown("## 🚀 快速开始指南")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📋 使用步骤
        
        1. **选择算法** - 从上方算法菜单中选择您感兴趣的分类算法
        2. **学习原理** - 查看算法的数学原理、公式解释和应用场景
        3. **生成数据** - 创建适合的训练数据集，调整数据参数
        4. **训练模型** - 配置算法参数，启动模型训练过程
        5. **分析结果** - 查看性能指标、可视化图表和模型解释
        6. **比较算法** - 对比不同算法的表现，选择最佳方案
        
        ### 💡 学习建议
        
        - **初学者**：建议从逻辑回归和决策树开始学习
        - **进阶用户**：可以重点关注集成学习和神经网络
        - **实践导向**：尝试不同的数据集和参数配置
        - **对比学习**：使用算法比较功能深入理解差异
        """)
    
    with col2:
        # 学习路径推荐
        st.markdown("### 🎯 推荐学习路径")
        
        learning_paths = {
            "🔰 初学者路径": ["逻辑回归", "决策树", "K近邻"],
            "📈 进阶路径": ["随机森林", "支持向量机", "梯度提升"],
            "🚀 高级路径": ["XGBoost", "神经网络", "LightGBM"]
        }
        
        for path_name, algorithms in learning_paths.items():
            with st.expander(path_name):
                for algo in algorithms:
                    st.markdown(f"• {algo}")
    
    # 统计信息
    st.markdown("---")
    st.markdown("## 📊 项目统计")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("算法数量", "10", "种主流算法")
    
    with col2:
        st.metric("算法类别", "8", "个不同类别")
    
    with col3:
        st.metric("功能模块", "6", "个核心模块")
    
    with col4:
        st.metric("学习路径", "3", "条推荐路径")
    
    # 算法分布饼图
    create_algorithm_distribution_chart()

def create_algorithm_card(algo_name, config):
    """创建算法卡片"""
    
    # 获取算法信息
    name = config.get('name', algo_name)
    description = config.get('description', '')
    category = config.get('category', '')
    category_name = ALGORITHM_CATEGORIES.get(category, category)
    
    # 创建卡片HTML
    card_html = f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
        text-align: center;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    ">
        <div>
            <h4 style="color: white; margin-bottom: 0.5rem; font-size: 1.2rem;">{name}</h4>
            <p style="font-size: 0.8rem; opacity: 0.8; margin-bottom: 1rem;">{category_name}</p>
            <p style="font-size: 0.9rem; line-height: 1.4;">{description[:80]}{'...' if len(description) > 80 else ''}</p>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # 学习按钮
    if st.button(f"📖 学习 {name}", key=f"learn_{algo_name}", use_container_width=True):
        st.session_state.selected_algorithm = algo_name
        st.session_state.current_page = 'algorithm_learning'
        st.rerun()

def create_algorithm_distribution_chart():
    """创建算法分布图表"""
    
    st.markdown("### 📈 算法类别分布")
    
    # 统计各类别的算法数量
    category_counts = {}
    for config in ALGORITHMS_CONFIG.values():
        category = config.get('category', 'other')
        category_name = ALGORITHM_CATEGORIES.get(category, category)
        category_counts[category_name] = category_counts.get(category_name, 0) + 1
    
    # 创建饼图
    fig = go.Figure(data=[go.Pie(
        labels=list(category_counts.keys()),
        values=list(category_counts.values()),
        hole=0.3,
        textinfo='label+percent',
        textposition='outside',
        marker=dict(
            colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
        )
    )])
    
    fig.update_layout(
        title={
            'text': '算法类别分布',
            'x': 0.5,
            'xanchor': 'center'
        },
        showlegend=True,
        height=400,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 显示详细统计
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**类别统计：**")
        for category, count in category_counts.items():
            st.markdown(f"• {category}: {count} 个算法")
    
    with col2:
        st.markdown("**特色功能：**")
        st.markdown("• 🔬 原理讲解")
        st.markdown("• 📊 数据生成")
        st.markdown("• 🎯 模型训练")
        st.markdown("• 📈 结果分析")
        st.markdown("• ⚖️ 算法比较")