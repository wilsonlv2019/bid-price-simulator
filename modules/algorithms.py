"""算法实现模块
包含10种分类算法的具体实现和可视化功能
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, learning_curve
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_curve, auc
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
import xgboost as xgb
import lightgbm as lgb
from modules.algorithms_config import get_algorithm_info
import warnings
warnings.filterwarnings('ignore')

def show_algorithm_implementation(algorithm_name):
    """显示算法实现页面"""
    
    # 获取算法信息
    algo_info = get_algorithm_info(algorithm_name)
    
    if not algo_info:
        st.error(f"未找到算法: {algorithm_name}")
        return
    
    # 页面标题
    st.markdown(f'<div class="main-header">{algo_info["name"]} 实现</div>', unsafe_allow_html=True)
    
    # 检查数据
    if 'generated_data' not in st.session_state:
        show_no_data_message()
        return
    
    # 获取数据
    data = st.session_state.generated_data
    X, y = data['X'], data['y']
    
    # 创建标签页
    tabs = st.tabs(["📚 算法原理", "⚙️ 参数配置", "🎯 模型训练", "📊 结果分析", "🔍 可视化"])
    
    with tabs[0]:
        show_algorithm_theory(algo_info)
    
    with tabs[1]:
        params = show_parameter_configuration(algo_info)
    
    with tabs[2]:
        model, results = show_model_training(algorithm_name, X, y, params)
    
    with tabs[3]:
        if 'model' in locals() and model is not None:
            show_results_analysis(model, results, X, y)
    
    with tabs[4]:
        if 'model' in locals() and model is not None:
            show_algorithm_visualization(algorithm_name, model, X, y, results)

def show_no_data_message():
    """显示无数据提示"""
    
    st.markdown("## ⚠️ 没有可用的数据")
    st.markdown("""
    请先生成数据集才能训练算法。
    
    您可以：
    1. 前往 **数据生成** 页面生成数据
    2. 使用默认数据集
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 前往数据生成", use_container_width=True):
            st.session_state.current_page = 'data_generation'
            st.rerun()
    
    with col2:
        if st.button("🎲 使用默认数据", use_container_width=True):
            generate_default_data()
            st.rerun()

def generate_default_data():
    """生成默认数据集"""
    
    from sklearn.datasets import make_classification
    
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_informative=5,
        n_redundant=2,
        n_classes=3,
        random_state=42
    )
    
    st.session_state.generated_data = {
        'X': X,
        'y': y,
        'feature_names': [f'特征_{i+1}' for i in range(X.shape[1])],
        'target_names': [f'类别_{i}' for i in range(len(np.unique(y)))],
        'dataset_info': {
            'type': '默认分类数据集',
            'n_samples': len(X),
            'n_features': X.shape[1],
            'n_classes': len(np.unique(y))
        }
    }
    
    st.success("✅ 默认数据集生成成功！")

def show_algorithm_theory(algo_info):
    """显示算法原理"""
    
    st.markdown("## 📚 算法原理")
    
    # 算法描述
    st.markdown(f"### 📖 算法描述")
    st.markdown(algo_info['description'])
    
    # 核心公式
    st.markdown(f"### 🧮 核心公式")
    
    # 使用LaTeX渲染公式
    for formula in algo_info['formulas']:
        st.markdown(f"**{formula['name']}:**")
        st.latex(formula['formula'])
        st.markdown(formula['explanation'])
        st.markdown("---")
    
    # 算法优缺点
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ 优点")
        for advantage in algo_info['advantages']:
            st.markdown(f"- {advantage}")
    
    with col2:
        st.markdown("### ❌ 缺点")
        for disadvantage in algo_info['disadvantages']:
            st.markdown(f"- {disadvantage}")
    
    # 应用场景
    st.markdown("### 🎯 应用场景")
    for use_case in algo_info['use_cases']:
        st.markdown(f"- {use_case}")
    
    # 算法复杂度
    if 'complexity' in algo_info:
        st.markdown("### ⚡ 算法复杂度")
        complexity = algo_info['complexity']
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**时间复杂度:** {complexity.get('time', 'N/A')}")
        with col2:
            st.markdown(f"**空间复杂度:** {complexity.get('space', 'N/A')}")

