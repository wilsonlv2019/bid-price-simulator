"""算法学习页面模块
展示算法原理、公式解释和参数配置
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from modules.algorithms_config import ALGORITHMS_CONFIG, get_algorithm_info, get_algorithm_display_name

def show_algorithm_learning_page():
    """显示算法学习页面"""
    
    st.markdown('<div class="main-header">📖 算法学习中心</div>', unsafe_allow_html=True)
    
    # 算法选择
    if not st.session_state.selected_algorithm:
        show_algorithm_selector()
        return
    
    # 获取选中算法的信息
    algo_name = st.session_state.selected_algorithm
    algo_info = get_algorithm_info(algo_name)
    
    if not algo_info:
        st.error(f"未找到算法 '{algo_name}' 的配置信息")
        return
    
    # 显示算法详细信息
    show_algorithm_details(algo_name, algo_info)

def show_algorithm_selector():
    """显示算法选择器"""
    
    st.markdown("## 🎯 选择要学习的算法")
    st.markdown("请从下方列表中选择一个算法开始学习：")
    
    # 创建算法选择网格
    algorithms = list(ALGORITHMS_CONFIG.keys())
    
    # 每行3个算法
    for i in range(0, len(algorithms), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(algorithms):
                algo_name = algorithms[i + j]
                algo_info = ALGORITHMS_CONFIG[algo_name]
                
                with col:
                    if st.button(
                        f"📚 {algo_info['name']}",
                        key=f"select_{algo_name}",
                        use_container_width=True,
                        help=algo_info['description']
                    ):
                        st.session_state.selected_algorithm = algo_name
                        st.rerun()

def show_algorithm_details(algo_name, algo_info):
    """显示算法详细信息"""
    
    # 算法标题和基本信息
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"## 🔬 {algo_info['name']}")
        st.markdown(f"**类别：** {algo_info.get('category', '未分类')}")
        st.markdown(f"**描述：** {algo_info['description']}")
    
    with col2:
        if st.button("🔄 选择其他算法", use_container_width=True):
            st.session_state.selected_algorithm = None
            st.rerun()
        
        if st.button("🚀 开始训练", use_container_width=True):
            st.session_state.current_page = 'model_training'
            st.rerun()
    
    st.markdown("---")
    
    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📐 核心公式", "⚙️ 参数配置", "✅ 优缺点", "🎯 应用场景", "📊 算法演示"])
    
    with tab1:
        show_algorithm_formula(algo_info)
    
    with tab2:
        show_algorithm_parameters(algo_info)
    
    with tab3:
        show_algorithm_pros_cons(algo_info)
    
    with tab4:
        show_algorithm_use_cases(algo_info)
    
    with tab5:
        show_algorithm_demo(algo_name, algo_info)

def show_algorithm_formula(algo_info):
    """显示算法公式"""
    
    st.markdown("### 📐 核心数学公式")
    
    # 显示主要公式
    formula = algo_info.get('formula', '')
    if formula:
        st.latex(formula)
    else:
        st.warning("该算法暂无公式信息")
    
    # 公式解释
    formula_explanation = algo_info.get('formula_explanation', {})
    if formula_explanation:
        st.markdown("### 📝 公式符号说明")
        
        # 创建两列布局
        col1, col2 = st.columns(2)
        
        items = list(formula_explanation.items())
        mid = len(items) // 2
        
        with col1:
            for symbol, explanation in items[:mid]:
                st.markdown(f"**{symbol}**: {explanation}")
        
        with col2:
            for symbol, explanation in items[mid:]:
                st.markdown(f"**{symbol}**: {explanation}")
    
    # 算法工作流程
    st.markdown("### 🔄 算法工作流程")
    create_algorithm_workflow(algo_info)

def show_algorithm_theory(algo_name, algo_info):
    """显示算法原理"""
    
    st.markdown("### 📚 算法原理")
    
    # 基本原理
    theory = algo_info.get('theory', '暂无理论说明')
    st.markdown(theory)
    
    # 数学公式部分 - 增强版
    st.markdown("#### 🔢 核心数学公式")
    
    # 根据算法类型显示相应的数学公式
    if algo_name == 'logistic_regression':
        show_logistic_regression_formulas()
    elif algo_name == 'decision_tree':
        show_decision_tree_formulas()
    elif algo_name == 'random_forest':
        show_random_forest_formulas()
    elif algo_name == 'svm':
        show_svm_formulas()
    elif algo_name == 'knn':
        show_knn_formulas()
    elif algo_name == 'naive_bayes':
        show_naive_bayes_formulas()
    elif algo_name == 'gradient_boosting':
        show_gradient_boosting_formulas()
    elif algo_name == 'xgboost':
        show_xgboost_formulas()
    elif algo_name == 'neural_network':
        show_neural_network_formulas()
    elif algo_name == 'lightgbm':
        show_lightgbm_formulas()
    else:
        # 通用公式显示
        formula = algo_info.get('formula', '')
        if formula:
            st.latex(formula)
        else:
            st.markdown("暂无数学公式")
    
    # 算法步骤
    steps = algo_info.get('steps', [])
    if steps:
        st.markdown("#### 📝 算法步骤")
        for i, step in enumerate(steps, 1):
            st.markdown(f"{i}. {step}")
    
    # 优缺点分析
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ 优点")
        advantages = algo_info.get('advantages', [])
        for advantage in advantages:
            st.markdown(f"• {advantage}")
    
    with col2:
        st.markdown("#### ❌ 缺点")
        disadvantages = algo_info.get('disadvantages', [])
        for disadvantage in disadvantages:
            st.markdown(f"• {disadvantage}")
    
    # 时间复杂度
    complexity = algo_info.get('complexity', {})
    if complexity:
        st.markdown("#### ⏱️ 复杂度分析")
        col1, col2 = st.columns(2)
        
        with col1:
            train_complexity = complexity.get('training', 'O(n)')
            st.markdown(f"**训练复杂度:** {train_complexity}")
        
        with col2:
            predict_complexity = complexity.get('prediction', 'O(1)')
            st.markdown(f"**预测复杂度:** {predict_complexity}")

def show_algorithm_parameters(algo_info):
    """显示算法参数"""
    
    st.markdown("### ⚙️ 主要参数配置")
    
    default_params = algo_info.get('default_params', {})
    param_descriptions = algo_info.get('param_descriptions', {})
    
    if not default_params:
        st.warning("该算法暂无参数配置信息")
        return
    
    # 创建参数表格
    st.markdown("#### 📋 参数列表")
    
    for param_name, default_value in default_params.items():
        col1, col2, col3 = st.columns([2, 2, 3])
        
        with col1:
            st.markdown(f"**{param_name}**")
        
        with col2:
            st.code(str(default_value))
        
        with col3:
            description = param_descriptions.get(param_name, '暂无描述')
            st.markdown(description)
    
    # 参数调优建议
    st.markdown("### 💡 参数调优建议")
    show_parameter_tuning_tips(algo_info)

def show_algorithm_pros_cons(algo_info):
    """显示算法优缺点"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ 优点")
        advantages = algo_info.get('advantages', [])
        if advantages:
            for advantage in advantages:
                st.markdown(f"• {advantage}")
        else:
            st.markdown("暂无优点信息")
    
    with col2:
        st.markdown("### ❌ 缺点")
        disadvantages = algo_info.get('disadvantages', [])
        if disadvantages:
            for disadvantage in disadvantages:
                st.markdown(f"• {disadvantage}")
        else:
            st.markdown("暂无缺点信息")
    
    # 适用性分析
    st.markdown("---")
    st.markdown("### 📊 适用性分析")
    create_suitability_radar_chart(algo_info)

