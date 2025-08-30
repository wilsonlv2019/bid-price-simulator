"""结果分析页面模块
提供详细的模型性能分析、可视化和决策边界展示
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.metrics import (
    confusion_matrix, classification_report, roc_curve, auc,
    precision_recall_curve, average_precision_score,
    accuracy_score, precision_score, recall_score, f1_score
)
from sklearn.decomposition import PCA
from sklearn.preprocessing import label_binarize
from sklearn.model_selection import validation_curve
import time
import json
from datetime import datetime
from modules.utils import (
    plot_confusion_matrix, plot_roc_curves, plot_learning_curves,
    plot_feature_importance, format_metrics_table, create_metric_card
)
import warnings
warnings.filterwarnings('ignore')

def show_results_analysis_page():
    """显示结果分析页面"""
    
    st.markdown('<div class="main-header">📊 结果分析中心</div>', unsafe_allow_html=True)
    
    # 检查是否有训练结果
    if 'trained_model' not in st.session_state or 'training_results' not in st.session_state:
        show_no_results_message()
        return
    
    # 获取数据和结果
    model = st.session_state.trained_model
    results = st.session_state.training_results
    data = st.session_state.generated_data
    X, y = data['X'], data['y']
    
    # 侧边栏配置
    with st.sidebar:
        st.markdown("### 📊 分析配置")
        
        # 分析类型选择
        analysis_types = st.multiselect(
            "选择分析类型",
            ["性能概览", "详细指标", "混淆矩阵", "ROC曲线", "PR曲线",
             "特征重要性", "学习曲线", "预测分布", "类别分析", 
             "决策边界", "模型比较", "误差分析"],
            default=["性能概览", "混淆矩阵", "ROC曲线"]
        )
        
        # 可视化配置
        st.markdown("#### 🎨 可视化配置")
        
        plot_style = st.selectbox(
            "图表风格",
            ["默认", "深色", "简洁", "科学", "商务"]
        )
        
        color_scheme = st.selectbox(
            "配色方案",
            ["默认", "蓝色系", "红色系", "绿色系", "紫色系", "彩虹"]
        )
        
        # 高级选项
        st.markdown("#### ⚙️ 高级选项")
        show_confidence_intervals = st.checkbox("显示置信区间", value=True)
        show_statistical_tests = st.checkbox("显示统计检验", value=False)
        interactive_plots = st.checkbox("交互式图表", value=True)
        
        # 导出选项
        st.markdown("#### 📤 导出选项")
        
        if st.button("📊 生成分析报告", use_container_width=True):
            generate_analysis_report(model, results, X, y)
        
        if st.button("📈 导出图表", use_container_width=True):
            export_charts()
    
    # 主要内容区域
    show_analysis_content(model, results, X, y, analysis_types, plot_style, color_scheme)

def show_no_results_message():
    """显示无结果提示"""
    
    st.markdown("## ⚠️ 没有可分析的结果")
    st.markdown("""
    请先训练模型才能进行结果分析。
    
    您可以：
    1. 前往 **模型训练** 页面训练模型
    2. 加载已保存的模型
    3. 使用示例数据进行演示
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 前往模型训练", use_container_width=True):
            st.session_state.current_page = 'model_training'
            st.rerun()

def generate_sample_results():
    """生成示例分析结果"""
    
    # 创建示例数据
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    
    # 生成示例数据集
    X, y = make_classification(n_samples=1000, n_features=10, n_classes=3, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 训练示例模型
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    
    # 生成预测结果
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    
    # 计算指标
    results = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted'),
        'recall': recall_score(y_test, y_pred, average='weighted'),
        'f1': f1_score(y_test, y_pred, average='weighted'),
        'confusion_matrix': confusion_matrix(y_test, y_pred),
        'test_predictions': y_pred,
        'test_probabilities': y_proba,
        'training_time': 0.5
    }
    
    # 保存到session state
    st.session_state.trained_model = model
    st.session_state.training_results = results
    st.session_state.generated_data = {'X': X, 'y': y}
    
    st.success("✅ 示例分析结果已生成！")
    
    with col2:
        if st.button("📁 加载模型", use_container_width=True):
            show_model_loading_interface()
    
    with col3:
        if st.button("📊 生成示例结果", use_container_width=True):
            generate_sample_results()
            st.rerun()