def show_parameter_configuration(algo_info):
    """显示参数配置"""
    
    st.markdown("## ⚙️ 参数配置")
    
    params = {}
    
    # 获取默认参数
    default_params = algo_info['default_params']
    param_descriptions = algo_info['param_descriptions']
    
    # 创建参数配置界面
    st.markdown("### 🔧 调整参数")
    
    for param_name, default_value in default_params.items():
        description = param_descriptions.get(param_name, "")
        
        if isinstance(default_value, bool):
            params[param_name] = st.checkbox(
                f"{param_name}",
                value=default_value,
                help=description
            )
        
        elif isinstance(default_value, int):
            if param_name in ['n_estimators', 'max_iter', 'n_neighbors']:
                params[param_name] = st.slider(
                    f"{param_name}",
                    min_value=1,
                    max_value=1000,
                    value=default_value,
                    help=description
                )
            elif param_name in ['max_depth']:
                params[param_name] = st.slider(
                    f"{param_name}",
                    min_value=1,
                    max_value=50,
                    value=default_value,
                    help=description
                )
            else:
                params[param_name] = st.number_input(
                    f"{param_name}",
                    value=default_value,
                    help=description
                )
        
        elif isinstance(default_value, float):
            if param_name in ['learning_rate', 'alpha', 'gamma']:
                params[param_name] = st.slider(
                    f"{param_name}",
                    min_value=0.001,
                    max_value=1.0,
                    value=default_value,
                    step=0.001,
                    help=description
                )
            elif param_name in ['C']:
                params[param_name] = st.slider(
                    f"{param_name}",
                    min_value=0.01,
                    max_value=100.0,
                    value=default_value,
                    step=0.01,
                    help=description
                )
            else:
                params[param_name] = st.number_input(
                    f"{param_name}",
                    value=default_value,
                    help=description
                )
        
        elif isinstance(default_value, str):
            if param_name == 'kernel':
                options = ['linear', 'poly', 'rbf', 'sigmoid']
                params[param_name] = st.selectbox(
                    f"{param_name}",
                    options,
                    index=options.index(default_value) if default_value in options else 0,
                    help=description
                )
            elif param_name == 'criterion':
                options = ['gini', 'entropy']
                params[param_name] = st.selectbox(
                    f"{param_name}",
                    options,
                    index=options.index(default_value) if default_value in options else 0,
                    help=description
                )
            elif param_name == 'solver':
                options = ['lbfgs', 'liblinear', 'newton-cg', 'sag', 'saga']
                params[param_name] = st.selectbox(
                    f"{param_name}",
                    options,
                    index=options.index(default_value) if default_value in options else 0,
                    help=description
                )
            else:
                params[param_name] = st.text_input(
                    f"{param_name}",
                    value=str(default_value),
                    help=description
                )
    
    # 显示当前参数配置
    st.markdown("### 📋 当前参数配置")
    
    param_df = pd.DataFrame([
        {'参数': k, '值': v, '说明': param_descriptions.get(k, '')}
        for k, v in params.items()
    ])
    
    st.dataframe(param_df, use_container_width=True)
    
    return params

def show_model_training(algorithm_name, X, y, params):
    """显示模型训练"""
    
    st.markdown("## 🎯 模型训练")
    
    # 训练配置
    col1, col2 = st.columns(2)
    
    with col1:
        test_size = st.slider("测试集比例", 0.1, 0.5, 0.2, 0.05)
        random_state = st.number_input("随机种子", 0, 1000, 42)
    
    with col2:
        cv_folds = st.slider("交叉验证折数", 3, 10, 5)
        scale_features = st.checkbox("特征标准化", True)
    
    # 开始训练按钮
    if st.button("🚀 开始训练", use_container_width=True):
        with st.spinner("正在训练模型..."):
            model, results = train_algorithm(
                algorithm_name, X, y, params, test_size, 
                random_state, cv_folds, scale_features
            )
            
            if model is not None:
                st.success("✅ 模型训练完成！")
                
                # 保存到session state
                st.session_state.trained_model = {
                    'model': model,
                    'results': results,
                    'algorithm_name': algorithm_name,
                    'params': params
                }
                
                return model, results
            else:
                st.error("❌ 模型训练失败")
                return None, None
    
    # 如果已有训练好的模型，显示信息
    if 'trained_model' in st.session_state:
        trained_info = st.session_state.trained_model
        if trained_info['algorithm_name'] == algorithm_name:
            st.info("💡 检测到已训练的模型，可以直接查看结果")
            return trained_info['model'], trained_info['results']
    
    return None, None

