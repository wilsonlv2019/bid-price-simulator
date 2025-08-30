"""工具模块
包含数据可视化、模型评估和其他辅助功能
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
from sklearn.model_selection import learning_curve, validation_curve
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def set_page_style():
    """设置页面样式"""
    
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #f0f8ff, #e6f3ff);
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 1rem 0;
        padding: 0.5rem;
        border-left: 3px solid #3498db;
        background-color: #f8f9fa;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3498db;
        margin: 0.5rem 0;
    }
    
    .algorithm-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .algorithm-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .info-box {
        background-color: #e8f4fd;
        border: 1px solid #bee5eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0px 0px;
        color: #262730;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
    
    .stSelectbox > div > div {
        background-color: white;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """创建指标卡片"""
    
    delta_html = ""
    if delta is not None:
        color = "green" if delta_color == "normal" else "red"
        delta_html = f'<div style="color: {color}; font-size: 0.8rem;">Δ {delta}</div>'
    
    card_html = f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">{title}</div>
        <div style="font-size: 1.8rem; font-weight: bold; color: #2c3e50;">{value}</div>
        {delta_html}
    </div>
    """
    
    return card_html

def plot_confusion_matrix(y_true, y_pred, class_names=None, title="混淆矩阵"):
    """绘制混淆矩阵"""
    
    cm = confusion_matrix(y_true, y_pred)
    
    if class_names is None:
        class_names = [f"类别 {i}" for i in range(len(np.unique(y_true)))]
    
    # 使用plotly创建热力图
    fig = px.imshow(
        cm,
        labels=dict(x="预测类别", y="真实类别", color="样本数量"),
        x=class_names,
        y=class_names,
        color_continuous_scale='Blues',
        text_auto=True,
        title=title
    )
    
    fig.update_layout(
        width=500,
        height=500,
        font=dict(size=12)
    )
    
    return fig

def plot_roc_curves(y_true, y_proba, class_names=None, title="ROC曲线"):
    """绘制ROC曲线"""
    
    n_classes = y_proba.shape[1]
    
    if class_names is None:
        class_names = [f"类别 {i}" for i in range(n_classes)]
    
    fig = go.Figure()
    
    if n_classes == 2:
        # 二分类
        fpr, tpr, _ = roc_curve(y_true, y_proba[:, 1])
        roc_auc = auc(fpr, tpr)
        
        fig.add_trace(go.Scatter(
            x=fpr, y=tpr,
            mode='lines',
            name=f'ROC曲线 (AUC = {roc_auc:.3f})',
            line=dict(color='blue', width=2)
        ))
    else:
        # 多分类
        from sklearn.preprocessing import label_binarize
        
        y_true_bin = label_binarize(y_true, classes=np.unique(y_true))
        
        colors = px.colors.qualitative.Set1
        
        for i in range(n_classes):
            fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_proba[:, i])
            roc_auc = auc(fpr, tpr)
            
            fig.add_trace(go.Scatter(
                x=fpr, y=tpr,
                mode='lines',
                name=f'{class_names[i]} (AUC = {roc_auc:.3f})',
                line=dict(color=colors[i % len(colors)], width=2)
            ))
    
    # 添加对角线
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode='lines',
        name='随机分类器',
        line=dict(color='red', dash='dash', width=1)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='假正率 (FPR)',
        yaxis_title='真正率 (TPR)',
        width=600,
        height=500,
        legend=dict(x=0.6, y=0.1)
    )
    
    return fig

def plot_learning_curves(estimator, X, y, cv=5, title="学习曲线"):
    """绘制学习曲线"""
    
    train_sizes, train_scores, val_scores = learning_curve(
        estimator, X, y, cv=cv, n_jobs=-1,
        train_sizes=np.linspace(0.1, 1.0, 10)
    )
    
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    val_std = np.std(val_scores, axis=1)
    
    fig = go.Figure()
    
    # 训练分数
    fig.add_trace(go.Scatter(
        x=train_sizes, y=train_mean,
        mode='lines+markers',
        name='训练分数',
        line=dict(color='blue'),
        error_y=dict(type='data', array=train_std, visible=True)
    ))
    
    # 验证分数
    fig.add_trace(go.Scatter(
        x=train_sizes, y=val_mean,
        mode='lines+markers',
        name='验证分数',
        line=dict(color='red'),
        error_y=dict(type='data', array=val_std, visible=True)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='训练样本数量',
        yaxis_title='准确率',
        width=700,
        height=500
    )
    
    return fig

def plot_feature_importance(importances, feature_names=None, title="特征重要性"):
    """绘制特征重要性"""
    
    if feature_names is None:
        feature_names = [f'特征_{i+1}' for i in range(len(importances))]
    
    # 创建DataFrame并排序
    df = pd.DataFrame({
        '特征': feature_names,
        '重要性': importances
    }).sort_values('重要性', ascending=True)
    
    fig = px.bar(
        df, x='重要性', y='特征',
        orientation='h',
        title=title,
        color='重要性',
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        width=700,
        height=max(400, len(feature_names) * 25)
    )
    
    return fig

def plot_decision_boundary_2d(model, X, y, feature_names=None, title="决策边界"):
    """绘制2D决策边界"""
    
    if X.shape[1] != 2:
        raise ValueError("此函数仅支持2D数据")
    
    h = 0.02
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))
    
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    
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
            x=X[mask, 0], y=X[mask, 1],
            mode='markers',
            name=f'类别 {class_label}',
            marker=dict(
                color=colors[i % len(colors)],
                size=8,
                line=dict(width=1, color='white')
            )
        ))
    
    if feature_names is None:
        feature_names = ['特征1', '特征2']
    
    fig.update_layout(
        title=title,
        xaxis_title=feature_names[0],
        yaxis_title=feature_names[1],
        width=600,
        height=500
    )
    
    return fig