def show_model_loading_interface():
    """显示模型加载界面"""
    
    st.markdown("### 📁 加载已训练模型")
    
    # 从保存的模型中选择
    if 'saved_models' in st.session_state and st.session_state.saved_models:
        st.markdown("#### 💾 已保存的模型")
        
        model_names = list(st.session_state.saved_models.keys())
        selected_model = st.selectbox("选择模型", model_names)
        
        if st.button("加载选中模型"):
            model_data = st.session_state.saved_models[selected_model]
            st.session_state.trained_model = model_data['model']
            st.session_state.training_results = model_data['results']
            st.success(f"✅ 模型 '{selected_model}' 加载成功！")
            st.rerun()
    
    # 上传模型文件
    st.markdown("#### 📤 上传模型文件")
    
    uploaded_file = st.file_uploader(
        "选择模型文件",
        type=['pkl', 'joblib'],
        help="上传之前保存的模型文件",
        key="analysis_model_uploader"
    )
    
    if uploaded_file is not None:
        if st.button("加载上传的模型"):
            try:
                import joblib
                model = joblib.load(uploaded_file)
                st.session_state.trained_model = model
                st.success("✅ 模型上传成功！")
                st.rerun()
            except Exception as e:
                st.error(f"模型加载失败: {str(e)}")

def show_analysis_content(model, results, X, y, analysis_types, plot_style, color_scheme):
    """显示分析内容"""
    
    # 设置图表样式
    set_plot_style(plot_style)
    
    # 创建标签页
    tabs = st.tabs(["📈 性能分析", "🔍 详细分析", "📊 可视化", "📋 报告"])
    
    with tabs[0]:
        if "性能概览" in analysis_types:
            show_performance_overview(model, results, X, y)
        if "详细指标" in analysis_types:
            show_performance_details(model, results, X, y)
    
    with tabs[1]:
        if "混淆矩阵" in analysis_types:
            show_confusion_matrix_analysis(model, results, X, y)
        if "误差分析" in analysis_types:
            show_error_analysis(model, results, X, y)
        if "类别分析" in analysis_types:
            show_class_analysis(model, results, X, y)
    
    with tabs[2]:
        if "ROC曲线" in analysis_types:
            show_roc_analysis(model, results, X, y)
        if "PR曲线" in analysis_types:
            show_pr_curve_analysis(model, results, X, y)
        if "特征重要性" in analysis_types:
            show_feature_importance_analysis(model, results, X, y)
        if "学习曲线" in analysis_types:
            show_learning_curve_analysis(model, results, X, y)
        if "预测分布" in analysis_types:
            show_prediction_distribution(model, results, X, y)
        if "决策边界" in analysis_types:
            show_decision_boundary(model, results, X, y)
    
    with tabs[3]:
        show_analysis_summary(model, results, X, y, analysis_types)

def show_performance_overview(model, results, X, y):
    """显示性能概览"""
    
    st.markdown("### 📊 模型性能概览")
    
    # 核心指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        accuracy = results.get('accuracy', 0)
        st.metric(
            "准确率", 
            f"{accuracy:.4f}",
            delta=f"{(accuracy - 0.5):.4f}" if accuracy > 0.5 else None
        )
    
    with col2:
        precision = results.get('precision', 0)
        st.metric(
            "精确率", 
            f"{precision:.4f}",
            delta=f"{(precision - 0.5):.4f}" if precision > 0.5 else None
        )
    
    with col3:
        recall = results.get('recall', 0)
        st.metric(
            "召回率", 
            f"{recall:.4f}",
            delta=f"{(recall - 0.5):.4f}" if recall > 0.5 else None
        )
    
    with col4:
        f1 = results.get('f1', 0)
        st.metric(
            "F1分数", 
            f"{f1:.4f}",
            delta=f"{(f1 - 0.5):.4f}" if f1 > 0.5 else None
        )
    
    # 性能雷达图
    st.markdown("#### 🎯 性能雷达图")
    show_performance_radar(results)
    
    # 模型基本信息
    st.markdown("#### ℹ️ 模型基本信息")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**模型类型**: {type(model).__name__}")
    
    with col2:
        st.info(f"**数据集大小**: {len(X)} 样本")
    
    with col3:
        st.info(f"**特征数量**: {X.shape[1]} 个")