def train_algorithm(algorithm_name, X, y, params, test_size, random_state, cv_folds, scale_features):
    """训练算法"""
    
    try:
        # 数据分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # 特征标准化
        if scale_features:
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)
        else:
            scaler = None
        
        # 创建模型
        model = create_model(algorithm_name, params)
        
        if model is None:
            return None, None
        
        # 训练模型
        model.fit(X_train, y_train)
        
        # 预测
        y_pred = model.predict(X_test)
        
        # 计算性能指标
        accuracy = accuracy_score(y_test, y_pred)
        
        # 交叉验证
        cv_scores = cross_val_score(model, X_train, y_train, cv=cv_folds)
        
        # 分类报告
        class_report = classification_report(y_test, y_pred, output_dict=True)
        
        # 混淆矩阵
        conf_matrix = confusion_matrix(y_test, y_pred)
        
        # 学习曲线
        train_sizes, train_scores, val_scores = learning_curve(
            model, X_train, y_train, cv=cv_folds, n_jobs=-1
        )
        
        # 整理结果
        results = {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'y_pred': y_pred,
            'accuracy': accuracy,
            'cv_scores': cv_scores,
            'classification_report': class_report,
            'confusion_matrix': conf_matrix,
            'train_sizes': train_sizes,
            'train_scores': train_scores,
            'val_scores': val_scores,
            'scaler': scaler
        }
        
        # 如果模型支持概率预测
        if hasattr(model, 'predict_proba'):
            y_proba = model.predict_proba(X_test)
            results['y_proba'] = y_proba
        
        return model, results
        
    except Exception as e:
        st.error(f"训练过程中出现错误: {str(e)}")
        return None, None

def create_model(algorithm_name, params):
    """创建模型实例"""
    
    try:
        if algorithm_name == '逻辑回归':
            return LogisticRegression(**params)
        
        elif algorithm_name == '决策树':
            return DecisionTreeClassifier(**params)
        
        elif algorithm_name == '随机森林':
            return RandomForestClassifier(**params)
        
        elif algorithm_name == '支持向量机':
            return SVC(**params)
        
        elif algorithm_name == 'K近邻':
            return KNeighborsClassifier(**params)
        
        elif algorithm_name == '朴素贝叶斯':
            return GaussianNB(**params)
        
        elif algorithm_name == '梯度提升':
            return GradientBoostingClassifier(**params)
        
        elif algorithm_name == 'XGBoost':
            return xgb.XGBClassifier(**params)
        
        elif algorithm_name == '神经网络':
            return MLPClassifier(**params)
        
        elif algorithm_name == 'LightGBM':
            return lgb.LGBMClassifier(**params)
        
        else:
            st.error(f"不支持的算法: {algorithm_name}")
            return None
            
    except Exception as e:
        st.error(f"创建模型时出现错误: {str(e)}")
        return None