def plot_data_distribution(X, y, feature_names=None, title="数据分布"):
    """绘制数据分布"""
    
    if feature_names is None:
        feature_names = [f'特征_{i+1}' for i in range(X.shape[1])]
    
    n_features = X.shape[1]
    n_classes = len(np.unique(y))
    
    if n_features == 1:
        # 1D分布
        fig = go.Figure()
        
        colors = px.colors.qualitative.Set1
        for i, class_label in enumerate(np.unique(y)):
            mask = y == class_label
            fig.add_trace(go.Histogram(
                x=X[mask, 0],
                name=f'类别 {class_label}',
                opacity=0.7,
                marker_color=colors[i % len(colors)]
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title=feature_names[0],
            yaxis_title='频数',
            barmode='overlay'
        )
    
    elif n_features == 2:
        # 2D散点图
        df = pd.DataFrame(X, columns=feature_names)
        df['类别'] = y
        
        fig = px.scatter(
            df, x=feature_names[0], y=feature_names[1],
            color='类别', title=title,
            color_discrete_sequence=px.colors.qualitative.Set1
        )
    
    else:
        # 多维数据使用PCA降维
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X)
        
        df = pd.DataFrame(X_pca, columns=['第一主成分', '第二主成分'])
        df['类别'] = y
        
        fig = px.scatter(
            df, x='第一主成分', y='第二主成分',
            color='类别', title=f"{title} (PCA降维)",
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        
        # 添加解释方差比信息
        explained_ratio = pca.explained_variance_ratio_
        fig.add_annotation(
            text=f"解释方差比: PC1={explained_ratio[0]:.3f}, PC2={explained_ratio[1]:.3f}",
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            bgcolor="white",
            bordercolor="black",
            borderwidth=1
        )
    
    fig.update_layout(width=600, height=500)
    return fig

def calculate_metrics(y_true, y_pred, y_proba=None):
    """计算各种评估指标"""
    
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, average='weighted', zero_division=0),
        'recall': recall_score(y_true, y_pred, average='weighted', zero_division=0),
        'f1': f1_score(y_true, y_pred, average='weighted', zero_division=0)
    }
    
    # 如果有概率预测，计算AUC
    if y_proba is not None:
        try:
            n_classes = len(np.unique(y_true))
            if n_classes == 2:
                fpr, tpr, _ = roc_curve(y_true, y_proba[:, 1])
                metrics['auc'] = auc(fpr, tpr)
            else:
                # 多分类AUC (macro average)
                from sklearn.preprocessing import label_binarize
                from sklearn.metrics import roc_auc_score
                
                y_true_bin = label_binarize(y_true, classes=np.unique(y_true))
                metrics['auc'] = roc_auc_score(y_true_bin, y_proba, average='macro')
        except:
            metrics['auc'] = None
    
    return metrics

def format_metrics_table(metrics_dict):
    """格式化指标表格"""
    
    df = pd.DataFrame([
        {'指标': '准确率', '值': f"{metrics_dict['accuracy']:.4f}", '说明': '正确预测的样本比例'},
        {'指标': '精确率', '值': f"{metrics_dict['precision']:.4f}", '说明': '预测为正类中实际为正类的比例'},
        {'指标': '召回率', '值': f"{metrics_dict['recall']:.4f}", '说明': '实际正类中被正确预测的比例'},
        {'指标': 'F1分数', '值': f"{metrics_dict['f1']:.4f}", '说明': '精确率和召回率的调和平均'}
    ])
    
    if 'auc' in metrics_dict and metrics_dict['auc'] is not None:
        df = pd.concat([df, pd.DataFrame([{
            '指标': 'AUC', 
            '值': f"{metrics_dict['auc']:.4f}", 
            '说明': 'ROC曲线下面积'
        }])], ignore_index=True)
    
    return df