def show_performance_details(model, results, X, y):
    """显示性能详情"""
    
    st.markdown("### 🎯 详细性能分析")
    
    # 分类报告
    if 'test_predictions' in results:
        st.markdown("#### 📋 分类报告")
        
        # 重新计算测试集（如果需要）
        from sklearn.model_selection import train_test_split
        _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        y_pred = results['test_predictions']
        
        # 生成分类报告
        from sklearn.metrics import classification_report
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # 转换为DataFrame显示
        report_df = pd.DataFrame(report).transpose()
        st.dataframe(report_df.round(4), use_container_width=True)
    
    # 交叉验证结果
    if 'cv_scores' in results and results['cv_scores'] is not None:
        st.markdown("#### ✅ 交叉验证结果")
        
        cv_scores = results['cv_scores']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("平均分数", f"{cv_scores.mean():.4f}")
        
        with col2:
            st.metric("标准差", f"{cv_scores.std():.4f}")
        
        with col3:
            st.metric("95%置信区间", f"±{cv_scores.std()*1.96:.4f}")
        
        # 交叉验证分数分布
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            y=cv_scores,
            name="交叉验证分数",
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8
        ))
        
        fig.update_layout(
            title="交叉验证分数分布",
            yaxis_title="分数",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 预测概率分布
    if 'test_probabilities' in results and results['test_probabilities'] is not None:
        st.markdown("#### 📊 预测概率分布")
        show_prediction_probability_distribution(results['test_probabilities'])

def show_deep_analysis(model, results, X, y):
    """显示深度分析"""
    
    st.markdown("### 🔍 深度分析")
    
    # 特征重要性
    if hasattr(model, 'feature_importances_'):
        st.markdown("#### 🎯 特征重要性")
        show_feature_importance(model, X.shape[1])
    
    # 学习曲线
    st.markdown("#### 📈 学习曲线")
    show_learning_curves(model, X, y)
    
    # 决策边界（仅适用于2D数据）
    if X.shape[1] == 2:
        st.markdown("#### 🎨 决策边界")
        show_decision_boundary(model, X, y)
    elif X.shape[1] > 2:
        st.markdown("#### 🎨 决策边界（PCA降维）")
        show_decision_boundary_pca(model, X, y)
    
    # 误差分析
    if 'test_predictions' in results:
        st.markdown("#### ❌ 误差分析")
        show_error_analysis(model, results, X, y)

def show_visualization_charts(model, results, X, y, color_scheme):
    """显示可视化图表"""
    
    st.markdown("### 📈 可视化图表集合")
    
    # 设置配色方案
    colors = get_color_scheme(color_scheme)
    
    # 创建子图
    col1, col2 = st.columns(2)
    
    with col1:
        # 性能对比图
        st.markdown("#### 📊 性能指标对比")
        show_metrics_comparison(results, colors)
        
        # 类别分布
        st.markdown("#### 🥧 类别分布")
        show_class_distribution(y, colors)
    
    with col2:
        # 预测结果分布
        if 'test_predictions' in results:
            st.markdown("#### 📈 预测结果分布")
            show_prediction_distribution(results['test_predictions'], colors)
        
        # 训练时间分析
        if 'training_time' in results:
            st.markdown("#### ⏱️ 训练效率")
            show_training_efficiency(results, colors)
    
    # 综合可视化
    st.markdown("#### 🎨 综合可视化面板")
    show_comprehensive_visualization(model, results, X, y, colors)

def show_performance_radar(results):
    """显示性能雷达图"""
    
    metrics = ['准确率', '精确率', '召回率', 'F1分数']
    values = [
        results.get('accuracy', 0),
        results.get('precision', 0),
        results.get('recall', 0),
        results.get('f1', 0)
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=metrics,
        fill='toself',
        name='模型性能',
        line_color='rgb(0, 123, 255)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        title="模型性能雷达图",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_confusion_matrix(cm):
    """显示混淆矩阵"""
    
    # 计算百分比
    cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100
    
    # 创建热力图
    fig = go.Figure(data=go.Heatmap(
        z=cm,
        text=[[f'{cm[i][j]}<br>({cm_percent[i][j]:.1f}%)' 
               for j in range(cm.shape[1])] 
              for i in range(cm.shape[0])],
        texttemplate="%{text}",
        textfont={"size": 12},
        colorscale='Blues',
        showscale=True
    ))
    
    fig.update_layout(
        title="混淆矩阵",
        xaxis_title="预测类别",
        yaxis_title="真实类别",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 混淆矩阵分析
    st.markdown("**混淆矩阵分析：**")
    
    # 计算每个类别的性能
    n_classes = cm.shape[0]
    
    for i in range(n_classes):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        tn = cm.sum() - tp - fp - fn
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        st.markdown(f"- **类别 {i}**: 精确率 {precision:.3f}, 召回率 {recall:.3f}")

def show_roc_curve(roc_data):
    """显示ROC曲线"""
    
    fpr, tpr, auc_score = roc_data
    
    fig = go.Figure()
    
    # ROC曲线
    fig.add_trace(go.Scatter(
        x=fpr, y=tpr,
        name=f'ROC曲线 (AUC = {auc_score:.3f})',
        line=dict(color='blue', width=3)
    ))
    
    # 随机分类器基线
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        name='随机分类器 (AUC = 0.5)',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    # 完美分类器
    fig.add_trace(go.Scatter(
        x=[0, 0, 1], y=[0, 1, 1],
        name='完美分类器 (AUC = 1.0)',
        line=dict(color='green', width=2, dash='dot')
    ))
    
    fig.update_layout(
        title=f'ROC曲线分析 (AUC = {auc_score:.3f})',
        xaxis_title='假正率 (FPR)',
        yaxis_title='真正率 (TPR)',
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # AUC解释
    if auc_score >= 0.9:
        interpretation = "🌟 优秀 - 模型性能非常好"
    elif auc_score >= 0.8:
        interpretation = "👍 良好 - 模型性能较好"
    elif auc_score >= 0.7:
        interpretation = "👌 一般 - 模型性能中等"
    elif auc_score >= 0.6:
        interpretation = "⚠️ 较差 - 模型性能偏低"
    else:
        interpretation = "❌ 很差 - 模型性能很差"
    
    st.markdown(f"**AUC解释：** {interpretation}")

def show_feature_importance(model, n_features):
    """显示特征重要性"""
    
    importances = model.feature_importances_
    feature_names = [f'特征_{i+1}' for i in range(n_features)]
    
    # 创建DataFrame
    importance_df = pd.DataFrame({
        '特征': feature_names,
        '重要性': importances
    }).sort_values('重要性', ascending=True)
    
    # 水平条形图
    fig = px.bar(
        importance_df, 
        x='重要性', 
        y='特征',
        orientation='h',
        title='特征重要性排序',
        color='重要性',
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(height=max(400, n_features * 30))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 重要性统计
    st.markdown("**特征重要性统计：**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("最重要特征", feature_names[np.argmax(importances)])
    
    with col2:
        st.metric("平均重要性", f"{importances.mean():.4f}")
    
    with col3:
        top_3_ratio = np.sort(importances)[-3:].sum()
        st.metric("前3特征占比", f"{top_3_ratio:.2%}")

def show_learning_curves(model, X, y):
    """显示学习曲线"""
    
    from sklearn.model_selection import learning_curve
    
    try:
        # 计算学习曲线
        train_sizes, train_scores, val_scores = learning_curve(
            model, X, y, cv=5, n_jobs=-1, 
            train_sizes=np.linspace(0.1, 1.0, 10),
            random_state=42
        )
        
        # 计算均值和标准差
        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        val_mean = np.mean(val_scores, axis=1)
        val_std = np.std(val_scores, axis=1)
        
        fig = go.Figure()
        
        # 训练分数
        fig.add_trace(go.Scatter(
            x=train_sizes, y=train_mean,
            name='训练分数',
            line=dict(color='blue'),
            mode='lines+markers'
        ))
        
        # 训练分数置信区间
        fig.add_trace(go.Scatter(
            x=np.concatenate([train_sizes, train_sizes[::-1]]),
            y=np.concatenate([train_mean + train_std, (train_mean - train_std)[::-1]]),
            fill='toself',
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='训练分数置信区间',
            showlegend=False
        ))
        
        # 验证分数
        fig.add_trace(go.Scatter(
            x=train_sizes, y=val_mean,
            name='验证分数',
            line=dict(color='red'),
            mode='lines+markers'
        ))
        
        # 验证分数置信区间
        fig.add_trace(go.Scatter(
            x=np.concatenate([train_sizes, train_sizes[::-1]]),
            y=np.concatenate([val_mean + val_std, (val_mean - val_std)[::-1]]),
            fill='toself',
            fillcolor='rgba(255,0,0,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='验证分数置信区间',
            showlegend=False
        ))
        
        fig.update_layout(
            title='学习曲线',
            xaxis_title='训练样本数量',
            yaxis_title='分数',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 学习曲线分析
        final_gap = train_mean[-1] - val_mean[-1]
        
        if final_gap < 0.05:
            analysis = "✅ 模型拟合良好，训练和验证性能接近"
        elif final_gap < 0.1:
            analysis = "⚠️ 模型轻微过拟合，可以考虑增加正则化"
        else:
            analysis = "❌ 模型过拟合严重，需要增加正则化或减少模型复杂度"
        
        st.markdown(f"**学习曲线分析：** {analysis}")
        
    except Exception as e:
        st.error(f"学习曲线计算失败: {str(e)}")

def show_decision_boundary(model, X, y):
    """显示2D决策边界"""
    
    # 创建网格
    h = 0.02
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))
    
    # 预测网格点
    try:
        Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)
        
        # 创建决策边界图
        fig = go.Figure()
        
        # 决策边界
        fig.add_trace(go.Contour(
            x=np.arange(x_min, x_max, h),
            y=np.arange(y_min, y_max, h),
            z=Z,
            showscale=False,
            opacity=0.3,
            colorscale='RdYlBu'
        ))
        
        # 数据点
        colors = ['red', 'blue', 'green', 'orange', 'purple']
        for i, class_label in enumerate(np.unique(y)):
            mask = y == class_label
            fig.add_trace(go.Scatter(
                x=X[mask, 0],
                y=X[mask, 1],
                mode='markers',
                name=f'类别 {class_label}',
                marker=dict(
                    color=colors[i % len(colors)],
                    size=8,
                    line=dict(width=1, color='black')
                )
            ))
        
        fig.update_layout(
            title='决策边界可视化',
            xaxis_title='特征 1',
            yaxis_title='特征 2',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"决策边界绘制失败: {str(e)}")

def show_decision_boundary_pca(model, X, y):
    """显示PCA降维后的决策边界"""
    
    # PCA降维到2D
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    
    # 在PCA空间中训练一个新模型（用于可视化）
    from sklearn.base import clone
    model_pca = clone(model)
    model_pca.fit(X_pca, y)
    
    # 显示决策边界
    show_decision_boundary(model_pca, X_pca, y)
    
    # 显示PCA信息
    st.markdown("**PCA降维信息：**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("第一主成分方差比", f"{pca.explained_variance_ratio_[0]:.3f}")
    
    with col2:
        st.metric("第二主成分方差比", f"{pca.explained_variance_ratio_[1]:.3f}")
    
    total_variance = pca.explained_variance_ratio_.sum()
    st.metric("总方差解释比例", f"{total_variance:.3f}")

def show_error_analysis(model, results, X, y):
    """显示误差分析"""
    
    from sklearn.model_selection import train_test_split
    
    # 重新分割数据
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    y_pred = results['test_predictions']
    
    # 找出错误分类的样本
    errors = y_test != y_pred
    error_indices = np.where(errors)[0]
    
    st.markdown(f"**错误分类样本数量：** {len(error_indices)} / {len(y_test)} ({len(error_indices)/len(y_test)*100:.1f}%)")
    
    if len(error_indices) > 0:
        # 错误类型分析
        error_types = {}
        for i in error_indices:
            true_label = y_test[i]
            pred_label = y_pred[i]
            error_type = f"{true_label} → {pred_label}"
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # 错误类型分布
        error_df = pd.DataFrame(list(error_types.items()), columns=['错误类型', '数量'])
        error_df = error_df.sort_values('数量', ascending=False)
        
        fig = px.bar(
            error_df, 
            x='错误类型', 
            y='数量',
            title='错误分类类型分布'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示具体错误样本（如果是2D数据）
        if X.shape[1] == 2:
            st.markdown("#### 错误分类样本可视化")
            
            fig = go.Figure()
            
            # 正确分类的样本
            correct_mask = ~errors
            fig.add_trace(go.Scatter(
                x=X_test[correct_mask, 0],
                y=X_test[correct_mask, 1],
                mode='markers',
                name='正确分类',
                marker=dict(color='green', size=6, opacity=0.6)
            ))
            
            # 错误分类的样本
            fig.add_trace(go.Scatter(
                x=X_test[errors, 0],
                y=X_test[errors, 1],
                mode='markers',
                name='错误分类',
                marker=dict(color='red', size=10, symbol='x')
            ))
            
            fig.update_layout(
                title='错误分类样本分布',
                xaxis_title='特征 1',
                yaxis_title='特征 2',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)

def show_prediction_probability_distribution(probabilities):
    """显示预测概率分布"""
    
    n_classes = probabilities.shape[1]
    
    fig = make_subplots(
        rows=1, cols=n_classes,
        subplot_titles=[f'类别 {i} 概率分布' for i in range(n_classes)]
    )
    
    for i in range(n_classes):
        fig.add_trace(
            go.Histogram(
                x=probabilities[:, i],
                name=f'类别 {i}',
                nbinsx=30
            ),
            row=1, col=i+1
        )
    
    fig.update_layout(
        title='预测概率分布',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_metrics_comparison(results, colors):
    """显示指标对比"""
    
    metrics = ['准确率', '精确率', '召回率', 'F1分数']
    values = [
        results.get('accuracy', 0),
        results.get('precision', 0),
        results.get('recall', 0),
        results.get('f1', 0)
    ]
    
    fig = px.bar(
        x=metrics, 
        y=values,
        title='性能指标对比',
        color=values,
        color_continuous_scale=colors['primary']
    )
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

def show_class_distribution(y, colors):
    """显示类别分布"""
    
    unique, counts = np.unique(y, return_counts=True)
    
    fig = px.pie(
        values=counts,
        names=[f'类别 {i}' for i in unique],
        title='类别分布'
    )
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

def show_prediction_distribution(model, results, X, y):
    """显示预测分布"""
    st.markdown("#### 📊 预测分布分析")
    
    if 'test_probabilities' not in results:
        st.warning("⚠️ 没有预测概率数据")
        return
    
    probabilities = results['test_probabilities']
    predictions = results.get('test_predictions', [])
    
    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["概率分布", "置信度分析", "预测统计"])
    
    with tab1:
        # 预测概率分布
        st.markdown("**各类别预测概率分布**")
        
        if probabilities.shape[1] <= 5:  # 如果类别数不多，显示所有类别
            fig = make_subplots(
                rows=1, cols=probabilities.shape[1],
                subplot_titles=[f'类别 {i}' for i in range(probabilities.shape[1])]
            )
            
            for i in range(probabilities.shape[1]):
                fig.add_trace(
                    go.Histogram(
                        x=probabilities[:, i],
                        name=f'类别 {i}',
                        nbinsx=30,
                        opacity=0.7
                    ),
                    row=1, col=i+1
                )
            
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            # 如果类别太多，只显示选中的类别
            selected_class = st.selectbox(
                "选择要查看的类别",
                range(probabilities.shape[1])
            )
            
            fig = px.histogram(
                x=probabilities[:, selected_class],
                nbins=30,
                title=f'类别 {selected_class} 预测概率分布'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # 预测置信度分析
        st.markdown("**预测置信度分析**")
        
        max_probs = np.max(probabilities, axis=1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 置信度分布直方图
            fig = px.histogram(
                x=max_probs,
                nbins=30,
                title='最大预测概率分布',
                labels={'x': '最大预测概率', 'y': '频次'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 置信度统计
            confidence_stats = {
                '平均置信度': f"{np.mean(max_probs):.4f}",
                '置信度标准差': f"{np.std(max_probs):.4f}",
                '高置信度样本(>0.9)': f"{np.sum(max_probs > 0.9)}/{len(max_probs)}",
                '低置信度样本(<0.6)': f"{np.sum(max_probs < 0.6)}/{len(max_probs)}"
            }
            
            for key, value in confidence_stats.items():
                st.metric(key, value)
        
        # 置信度vs准确性散点图
        if len(predictions) > 0:
            st.markdown("**置信度与预测准确性关系**")
            
            # 计算每个样本的正确性
            if 'test_labels' in results:
                correct = (predictions == results['test_labels']).astype(int)
                
                fig = px.scatter(
                    x=max_probs,
                    y=correct,
                    title='置信度与预测准确性',
                    labels={'x': '预测置信度', 'y': '预测正确性 (0=错误, 1=正确)'},
                    opacity=0.6
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # 预测统计
        st.markdown("**预测结果统计**")
        
        if len(predictions) > 0:
            # 预测类别分布
            pred_unique, pred_counts = np.unique(predictions, return_counts=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 预测分布饼图
                fig = px.pie(
                    values=pred_counts,
                    names=[f'类别 {i}' for i in pred_unique],
                    title='预测类别分布'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 预测统计表
                pred_df = pd.DataFrame({
                    '预测类别': pred_unique,
                    '预测数量': pred_counts,
                    '预测占比': pred_counts / len(predictions)
                })
                st.dataframe(pred_df, use_container_width=True)

def show_training_efficiency(results, colors):
    """显示训练效率分析"""
    st.markdown("#### ⏱️ 训练效率分析")
    
    if 'training_time' not in results:
        st.warning("⚠️ 没有训练时间数据")
        return
    
    training_time = results['training_time']
    
    # 基础效率指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("训练时间", f"{training_time:.4f} 秒")
    
    with col2:
        if 'test_accuracy' in results:
            efficiency = results['test_accuracy'] / training_time
            st.metric("效率指标", f"{efficiency:.4f} 准确率/秒")
    
    with col3:
        if 'n_samples' in results:
            throughput = results['n_samples'] / training_time
            st.metric("样本处理速度", f"{throughput:.0f} 样本/秒")
    
    with col4:
        if 'n_features' in results:
            feature_efficiency = results['n_features'] / training_time
            st.metric("特征处理速度", f"{feature_efficiency:.0f} 特征/秒")
    
    # 详细效率分析
    if 'cv_scores' in results and 'cv_times' in results:
        st.markdown("**交叉验证效率分析**")
        
        cv_times = results['cv_times']
        cv_scores = results['cv_scores']
        
        # 时间vs性能散点图
        fig = px.scatter(
            x=cv_times,
            y=cv_scores,
            title='训练时间与性能关系',
            labels={'x': '训练时间 (秒)', 'y': '交叉验证得分'},
            trendline='ols'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 效率统计
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**时间统计**")
            time_stats = {
                '平均时间': f"{np.mean(cv_times):.4f} 秒",
                '时间标准差': f"{np.std(cv_times):.4f} 秒",
                '最快训练': f"{np.min(cv_times):.4f} 秒",
                '最慢训练': f"{np.max(cv_times):.4f} 秒"
            }
            
            for key, value in time_stats.items():
                st.text(f"{key}: {value}")
        
        with col2:
            st.markdown("**效率统计**")
            efficiency_scores = cv_scores / cv_times
            eff_stats = {
                '平均效率': f"{np.mean(efficiency_scores):.4f}",
                '效率标准差': f"{np.std(efficiency_scores):.4f}",
                '最高效率': f"{np.max(efficiency_scores):.4f}",
                '最低效率': f"{np.min(efficiency_scores):.4f}"
            }
            
            for key, value in eff_stats.items():
                st.text(f"{key}: {value}")

def show_comprehensive_visualization(model, results, X, y, colors):
    """显示综合可视化分析"""
    st.markdown("#### 🎨 综合可视化分析")
    
    # 创建可视化选项
    col1, col2 = st.columns([2, 1])
    
    with col1:
        viz_options = st.multiselect(
            "选择要显示的可视化",
            ["混淆矩阵", "ROC曲线", "PR曲线", "学习曲线", "特征重要性", "决策边界", "预测分布"],
            default=["混淆矩阵", "ROC曲线"]
        )
    
    with col2:
        show_interactive = st.checkbox("交互式图表", value=True)
        export_format = st.selectbox("导出格式", ["PNG", "SVG", "HTML"])
    
    # 创建可视化布局
    if len(viz_options) > 0:
        # 根据选择的可视化数量调整布局
        if len(viz_options) == 1:
            cols = [1]
        elif len(viz_options) == 2:
            cols = st.columns(2)
        elif len(viz_options) <= 4:
            cols = st.columns(2)
        else:
            cols = st.columns(3)
        
        viz_index = 0
        
        for viz_option in viz_options:
            if len(viz_options) > 1:
                with cols[viz_index % len(cols)]:
                    _show_single_visualization(viz_option, model, results, X, y, colors, show_interactive)
            else:
                _show_single_visualization(viz_option, model, results, X, y, colors, show_interactive)
            
            viz_index += 1
        
        # 导出选项
        if st.button("📥 导出所有可视化"):
            export_visualizations(viz_options, model, results, X, y, colors, export_format)
    else:
        st.info("请选择至少一个可视化选项")

def _show_single_visualization(viz_option, model, results, X, y, colors, interactive=True):
    """显示单个可视化"""
    try:
        if viz_option == "混淆矩阵":
            show_confusion_matrix_analysis(results, colors)
        elif viz_option == "ROC曲线":
            show_roc_analysis(results, colors)
        elif viz_option == "PR曲线":
            show_pr_curve_analysis(results, colors)
        elif viz_option == "学习曲线":
            show_learning_curve_analysis(results, colors)
        elif viz_option == "特征重要性":
            show_feature_importance_analysis(model, X, colors)
        elif viz_option == "决策边界":
            if X.shape[1] == 2:
                from modules.utils import plot_decision_boundary
                st.markdown("**🎯 决策边界**")
                fig = plot_decision_boundary(model, X, y)
                st.pyplot(fig)
            else:
                st.warning("决策边界可视化仅支持2维数据")
        elif viz_option == "预测分布":
            show_prediction_distribution(model, results, X, y)
    except Exception as e:
        st.error(f"生成 {viz_option} 时出错: {str(e)}")

def export_visualizations(viz_options, model, results, X, y, colors, format_type):
    """导出可视化结果"""
    try:
        import zipfile
        import io
        from datetime import datetime
        
        # 创建临时文件
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for viz_option in viz_options:
                # 这里可以添加具体的导出逻辑
                # 由于streamlit的限制，这里只是示例
                filename = f"{viz_option}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type.lower()}"
                zip_file.writestr(filename, f"Visualization: {viz_option}")
        
        zip_buffer.seek(0)
        
        st.download_button(
            label="下载可视化文件",
            data=zip_buffer.getvalue(),
            file_name=f"visualizations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip"
        )
        
        st.success("✅ 可视化文件已准备好下载")
        
    except Exception as e:
        st.error(f"导出失败: {str(e)}")

def set_plot_style(style):
    """设置图表样式"""
    
    if style == "深色":
        plt.style.use('dark_background')
    elif style == "简洁":
        plt.style.use('seaborn-v0_8')
    elif style == "科学":
        plt.style.use('seaborn-v0_8-paper')
    else:
        plt.style.use('default')

def get_color_scheme(scheme):
    """获取配色方案"""
    
    schemes = {
        "默认": {
            "primary": "viridis",
            "secondary": "plasma"
        },
        "蓝色系": {
            "primary": "Blues",
            "secondary": "Blues_r"
        },
        "红色系": {
            "primary": "Reds",
            "secondary": "Reds_r"
        },
        "绿色系": {
            "primary": "Greens",
            "secondary": "Greens_r"
        },
        "彩虹": {
            "primary": "rainbow",
            "secondary": "rainbow"
        }
    }
    
    return schemes.get(scheme, schemes["默认"])

def generate_analysis_report(model, results, X, y):
    """生成分析报告"""
    
    st.markdown("### 📊 生成分析报告")
    
    # 创建报告内容
    report_content = f"""
# 模型分析报告

## 基本信息
- 模型类型: {type(model).__name__}
- 数据集大小: {len(X)} 样本, {X.shape[1]} 特征
- 类别数量: {len(np.unique(y))}
- 训练时间: {results.get('training_time', '未知')}

## 性能指标
- 准确率: {results.get('accuracy', 0):.4f}
- 精确率: {results.get('precision', 0):.4f}
- 召回率: {results.get('recall', 0):.4f}
- F1分数: {results.get('f1', 0):.4f}

## 模型评估
{get_model_evaluation_text(results)}

## 建议
{get_improvement_suggestions(model, results)}

---
报告生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    st.markdown(report_content)
    
    # 提供下载
    st.download_button(
        label="📄 下载报告",
        data=report_content,
        file_name=f"model_analysis_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown"
    )

def get_model_evaluation_text(results):
    """获取模型评估文本"""
    
    accuracy = results.get('accuracy', 0)
    
    if accuracy >= 0.9:
        return "模型性能优秀，在测试集上表现出色。"
    elif accuracy >= 0.8:
        return "模型性能良好，达到了较高的准确率。"
    elif accuracy >= 0.7:
        return "模型性能中等，还有改进空间。"
    else:
        return "模型性能较差，需要进一步优化。"

def get_improvement_suggestions(model, results):
    """获取改进建议"""
    
    suggestions = []
    
    accuracy = results.get('accuracy', 0)
    precision = results.get('precision', 0)
    recall = results.get('recall', 0)
    
    if accuracy < 0.8:
        suggestions.append("考虑尝试其他算法或调整超参数")
    
    if precision < recall:
        suggestions.append("精确率较低，考虑调整分类阈值")
    elif recall < precision:
        suggestions.append("召回率较低，可能需要更多训练数据")
    
    if hasattr(model, 'feature_importances_'):
        suggestions.append("考虑特征选择，移除不重要的特征")
    
    if len(suggestions) == 0:
        suggestions.append("模型性能良好，可以考虑进一步的超参数优化")
    
    return "\n".join([f"- {s}" for s in suggestions])

def show_confusion_matrix_analysis(model, results, X, y):
    """显示混淆矩阵分析"""
    
    if 'confusion_matrix' in results:
        st.markdown("#### 🔍 混淆矩阵")
        show_confusion_matrix(results['confusion_matrix'])

def show_roc_analysis(model, results, X, y):
    """显示ROC曲线分析"""
    
    if 'roc_curve' in results and results['roc_curve']:
        st.markdown("#### 📈 ROC曲线")
        show_roc_curve(results['roc_curve'])

def show_pr_curve_analysis(model, results, X, y):
    """显示PR曲线分析"""
    
    st.markdown("#### 📊 PR曲线")
    st.info("PR曲线分析功能开发中...")

def show_feature_importance_analysis(model, results, X, y):
    """显示特征重要性分析"""
    
    if hasattr(model, 'feature_importances_'):
        st.markdown("#### 🎯 特征重要性")
        show_feature_importance(model, X.shape[1])
    else:
        st.info("当前模型不支持特征重要性分析")

def show_learning_curve_analysis(model, results, X, y):
    """显示学习曲线分析"""
    
    st.markdown("#### 📈 学习曲线")
    show_learning_curves(model, X, y)

def show_class_analysis(model, results, X, y):
    """显示类别分析"""
    
    st.markdown("#### 📊 类别分析")
    unique, counts = np.unique(y, return_counts=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 类别分布饼图
        fig = px.pie(
            values=counts,
            names=[f'类别 {i}' for i in unique],
            title='类别分布'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 类别统计表
        class_df = pd.DataFrame({
            '类别': unique,
            '样本数': counts,
            '占比': counts / len(y)
        })
        st.dataframe(class_df, use_container_width=True)

def show_analysis_summary(model, results, X, y, analysis_types):
    """显示分析总结"""
    
    st.markdown("### 📋 分析总结")
    
    # 生成总结报告
    st.markdown("#### 📊 模型评估总结")
    
    accuracy = results.get('accuracy', 0)
    
    if accuracy >= 0.9:
        performance_level = "🌟 优秀"
        recommendation = "模型性能优秀，可以投入使用"
    elif accuracy >= 0.8:
        performance_level = "👍 良好"
        recommendation = "模型性能良好，可考虑进一步优化"
    elif accuracy >= 0.7:
        performance_level = "👌 一般"
        recommendation = "模型性能中等，建议调整参数或增加数据"
    else:
        performance_level = "⚠️ 需要改进"
        recommendation = "模型性能较差，需要重新设计或选择其他算法"
    
    st.markdown(f"**性能等级**: {performance_level}")
    st.markdown(f"**建议**: {recommendation}")
    
    # 关键指标汇总
    st.markdown("#### 📈 关键指标汇总")
    
    metrics_summary = {
        '指标': ['准确率', '精确率', '召回率', 'F1分数'],
        '数值': [
            f"{results.get('accuracy', 0):.4f}",
            f"{results.get('precision', 0):.4f}",
            f"{results.get('recall', 0):.4f}",
            f"{results.get('f1', 0):.4f}"
        ]
    }
    
    summary_df = pd.DataFrame(metrics_summary)
    st.dataframe(summary_df, use_container_width=True)

def export_charts():
    """导出图表"""
    
    st.success("📈 图表导出功能开发中...")
    st.info("将支持导出PNG、PDF、SVG等格式的图表")