def show_results_analysis(model, results, X, y):
    """显示结果分析"""
    
    st.markdown("## 📊 结果分析")
    
    # 性能指标概览
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("准确率", f"{results['accuracy']:.4f}")
    
    with col2:
        cv_mean = results['cv_scores'].mean()
        st.metric("交叉验证均值", f"{cv_mean:.4f}")
    
    with col3:
        cv_std = results['cv_scores'].std()
        st.metric("交叉验证标准差", f"{cv_std:.4f}")
    
    with col4:
        n_samples = len(results['y_test'])
        st.metric("测试样本数", n_samples)
    
    # 详细分析标签页
    analysis_tabs = st.tabs(["📈 性能指标", "🔥 混淆矩阵", "📊 分类报告", "📉 学习曲线"])
    
    with analysis_tabs[0]:
        show_performance_metrics(results)
    
    with analysis_tabs[1]:
        show_confusion_matrix(results)
    
    with analysis_tabs[2]:
        show_classification_report(results)
    
    with analysis_tabs[3]:
        show_learning_curve(results)

def show_performance_metrics(results):
    """显示性能指标"""
    
    st.markdown("### 📈 性能指标详情")
    
    # 交叉验证分数分布
    fig = go.Figure()
    
    fig.add_trace(go.Box(
        y=results['cv_scores'],
        name='交叉验证分数',
        boxpoints='all',
        jitter=0.3,
        pointpos=-1.8
    ))
    
    fig.update_layout(
        title="交叉验证分数分布",
        yaxis_title="准确率",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 性能统计
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**交叉验证统计:**")
        cv_stats = {
            '均值': results['cv_scores'].mean(),
            '标准差': results['cv_scores'].std(),
            '最小值': results['cv_scores'].min(),
            '最大值': results['cv_scores'].max(),
            '中位数': np.median(results['cv_scores'])
        }
        
        for stat, value in cv_stats.items():
            st.markdown(f"- {stat}: {value:.4f}")
    
    with col2:
        st.markdown("**模型稳定性:**")
        cv_mean = results['cv_scores'].mean()
        cv_std = results['cv_scores'].std()
        
        if cv_std < 0.01:
            stability = "非常稳定"
        elif cv_std < 0.05:
            stability = "稳定"
        elif cv_std < 0.1:
            stability = "中等稳定"
        else:
            stability = "不稳定"
        
        st.markdown(f"- 稳定性评级: **{stability}**")
        st.markdown(f"- 变异系数: {(cv_std/cv_mean)*100:.2f}%")

def show_confusion_matrix(results):
    """显示混淆矩阵"""
    
    st.markdown("### 🔥 混淆矩阵")
    
    conf_matrix = results['confusion_matrix']
    
    # 使用plotly创建热力图
    fig = px.imshow(
        conf_matrix,
        labels=dict(x="预测类别", y="真实类别", color="样本数量"),
        x=[f"类别 {i}" for i in range(conf_matrix.shape[1])],
        y=[f"类别 {i}" for i in range(conf_matrix.shape[0])],
        color_continuous_scale='Blues',
        text_auto=True
    )
    
    fig.update_layout(
        title="混淆矩阵",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 混淆矩阵分析
    st.markdown("**混淆矩阵分析:**")
    
    # 计算每个类别的精确率和召回率
    n_classes = conf_matrix.shape[0]
    
    for i in range(n_classes):
        tp = conf_matrix[i, i]
        fp = conf_matrix[:, i].sum() - tp
        fn = conf_matrix[i, :].sum() - tp
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        st.markdown(f"- **类别 {i}**: 精确率 {precision:.3f}, 召回率 {recall:.3f}")

def show_classification_report(results):
    """显示分类报告"""
    
    st.markdown("### 📊 分类报告")
    
    class_report = results['classification_report']
    
    # 转换为DataFrame显示
    report_df = pd.DataFrame(class_report).transpose()
    
    # 格式化数值
    numeric_columns = ['precision', 'recall', 'f1-score']
    for col in numeric_columns:
        if col in report_df.columns:
            report_df[col] = report_df[col].apply(lambda x: f"{x:.4f}" if isinstance(x, (int, float)) else x)
    
    if 'support' in report_df.columns:
        report_df['support'] = report_df['support'].apply(lambda x: int(x) if isinstance(x, (int, float)) else x)
    
    st.dataframe(report_df, use_container_width=True)
    
    # 可视化分类报告
    if len(class_report) > 3:  # 确保有足够的类别数据
        metrics_data = []
        
        for class_name, metrics in class_report.items():
            if isinstance(metrics, dict) and class_name not in ['accuracy', 'macro avg', 'weighted avg']:
                metrics_data.append({
                    '类别': class_name,
                    '精确率': metrics['precision'],
                    '召回率': metrics['recall'],
                    'F1分数': metrics['f1-score']
                })
        
        if metrics_data:
            metrics_df = pd.DataFrame(metrics_data)
            
            # 创建柱状图
            fig = px.bar(
                metrics_df.melt(id_vars=['类别'], var_name='指标', value_name='分数'),
                x='类别',
                y='分数',
                color='指标',
                barmode='group',
                title="各类别性能指标对比"
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

def show_learning_curve(results):
    """显示学习曲线"""
    
    st.markdown("### 📉 学习曲线")
    
    train_sizes = results['train_sizes']
    train_scores = results['train_scores']
    val_scores = results['val_scores']
    
    # 计算均值和标准差
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    val_std = np.std(val_scores, axis=1)
    
    # 创建学习曲线图
    fig = go.Figure()
    
    # 训练分数
    fig.add_trace(go.Scatter(
        x=train_sizes,
        y=train_mean,
        mode='lines+markers',
        name='训练分数',
        line=dict(color='blue'),
        error_y=dict(type='data', array=train_std, visible=True)
    ))
    
    # 验证分数
    fig.add_trace(go.Scatter(
        x=train_sizes,
        y=val_mean,
        mode='lines+markers',
        name='验证分数',
        line=dict(color='red'),
        error_y=dict(type='data', array=val_std, visible=True)
    ))
    
    fig.update_layout(
        title="学习曲线",
        xaxis_title="训练样本数量",
        yaxis_title="准确率",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 学习曲线分析
    st.markdown("**学习曲线分析:**")
    
    final_train_score = train_mean[-1]
    final_val_score = val_mean[-1]
    gap = final_train_score - final_val_score
    
    if gap < 0.05:
        analysis = "模型拟合良好，训练和验证性能接近"
    elif gap < 0.1:
        analysis = "模型轻微过拟合，可以考虑增加正则化"
    elif gap < 0.2:
        analysis = "模型过拟合，建议增加正则化或减少模型复杂度"
    else:
        analysis = "模型严重过拟合，需要显著调整模型参数"
    
    st.markdown(f"- {analysis}")
    st.markdown(f"- 训练-验证分数差距: {gap:.4f}")
    
    if val_mean[-1] < val_mean[0]:
        st.markdown("- ⚠️ 验证分数下降，可能存在过拟合")
    else:
        st.markdown("- ✅ 验证分数稳定或上升，模型学习正常")

def show_algorithm_visualization(algorithm_name, model, X, y, results):
    """显示算法可视化"""
    
    st.markdown("## 🔍 算法可视化")
    
    # 创建可视化标签页
    viz_tabs = st.tabs(["🎯 决策边界", "📊 特征重要性", "🔄 ROC曲线", "📈 预测分布"])
    
    with viz_tabs[0]:
        show_decision_boundary(model, results, X, y)
    
    with viz_tabs[1]:
        show_feature_importance(algorithm_name, model, X)
    
    with viz_tabs[2]:
        show_roc_curve(results)
    
    with viz_tabs[3]:
        show_prediction_distribution(results)

def show_decision_boundary(model, results, X, y):
    """显示决策边界"""
    
    st.markdown("### 🎯 决策边界可视化")
    
    if X.shape[1] > 2:
        st.info("数据维度大于2，使用PCA降维到2D进行可视化")
        
        from sklearn.decomposition import PCA
        
        # PCA降维
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X)
        
        # 重新训练模型（在降维数据上）
        model_2d = create_model(st.session_state.trained_model['algorithm_name'], 
                               st.session_state.trained_model['params'])
        
        if model_2d is not None:
            model_2d.fit(X_pca, y)
            
            # 创建网格
            h = 0.02
            x_min, x_max = X_pca[:, 0].min() - 1, X_pca[:, 0].max() + 1
            y_min, y_max = X_pca[:, 1].min() - 1, X_pca[:, 1].max() + 1
            xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                               np.arange(y_min, y_max, h))
            
            # 预测网格点
            try:
                Z = model_2d.predict(np.c_[xx.ravel(), yy.ravel()])
                Z = Z.reshape(xx.shape)
                
                # 创建决策边界图
                fig = go.Figure()
                
                # 添加决策边界
                fig.add_trace(go.Contour(
                    x=np.arange(x_min, x_max, h),
                    y=np.arange(y_min, y_max, h),
                    z=Z,
                    colorscale='Viridis',
                    opacity=0.3,
                    showscale=False,
                    hoverinfo='skip'
                ))
                
                # 添加数据点
                colors = px.colors.qualitative.Set1
                for i, class_label in enumerate(np.unique(y)):
                    mask = y == class_label
                    fig.add_trace(go.Scatter(
                        x=X_pca[mask, 0],
                        y=X_pca[mask, 1],
                        mode='markers',
                        name=f'类别 {class_label}',
                        marker=dict(
                            color=colors[i % len(colors)],
                            size=8,
                            line=dict(width=1, color='white')
                        )
                    ))
                
                fig.update_layout(
                    title="决策边界 (PCA降维)",
                    xaxis_title="第一主成分",
                    yaxis_title="第二主成分",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # PCA解释
                explained_ratio = pca.explained_variance_ratio_
                st.markdown(f"**PCA信息:**")
                st.markdown(f"- 第一主成分解释方差比: {explained_ratio[0]:.3f}")
                st.markdown(f"- 第二主成分解释方差比: {explained_ratio[1]:.3f}")
                st.markdown(f"- 总解释方差比: {explained_ratio.sum():.3f}")
                
            except Exception as e:
                st.warning(f"无法生成决策边界: {str(e)}")
    
    else:
        st.info("数据已经是2D，直接显示决策边界")
        # 对于2D数据的决策边界可视化
        # 这里可以添加2D决策边界的代码

def show_feature_importance(algorithm_name, model, X):
    """显示特征重要性"""
    
    st.markdown("### 📊 特征重要性")
    
    try:
        # 获取特征重要性
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importances = np.abs(model.coef_[0]) if len(model.coef_.shape) > 1 else np.abs(model.coef_)
        else:
            st.info(f"{algorithm_name} 不支持特征重要性分析")
            return
        
        # 创建特征名称
        if 'generated_data' in st.session_state and 'feature_names' in st.session_state.generated_data:
            feature_names = st.session_state.generated_data['feature_names']
        else:
            feature_names = [f'特征_{i+1}' for i in range(len(importances))]
        
        # 创建DataFrame
        importance_df = pd.DataFrame({
            '特征': feature_names,
            '重要性': importances
        }).sort_values('重要性', ascending=True)
        
        # 创建水平柱状图
        fig = px.bar(
            importance_df,
            x='重要性',
            y='特征',
            orientation='h',
            title="特征重要性排名",
            color='重要性',
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(height=max(400, len(feature_names) * 30))
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示重要性数值
        st.markdown("**特征重要性数值:**")
        importance_display = importance_df.sort_values('重要性', ascending=False)
        
        for _, row in importance_display.iterrows():
            st.markdown(f"- {row['特征']}: {row['重要性']:.4f}")
        
    except Exception as e:
        st.warning(f"无法显示特征重要性: {str(e)}")

def show_roc_curve(results):
    """显示ROC曲线"""
    
    st.markdown("### 🔄 ROC曲线")
    
    if 'y_proba' not in results:
        st.info("当前模型不支持概率预测，无法绘制ROC曲线")
        return
    
    try:
        y_test = results['y_test']
        y_proba = results['y_proba']
        
        n_classes = len(np.unique(y_test))
        
        if n_classes == 2:
            # 二分类ROC曲线
            fpr, tpr, _ = roc_curve(y_test, y_proba[:, 1])
            roc_auc = auc(fpr, tpr)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=fpr,
                y=tpr,
                mode='lines',
                name=f'ROC曲线 (AUC = {roc_auc:.3f})',
                line=dict(color='blue', width=2)
            ))
            
            # 添加对角线
            fig.add_trace(go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode='lines',
                name='随机分类器',
                line=dict(color='red', dash='dash')
            ))
            
            fig.update_layout(
                title="ROC曲线",
                xaxis_title="假正率 (FPR)",
                yaxis_title="真正率 (TPR)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # AUC解释
            if roc_auc > 0.9:
                performance = "优秀"
            elif roc_auc > 0.8:
                performance = "良好"
            elif roc_auc > 0.7:
                performance = "一般"
            else:
                performance = "较差"
            
            st.markdown(f"**AUC分析:** {roc_auc:.3f} ({performance})")
        
        else:
            # 多分类ROC曲线
            from sklearn.preprocessing import label_binarize
            from sklearn.metrics import roc_curve, auc
            
            # 二值化标签
            y_test_bin = label_binarize(y_test, classes=np.unique(y_test))
            
            fig = go.Figure()
            
            # 为每个类别绘制ROC曲线
            for i in range(n_classes):
                fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_proba[:, i])
                roc_auc = auc(fpr, tpr)
                
                fig.add_trace(go.Scatter(
                    x=fpr,
                    y=tpr,
                    mode='lines',
                    name=f'类别 {i} (AUC = {roc_auc:.3f})'
                ))
            
            # 添加对角线
            fig.add_trace(go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode='lines',
                name='随机分类器',
                line=dict(color='black', dash='dash')
            ))
            
            fig.update_layout(
                title="多分类ROC曲线",
                xaxis_title="假正率 (FPR)",
                yaxis_title="真正率 (TPR)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.warning(f"无法绘制ROC曲线: {str(e)}")

def show_prediction_distribution(results):
    """显示预测分布"""
    
    st.markdown("### 📈 预测分布")
    
    y_test = results['y_test']
    y_pred = results['y_pred']
    
    # 预测结果统计
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**真实标签分布:**")
        true_counts = pd.Series(y_test).value_counts().sort_index()
        
        fig = px.bar(
            x=true_counts.index,
            y=true_counts.values,
            title="真实标签分布",
            labels={'x': '类别', 'y': '数量'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**预测标签分布:**")
        pred_counts = pd.Series(y_pred).value_counts().sort_index()
        
        fig = px.bar(
            x=pred_counts.index,
            y=pred_counts.values,
            title="预测标签分布",
            labels={'x': '类别', 'y': '数量'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 预测概率分布（如果可用）
    if 'y_proba' in results:
        st.markdown("**预测概率分布:**")
        
        y_proba = results['y_proba']
        n_classes = y_proba.shape[1]
        
        # 为每个类别创建概率分布图
        fig = make_subplots(
            rows=1, cols=n_classes,
            subplot_titles=[f'类别 {i} 概率分布' for i in range(n_classes)]
        )
        
        for i in range(n_classes):
            fig.add_trace(
                go.Histogram(
                    x=y_proba[:, i],
                    name=f'类别 {i}',
                    nbinsx=20
                ),
                row=1, col=i+1
            )
        
        fig.update_layout(
            title="各类别预测概率分布",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 预测准确性分析
    st.markdown("**预测准确性分析:**")
    
    correct_predictions = (y_test == y_pred).sum()
    total_predictions = len(y_test)
    accuracy = correct_predictions / total_predictions
    
    st.markdown(f"- 正确预测: {correct_predictions}/{total_predictions}")
    st.markdown(f"- 准确率: {accuracy:.4f}")
    
    # 各类别准确率
    class_accuracy = {}
    for class_label in np.unique(y_test):
        mask = y_test == class_label
        class_correct = (y_test[mask] == y_pred[mask]).sum()
        class_total = mask.sum()
        class_accuracy[class_label] = class_correct / class_total if class_total > 0 else 0
    
    st.markdown("**各类别准确率:**")
    for class_label, acc in class_accuracy.items():
        st.markdown(f"- 类别 {class_label}: {acc:.4f}")