def create_comparison_radar_chart(algorithms_metrics, title="算法性能对比"):
    """创建算法对比雷达图"""
    
    metrics = ['accuracy', 'precision', 'recall', 'f1']
    metric_names = ['准确率', '精确率', '召回率', 'F1分数']
    
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set1
    
    for i, (algo_name, algo_metrics) in enumerate(algorithms_metrics.items()):
        values = [algo_metrics.get(metric, 0) for metric in metrics]
        values.append(values[0])  # 闭合雷达图
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=metric_names + [metric_names[0]],
            fill='toself',
            name=algo_name,
            line_color=colors[i % len(colors)]
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        title=title,
        width=600,
        height=500
    )
    
    return fig

def export_results_to_csv(results_dict, filename="model_results.csv"):
    """导出结果到CSV文件"""
    
    try:
        df = pd.DataFrame(results_dict)
        csv = df.to_csv(index=False)
        return csv
    except Exception as e:
        st.error(f"导出CSV时出现错误: {str(e)}")
        return None

def export_results_to_json(results_dict, filename="model_results.json"):
    """导出结果到JSON文件"""
    
    try:
        import json
        
        # 处理numpy数组
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            return obj
        
        # 递归转换字典中的numpy对象
        def clean_dict(d):
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [clean_dict(item) for item in d]
            else:
                return convert_numpy(d)
        
        cleaned_results = clean_dict(results_dict)
        json_str = json.dumps(cleaned_results, indent=2, ensure_ascii=False)
        return json_str
    except Exception as e:
        st.error(f"导出JSON时出现错误: {str(e)}")
        return None

def show_algorithm_info_card(algo_info):
    """显示算法信息卡片"""
    
    card_html = f"""
    <div class="algorithm-card">
        <h3 style="margin: 0 0 1rem 0;">{algo_info['name']}</h3>
        <p style="margin: 0 0 1rem 0; opacity: 0.9;">{algo_info['description'][:100]}...</p>
        <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
            <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">
                类别: {algo_info['category']}
            </span>
            <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">
                复杂度: {algo_info.get('complexity', {}).get('time', 'N/A')}
            </span>
        </div>
    </div>
    """
    
    return card_html

def create_progress_bar(current, total, label="进度"):
    """创建进度条"""
    
    progress = current / total
    
    progress_html = f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="font-weight: 500;">{label}</span>
            <span style="color: #666;">{current}/{total} ({progress*100:.1f}%)</span>
        </div>
        <div style="background-color: #e0e0e0; border-radius: 10px; height: 8px; overflow: hidden;">
            <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; width: {progress*100}%; transition: width 0.3s ease;"></div>
        </div>
    </div>
    """
    
    return progress_html

def validate_data(X, y):
    """验证数据有效性"""
    
    issues = []
    
    # 检查数据类型
    if not isinstance(X, np.ndarray):
        issues.append("特征数据必须是numpy数组")
    
    if not isinstance(y, np.ndarray):
        issues.append("标签数据必须是numpy数组")
    
    if len(issues) > 0:
        return False, issues
    
    # 检查数据形状
    if X.shape[0] != y.shape[0]:
        issues.append("特征和标签的样本数量不匹配")
    
    # 检查缺失值
    if np.isnan(X).any():
        issues.append("特征数据包含缺失值")
    
    if np.isnan(y).any():
        issues.append("标签数据包含缺失值")
    
    # 检查无穷值
    if np.isinf(X).any():
        issues.append("特征数据包含无穷值")
    
    # 检查类别数量
    n_classes = len(np.unique(y))
    if n_classes < 2:
        issues.append("至少需要2个类别")
    
    # 检查样本数量
    if X.shape[0] < 10:
        issues.append("样本数量太少，建议至少10个样本")
    
    return len(issues) == 0, issues

def get_algorithm_recommendations(X, y):
    """根据数据特征推荐算法"""
    
    n_samples, n_features = X.shape
    n_classes = len(np.unique(y))
    
    recommendations = []
    
    # 基于样本数量的推荐
    if n_samples < 1000:
        recommendations.extend([
            "K近邻 - 适合小数据集",
            "朴素贝叶斯 - 计算效率高",
            "决策树 - 易于理解和解释"
        ])
    elif n_samples < 10000:
        recommendations.extend([
            "随机森林 - 平衡性能和稳定性",
            "支持向量机 - 适合中等规模数据",
            "逻辑回归 - 简单有效"
        ])
    else:
        recommendations.extend([
            "XGBoost - 大数据集性能优异",
            "LightGBM - 训练速度快",
            "神经网络 - 处理复杂模式"
        ])
    
    # 基于特征数量的推荐
    if n_features > 100:
        recommendations.append("随机森林 - 处理高维特征")
        recommendations.append("XGBoost - 特征选择能力强")
    
    # 基于类别数量的推荐
    if n_classes == 2:
        recommendations.append("逻辑回归 - 二分类经典算法")
        recommendations.append("支持向量机 - 二分类效果好")
    else:
        recommendations.append("随机森林 - 多分类稳定")
        recommendations.append("梯度提升 - 多分类性能好")
    
    return list(set(recommendations))  # 去重