def show_algorithm_use_cases(algo_info):
    """显示算法应用场景"""
    
    st.markdown("### 🎯 实际应用场景")
    
    use_cases = algo_info.get('use_cases', [])
    if use_cases:
        # 创建应用场景卡片
        for i, use_case in enumerate(use_cases):
            with st.expander(f"📌 应用场景 {i+1}: {use_case}"):
                show_use_case_details(use_case, algo_info)
    else:
        st.markdown("暂无应用场景信息")
    
    # 行业应用分布
    st.markdown("### 🏢 行业应用分布")
    create_industry_application_chart(use_cases)

def show_algorithm_demo(algo_name, algo_info):
    """显示算法演示"""
    
    st.markdown("### 📊 算法可视化演示")
    
    # 生成演示数据
    np.random.seed(42)
    n_samples = 200
    
    if algo_name in ['logistic_regression', 'svm', 'neural_network']:
        # 线性可分数据
        X1 = np.random.multivariate_normal([2, 2], [[1, 0.5], [0.5, 1]], n_samples//2)
        X2 = np.random.multivariate_normal([-2, -2], [[1, 0.5], [0.5, 1]], n_samples//2)
        X = np.vstack([X1, X2])
        y = np.hstack([np.zeros(n_samples//2), np.ones(n_samples//2)])
    else:
        # 非线性数据
        from sklearn.datasets import make_classification
        X, y = make_classification(n_samples=n_samples, n_features=2, n_redundant=0, 
                                 n_informative=2, n_clusters_per_class=1, random_state=42)
    
    # 创建散点图
    fig = go.Figure()
    
    colors = ['red', 'blue']
    for i in range(2):
        mask = y == i
        fig.add_trace(go.Scatter(
            x=X[mask, 0],
            y=X[mask, 1],
            mode='markers',
            name=f'类别 {i}',
            marker=dict(color=colors[i], size=8, opacity=0.7)
        ))
    
    fig.update_layout(
        title=f'{algo_info["name"]} - 数据分布示例',
        xaxis_title='特征 1',
        yaxis_title='特征 2',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 算法特性说明
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**数据特点：**")
        st.markdown(f"• 样本数量: {n_samples}")
        st.markdown(f"• 特征维度: 2")
        st.markdown(f"• 类别数量: 2")
    
    with col2:
        st.markdown("**算法特性：**")
        category = algo_info.get('category', '')
        if category == 'linear':
            st.markdown("• 线性决策边界")
            st.markdown("• 适合线性可分数据")
        elif category == 'tree':
            st.markdown("• 矩形决策边界")
            st.markdown("• 处理非线性关系")
        elif category == 'kernel':
            st.markdown("• 非线性决策边界")
            st.markdown("• 核技巧处理复杂数据")
        else:
            st.markdown("• 复杂决策边界")
            st.markdown("• 适应多种数据分布")

def create_algorithm_workflow(algo_info):
    """创建算法工作流程图"""
    
    category = algo_info.get('category', '')
    
    # 根据算法类别创建不同的工作流程
    if category == 'linear':
        steps = ["数据输入", "特征标准化", "线性变换", "激活函数", "输出预测"]
    elif category == 'tree':
        steps = ["数据输入", "特征选择", "节点分割", "递归构建", "叶节点预测"]
    elif category == 'ensemble':
        steps = ["数据输入", "Bootstrap采样", "多模型训练", "投票集成", "输出预测"]
    elif category == 'kernel':
        steps = ["数据输入", "核变换", "支持向量", "决策函数", "输出预测"]
    else:
        steps = ["数据输入", "特征处理", "模型训练", "参数优化", "输出预测"]
    
    # 创建流程图
    fig = go.Figure()
    
    # 添加节点
    for i, step in enumerate(steps):
        fig.add_trace(go.Scatter(
            x=[i],
            y=[0],
            mode='markers+text',
            text=[step],
            textposition='middle center',
            marker=dict(size=80, color='lightblue'),
            showlegend=False
        ))
        
        # 添加箭头
        if i < len(steps) - 1:
            fig.add_annotation(
                x=i+0.4, y=0,
                ax=i+0.6, ay=0,
                xref='x', yref='y',
                axref='x', ayref='y',
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='gray'
            )
    
    fig.update_layout(
        title='算法工作流程',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=200,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_parameter_tuning_tips(algo_info):
    """显示参数调优建议"""
    
    category = algo_info.get('category', '')
    
    tips = {
        'linear': [
            "调整正则化参数C来控制过拟合",
            "选择合适的求解器solver",
            "增加最大迭代次数max_iter"
        ],
        'tree': [
            "限制树的最大深度max_depth",
            "设置最小分割样本数min_samples_split",
            "调整最小叶节点样本数min_samples_leaf"
        ],
        'ensemble': [
            "增加基学习器数量n_estimators",
            "调整学习率learning_rate",
            "控制单个模型复杂度"
        ],
        'kernel': [
            "选择合适的核函数kernel",
            "调整正则化参数C",
            "优化核函数参数gamma"
        ]
    }
    
    category_tips = tips.get(category, ["根据验证集表现调整参数", "使用网格搜索优化", "注意过拟合问题"])
    
    for tip in category_tips:
        st.markdown(f"💡 {tip}")

def create_suitability_radar_chart(algo_info):
    """创建适用性雷达图"""
    
    # 根据算法类别设置适用性评分
    category = algo_info.get('category', '')
    
    scores = {
        'linear': [8, 6, 9, 7, 8, 6],
        'tree': [7, 9, 6, 8, 7, 9],
        'ensemble': [9, 7, 7, 9, 6, 8],
        'kernel': [8, 5, 8, 6, 9, 7],
        'instance_based': [6, 8, 7, 7, 6, 8],
        'probabilistic': [7, 7, 8, 6, 7, 9],
        'boosting': [9, 6, 7, 8, 8, 7],
        'neural': [9, 5, 6, 7, 9, 6]
    }
    
    categories = ['准确性', '可解释性', '训练速度', '预测速度', '处理大数据', '处理噪声']
    values = scores.get(category, [7, 7, 7, 7, 7, 7])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=algo_info['name']
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=True,
        title='算法适用性评估',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_use_case_details(use_case, algo_info):
    """显示应用场景详细信息"""
    
    # 根据应用场景提供详细说明
    case_details = {
        '医疗诊断': {
            'description': '利用患者症状和检查结果进行疾病诊断',
            'data_type': '结构化医疗数据',
            'challenges': ['数据不平衡', '特征相关性', '可解释性要求'],
            'metrics': ['准确率', '召回率', '特异性']
        },
        '文本分类': {
            'description': '对文档、邮件、评论等文本进行自动分类',
            'data_type': '文本数据',
            'challenges': ['高维稀疏', '语义理解', '多语言处理'],
            'metrics': ['精确率', '召回率', 'F1分数']
        },
        '图像识别': {
            'description': '识别和分类图像中的对象或场景',
            'data_type': '图像数据',
            'challenges': ['数据量大', '特征提取', '计算复杂'],
            'metrics': ['Top-1准确率', 'Top-5准确率', 'mAP']
        }
    }
    
    details = case_details.get(use_case, {
        'description': f'{use_case}的具体应用',
        'data_type': '相关数据类型',
        'challenges': ['数据质量', '模型选择', '性能优化'],
        'metrics': ['准确率', '精确率', '召回率']
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**应用描述：** {details['description']}")
        st.markdown(f"**数据类型：** {details['data_type']}")
    
    with col2:
        st.markdown("**主要挑战：**")
        for challenge in details['challenges']:
            st.markdown(f"• {challenge}")
        
        st.markdown("**评估指标：**")
        for metric in details['metrics']:
            st.markdown(f"• {metric}")

def create_industry_application_chart(use_cases):
    """创建行业应用分布图"""
    
    if not use_cases:
        st.markdown("暂无行业应用数据")
        return
    
    # 行业分类映射
    industry_mapping = {
        '医疗诊断': '医疗健康',
        '文本分类': '信息技术',
        '图像识别': '人工智能',
        '垃圾邮件过滤': '信息技术',
        '推荐系统': '电子商务',
        '风险评估': '金融服务',
        '客户分类': '市场营销',
        '异常检测': '网络安全',
        '语音识别': '人工智能',
        '生物信息学': '生物科技'
    }
    
    # 统计行业分布
    industry_counts = {}
    for use_case in use_cases:
        industry = industry_mapping.get(use_case, '其他')
        industry_counts[industry] = industry_counts.get(industry, 0) + 1
    
    if industry_counts:
        fig = go.Figure(data=[go.Bar(
            x=list(industry_counts.keys()),
            y=list(industry_counts.values()),
            marker_color='lightblue'
        )])
        
        fig.update_layout(
            title='行业应用分布',
            xaxis_title='行业',
            yaxis_title='应用数量',
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown("暂无行业分布数据")

# 数学公式渲染函数
def show_logistic_regression_formulas():
    """显示逻辑回归的数学公式"""
    
    st.markdown("**1. Sigmoid函数（激活函数）**")
    st.latex(r"\sigma(z) = \frac{1}{1 + e^{-z}}")
    
    st.markdown("**2. 线性组合**")
    st.latex(r"z = \theta_0 + \theta_1 x_1 + \theta_2 x_2 + ... + \theta_n x_n = \theta^T x")
    
    st.markdown("**3. 预测概率**")
    st.latex(r"P(y=1|x) = \sigma(\theta^T x) = \frac{1}{1 + e^{-\theta^T x}}")
    
    st.markdown("**4. 损失函数（对数似然）**")
    st.latex(r"J(\theta) = -\frac{1}{m} \sum_{i=1}^{m} [y^{(i)} \log(h_\theta(x^{(i)})) + (1-y^{(i)}) \log(1-h_\theta(x^{(i)}))]")
    
    st.markdown("**5. 梯度下降更新规则**")
    st.latex(r"\theta_j := \theta_j - \alpha \frac{\partial J(\theta)}{\partial \theta_j}")

def show_decision_tree_formulas():
    """显示决策树的数学公式"""
    
    st.markdown("**1. 信息熵（Entropy）**")
    st.latex(r"H(S) = -\sum_{i=1}^{c} p_i \log_2(p_i)")
    
    st.markdown("**2. 信息增益（Information Gain）**")
    st.latex(r"IG(S, A) = H(S) - \sum_{v \in Values(A)} \frac{|S_v|}{|S|} H(S_v)")
    
    st.markdown("**3. 基尼不纯度（Gini Impurity）**")
    st.latex(r"Gini(S) = 1 - \sum_{i=1}^{c} p_i^2")
    
    st.markdown("**4. 基尼增益**")
    st.latex(r"Gini_{gain}(S, A) = Gini(S) - \sum_{v \in Values(A)} \frac{|S_v|}{|S|} Gini(S_v)")

def show_random_forest_formulas():
    """显示随机森林的数学公式"""
    
    st.markdown("**1. Bootstrap采样**")
    st.latex(r"D_i = \{(x_{j_1}, y_{j_1}), (x_{j_2}, y_{j_2}), ..., (x_{j_n}, y_{j_n})\}")
    
    st.markdown("**2. 随机特征选择**")
    st.latex(r"F_i \subset F, |F_i| = \sqrt{|F|}")
    
    st.markdown("**3. 投票预测（分类）**")
    st.latex(r"\hat{y} = \text{mode}\{h_1(x), h_2(x), ..., h_B(x)\}")
    
    st.markdown("**4. 平均预测（回归）**")
    st.latex(r"\hat{y} = \frac{1}{B} \sum_{i=1}^{B} h_i(x)")
    
    st.markdown("**5. 袋外误差（OOB Error）**")
    st.latex(r"OOB_{error} = \frac{1}{n} \sum_{i=1}^{n} I(y_i \neq \hat{y}_i^{OOB})")

def show_svm_formulas():
    """显示支持向量机的数学公式"""
    
    st.markdown("**1. 决策函数**")
    st.latex(r"f(x) = \text{sign}(\sum_{i=1}^{n} \alpha_i y_i K(x_i, x) + b)")
    
    st.markdown("**2. 优化目标（原问题）**")
    st.latex(r"\min_{w,b} \frac{1}{2} ||w||^2 + C \sum_{i=1}^{n} \xi_i")
    
    st.markdown("**3. 约束条件**")
    st.latex(r"y_i(w^T x_i + b) \geq 1 - \xi_i, \quad \xi_i \geq 0")
    
    st.markdown("**4. 核函数（RBF）**")
    st.latex(r"K(x_i, x_j) = \exp(-\gamma ||x_i - x_j||^2)")
    
    st.markdown("**5. 对偶问题**")
    st.latex(r"\max_{\alpha} \sum_{i=1}^{n} \alpha_i - \frac{1}{2} \sum_{i,j=1}^{n} \alpha_i \alpha_j y_i y_j K(x_i, x_j)")

def show_knn_formulas():
    """显示K近邻的数学公式"""
    
    st.markdown("**1. 欧几里得距离**")
    st.latex(r"d(x_i, x_j) = \sqrt{\sum_{k=1}^{p} (x_{ik} - x_{jk})^2}")
    
    st.markdown("**2. 曼哈顿距离**")
    st.latex(r"d(x_i, x_j) = \sum_{k=1}^{p} |x_{ik} - x_{jk}|")
    
    st.markdown("**3. 分类预测（多数投票）**")
    st.latex(r"\hat{y} = \text{mode}\{y_{i_1}, y_{i_2}, ..., y_{i_k}\}")
    
    st.markdown("**4. 回归预测（平均值）**")
    st.latex(r"\hat{y} = \frac{1}{k} \sum_{j=1}^{k} y_{i_j}")
    
    st.markdown("**5. 加权预测**")
    st.latex(r"\hat{y} = \frac{\sum_{j=1}^{k} w_j y_{i_j}}{\sum_{j=1}^{k} w_j}, \quad w_j = \frac{1}{d(x, x_{i_j})}")

def show_naive_bayes_formulas():
    """显示朴素贝叶斯的数学公式"""
    
    st.markdown("**1. 贝叶斯定理**")
    st.latex(r"P(y|x) = \frac{P(x|y) P(y)}{P(x)}")
    
    st.markdown("**2. 朴素假设（特征独立）**")
    st.latex(r"P(x|y) = \prod_{i=1}^{n} P(x_i|y)")
    
    st.markdown("**3. 分类决策**")
    st.latex(r"\hat{y} = \arg\max_y P(y) \prod_{i=1}^{n} P(x_i|y)")
    
    st.markdown("**4. 高斯朴素贝叶斯**")
    st.latex(r"P(x_i|y) = \frac{1}{\sqrt{2\pi\sigma_y^2}} \exp\left(-\frac{(x_i-\mu_y)^2}{2\sigma_y^2}\right)")
    
    st.markdown("**5. 拉普拉斯平滑**")
    st.latex(r"P(x_i|y) = \frac{N_{yi} + \alpha}{N_y + \alpha n}")

def show_gradient_boosting_formulas():
    """显示梯度提升的数学公式"""
    
    st.markdown("**1. 加法模型**")
    st.latex(r"F_m(x) = F_{m-1}(x) + \gamma_m h_m(x)")
    
    st.markdown("**2. 损失函数最小化**")
    st.latex(r"\gamma_m = \arg\min_\gamma \sum_{i=1}^{n} L(y_i, F_{m-1}(x_i) + \gamma h_m(x_i))")
    
    st.markdown("**3. 负梯度（伪残差）**")
    st.latex(r"r_{im} = -\left[\frac{\partial L(y_i, F(x_i))}{\partial F(x_i)}\right]_{F=F_{m-1}}")
    
    st.markdown("**4. 最终预测**")
    st.latex(r"F(x) = \sum_{m=1}^{M} \gamma_m h_m(x)")
    
    st.markdown("**5. 学习率调整**")
    st.latex(r"F_m(x) = F_{m-1}(x) + \nu \gamma_m h_m(x), \quad 0 < \nu \leq 1")

def show_xgboost_formulas():
    """显示XGBoost的数学公式"""
    
    st.markdown("**1. 目标函数**")
    st.latex(r"Obj^{(t)} = \sum_{i=1}^{n} l(y_i, \hat{y}_i^{(t-1)} + f_t(x_i)) + \Omega(f_t)")
    
    st.markdown("**2. 正则化项**")
    st.latex(r"\Omega(f) = \gamma T + \frac{1}{2} \lambda \sum_{j=1}^{T} w_j^2")
    
    st.markdown("**3. 二阶泰勒展开**")
    st.latex(r"Obj^{(t)} \approx \sum_{i=1}^{n} [g_i f_t(x_i) + \frac{1}{2} h_i f_t^2(x_i)] + \Omega(f_t)")
    
    st.markdown("**4. 最优权重**")
    st.latex(r"w_j^* = -\frac{G_j}{H_j + \lambda}")
    
    st.markdown("**5. 分割增益**")
    st.latex(r"Gain = \frac{1}{2} \left[\frac{G_L^2}{H_L + \lambda} + \frac{G_R^2}{H_R + \lambda} - \frac{(G_L + G_R)^2}{H_L + H_R + \lambda}\right] - \gamma")

def show_neural_network_formulas():
    """显示神经网络的数学公式"""
    
    st.markdown("**1. 前向传播**")
    st.latex(r"z^{(l)} = W^{(l)} a^{(l-1)} + b^{(l)}")
    
    st.markdown("**2. 激活函数（ReLU）**")
    st.latex(r"a^{(l)} = \max(0, z^{(l)})")
    
    st.markdown("**3. Softmax输出**")
    st.latex(r"a_i^{(L)} = \frac{e^{z_i^{(L)}}}{\sum_{j=1}^{K} e^{z_j^{(L)}}}")
    
    st.markdown("**4. 交叉熵损失**")
    st.latex(r"J = -\frac{1}{m} \sum_{i=1}^{m} \sum_{k=1}^{K} y_k^{(i)} \log(a_k^{(L)(i)})")
    
    st.markdown("**5. 反向传播**")
    st.latex(r"\frac{\partial J}{\partial W^{(l)}} = \frac{1}{m} \delta^{(l)} (a^{(l-1)})^T")
    
    st.markdown("**6. 权重更新**")
    st.latex(r"W^{(l)} := W^{(l)} - \alpha \frac{\partial J}{\partial W^{(l)}}")

def show_lightgbm_formulas():
    """显示LightGBM的数学公式"""
    
    st.markdown("**1. 基于梯度的单边采样（GOSS）**")
    st.latex(r"\tilde{G}_j = \frac{1-a}{b} \sum_{x_i \in A_l} g_i + \sum_{x_i \in B_l} g_i")
    
    st.markdown("**2. 互斥特征绑定（EFB）**")
    st.latex(r"Bundle = \{F_1, F_2, ..., F_k\} \text{ where } F_i \cap F_j = \emptyset")
    
    st.markdown("**3. 叶子节点分割增益**")
    st.latex(r"Gain = \frac{(\sum_{x_i \in I_L} g_i)^2}{\sum_{x_i \in I_L} h_i + \lambda} + \frac{(\sum_{x_i \in I_R} g_i)^2}{\sum_{x_i \in I_R} h_i + \lambda} - \frac{(\sum_{x_i \in I} g_i)^2}{\sum_{x_i \in I} h_i + \lambda}")
    
    st.markdown("**4. 叶子节点权重**")
    st.latex(r"w_j = -\frac{\sum_{x_i \in I_j} g_i}{\sum_{x_i \in I_j} h_i + \lambda}")
    
    st.markdown("**5. 预测输出**")
    st.latex(r"\hat{y} = \sum_{t=1}^{T} f_t(x) = \sum_{t=1}^{T} w_{q_t(x)}")