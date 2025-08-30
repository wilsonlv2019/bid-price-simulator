"""模型训练页面模块
提供模型训练、参数配置和实时训练监控功能
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import joblib
import json
from datetime import datetime

# 机器学习库
from sklearn.model_selection import (
    train_test_split, cross_val_score, GridSearchCV, 
    RandomizedSearchCV, StratifiedKFold, learning_curve
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score, roc_curve
)
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, f_classif

# 算法导入
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier

# 第三方算法
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

from modules.algorithms_config import ALGORITHMS_CONFIG, get_algorithm_info

def show_model_training_page():
    """显示模型训练页面"""
    
    st.markdown('<div class="main-header">🚀 模型训练中心</div>', unsafe_allow_html=True)
    
    # 检查是否有数据
    if 'generated_data' not in st.session_state:
        show_no_data_message()
        return
    
    # 获取数据
    data = st.session_state.generated_data
    if data is None:
        show_no_data_message()
        return
    X, y = data['X'], data['y']
    
    # 侧边栏配置
    with st.sidebar:
        st.markdown("### 🎯 训练配置")
        
        # 算法选择
        algorithm_name = st.selectbox(
            "选择算法",
            list(ALGORITHMS_CONFIG.keys()),
            index=0 if not st.session_state.selected_algorithm else 
                  list(ALGORITHMS_CONFIG.keys()).index(st.session_state.selected_algorithm) 
                  if st.session_state.selected_algorithm in ALGORITHMS_CONFIG else 0
        )
        
        # 更新选中的算法
        st.session_state.selected_algorithm = algorithm_name
        
        # 数据分割配置
        st.markdown("#### 📊 数据分割")
        test_size = st.slider("测试集比例", 0.1, 0.5, 0.2, 0.05)
        random_state = st.number_input("随机种子", 0, 1000, 42)
        
        # 数据预处理
        st.markdown("#### 🔧 数据预处理")
        scale_features = st.checkbox("特征标准化", value=True)
        
        # 特征选择
        use_feature_selection = st.checkbox("特征选择")
        if use_feature_selection:
            n_features = st.slider(
                "选择特征数量", 
                1, min(X.shape[1], 20), 
                min(X.shape[1], 10)
            )
        
        # 验证策略
        st.markdown("#### ✅ 验证策略")
        validation_method = st.selectbox(
            "验证方法",
            ["简单分割", "交叉验证", "分层交叉验证"]
        )
        
        if validation_method != "简单分割":
            cv_folds = st.slider("交叉验证折数", 3, 10, 5)
        else:
            cv_folds = 5
        
        # 超参数优化
        st.markdown("#### ⚙️ 超参数优化")
        optimization_method = st.selectbox(
            "优化方法",
            ["无", "网格搜索", "随机搜索"]
        )
        
        if optimization_method != "无":
            search_iterations = st.slider(
                "搜索迭代次数", 
                10, 100, 20 if optimization_method == "随机搜索" else 50
            )
        
        # 训练按钮
        if st.button("🚀 开始训练", use_container_width=True):
            train_model(algorithm_name, X, y, test_size, random_state, 
                       scale_features, validation_method, cv_folds, optimization_method)
    
    # 主要内容区域
    show_training_interface(algorithm_name, X, y)

def show_no_data_message():
    """显示无数据提示"""
    
    st.markdown("## ⚠️ 没有可用的数据集")
    st.markdown("""
    请先生成或导入数据集才能进行模型训练。
    
    您可以：
    1. 前往 **数据生成** 页面生成模拟数据集
    2. 上传自己的数据集文件
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 前往数据生成", use_container_width=True):
            st.session_state.current_page = 'data_generation'
            st.rerun()
    
    with col2:
        if st.button("📁 上传数据集", use_container_width=True):
            show_data_upload_interface()

def show_data_upload_interface():
    """显示数据上传界面"""
    
    st.markdown("### 📁 上传数据集")
    
    uploaded_file = st.file_uploader(
        "选择CSV文件",
        type=['csv'],
        help="请上传包含特征和目标变量的CSV文件",
        key="dataset_file_uploader"
    )
    
    if uploaded_file is not None:
        try:
            # 读取数据
            df = pd.read_csv(uploaded_file)
            
            st.markdown("#### 📋 数据预览")
            st.dataframe(df.head(), use_container_width=True)
            
            # 选择目标列
            target_column = st.selectbox(
                "选择目标变量列",
                df.columns.tolist()
            )
            
            if st.button("✅ 确认使用此数据集"):
                # 分离特征和目标
                X = df.drop(columns=[target_column]).values
                y = df[target_column].values
                
                # 如果目标变量是字符串，进行编码
                if y.dtype == 'object':
                    le = LabelEncoder()
                    y = le.fit_transform(y)
                
                # 保存到session state
                st.session_state.generated_data = {
                    'X': X,
                    'y': y,
                    'dataset_type': '用户上传数据',
                    'n_samples': len(X),
                    'n_features': X.shape[1],
                    'n_classes': len(np.unique(y)),
                    'random_state': 42,
                    'noise_level': 0.0
                }
                
                st.success("✅ 数据集上传成功！")
                st.rerun()
                
        except Exception as e:
            st.error(f"数据读取失败: {str(e)}")

def show_training_interface(algorithm_name, X, y):
    """显示训练界面"""
    
    # 算法信息
    algo_info = get_algorithm_info(algorithm_name)
    
    st.markdown(f"## 🔬 {algo_info['name']} 训练")
    
    # 数据集信息
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("样本数量", len(X))
    
    with col2:
        st.metric("特征数量", X.shape[1])
    
    with col3:
        st.metric("类别数量", len(np.unique(y)))
    
    with col4:
        balance_ratio = np.bincount(y).max() / np.bincount(y).min()
        st.metric("平衡比例", f"{balance_ratio:.2f}")
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["⚙️ 参数配置", "📊 训练监控", "📈 结果分析", "💾 模型管理"])
    
    with tab1:
        show_parameter_configuration(algorithm_name, algo_info)
    
    with tab2:
        show_training_monitoring()
    
    with tab3:
        show_training_results()
    
    with tab4:
        show_model_management()

def show_parameter_configuration(algorithm_name, algo_info):
    """显示参数配置界面"""
    
    st.markdown("### ⚙️ 算法参数配置")
    
    # 获取默认参数
    default_params = algo_info.get('default_params', {})
    param_descriptions = algo_info.get('param_descriptions', {})
    
    if not default_params:
        st.warning("该算法暂无可配置参数")
        return
    
    # 创建参数配置界面
    configured_params = {}
    
    st.markdown("#### 📋 主要参数")
    
    # 根据算法类型创建不同的参数配置界面
    if algorithm_name == 'logistic_regression':
        configured_params = configure_logistic_regression_params(default_params)
    elif algorithm_name == 'decision_tree':
        configured_params = configure_decision_tree_params(default_params)
    elif algorithm_name == 'random_forest':
        configured_params = configure_random_forest_params(default_params)
    elif algorithm_name == 'svm':
        configured_params = configure_svm_params(default_params)
    elif algorithm_name == 'knn':
        configured_params = configure_knn_params(default_params)
    elif algorithm_name == 'naive_bayes':
        configured_params = configure_naive_bayes_params(default_params)
    elif algorithm_name == 'gradient_boosting':
        configured_params = configure_gradient_boosting_params(default_params)
    elif algorithm_name == 'xgboost':
        configured_params = configure_xgboost_params(default_params)
    elif algorithm_name == 'neural_network':
        configured_params = configure_neural_network_params(default_params)
    elif algorithm_name == 'lightgbm':
        configured_params = configure_lightgbm_params(default_params)
    else:
        # 通用参数配置
        configured_params = configure_generic_params(default_params, param_descriptions)
    
    # 保存配置的参数
    st.session_state[f'{algorithm_name}_params'] = configured_params
    
    # 参数预设
    st.markdown("#### 🎯 参数预设")
    
    preset_options = ["自定义", "快速训练", "高精度", "平衡性能"]
    selected_preset = st.selectbox("选择参数预设", preset_options)
    
    if selected_preset != "自定义":
        if st.button(f"应用 {selected_preset} 预设"):
            preset_params = get_parameter_preset(algorithm_name, selected_preset)
            st.session_state[f'{algorithm_name}_params'] = preset_params
            st.success(f"已应用 {selected_preset} 参数预设")
            st.rerun()

def configure_logistic_regression_params(default_params):
    """配置逻辑回归参数"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        C = st.slider("正则化强度 (C)", 0.01, 10.0, 
                     default_params.get('C', 1.0), 0.01,
                     help="较小的值表示更强的正则化")
        
        max_iter = st.slider("最大迭代次数", 100, 2000, 
                           default_params.get('max_iter', 1000), 100)
    
    with col2:
        solver = st.selectbox("求解器", 
                            ['liblinear', 'lbfgs', 'newton-cg', 'sag', 'saga'],
                            index=0)
        
        penalty = st.selectbox("正则化类型", ['l1', 'l2', 'elasticnet', 'none'],
                             index=1)
    
    return {
        'C': C,
        'max_iter': max_iter,
        'solver': solver,
        'penalty': penalty,
        'random_state': 42
    }

def configure_decision_tree_params(default_params):
    """配置决策树参数"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_depth = st.slider("最大深度", 1, 20, 
                            default_params.get('max_depth', 5))
        
        min_samples_split = st.slider("最小分割样本数", 2, 20, 
                                    default_params.get('min_samples_split', 2))
    
    with col2:
        min_samples_leaf = st.slider("最小叶节点样本数", 1, 10, 
                                   default_params.get('min_samples_leaf', 1))
        
        criterion = st.selectbox("分割标准", ['gini', 'entropy'],
                               index=0)
    
    return {
        'max_depth': max_depth,
        'min_samples_split': min_samples_split,
        'min_samples_leaf': min_samples_leaf,
        'criterion': criterion,
        'random_state': 42
    }

def configure_random_forest_params(default_params):
    """配置随机森林参数"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        n_estimators = st.slider("树的数量", 10, 200, 
                               default_params.get('n_estimators', 100), 10)
        
        max_depth = st.slider("最大深度", 1, 20, 
                            default_params.get('max_depth', 10))
    
    with col2:
        min_samples_split = st.slider("最小分割样本数", 2, 20, 
                                    default_params.get('min_samples_split', 2))
        
        max_features = st.selectbox("最大特征数", ['sqrt', 'log2', 'auto', None],
                                  index=0)
    
    return {
        'n_estimators': n_estimators,
        'max_depth': max_depth,
        'min_samples_split': min_samples_split,
        'max_features': max_features,
        'random_state': 42
    }

def configure_svm_params(default_params):
    """配置SVM参数"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        C = st.slider("正则化参数 (C)", 0.01, 10.0, 
                     default_params.get('C', 1.0), 0.01)
        
        kernel = st.selectbox("核函数", ['rbf', 'linear', 'poly', 'sigmoid'],
                            index=0)
    
    with col2:
        if kernel == 'rbf':
            gamma = st.selectbox("Gamma", ['scale', 'auto'], index=0)
        else:
            gamma = 'scale'
        
        degree = st.slider("多项式度数", 2, 5, 3) if kernel == 'poly' else 3
    
    return {
        'C': C,
        'kernel': kernel,
        'gamma': gamma,
        'degree': degree,
        'random_state': 42
    }

def configure_knn_params(default_params):
    """配置KNN参数"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        n_neighbors = st.slider("邻居数量 (K)", 1, 20, 
                              default_params.get('n_neighbors', 5))
        
        weights = st.selectbox("权重方式", ['uniform', 'distance'],
                             index=0)
    
    with col2:
        algorithm = st.selectbox("算法", ['auto', 'ball_tree', 'kd_tree', 'brute'],
                               index=0)
        
        metric = st.selectbox("距离度量", ['euclidean', 'manhattan', 'minkowski'],
                            index=0)
    
    return {
        'n_neighbors': n_neighbors,
        'weights': weights,
        'algorithm': algorithm,
        'metric': metric
    }

def configure_naive_bayes_params(default_params):
    """配置朴素贝叶斯参数"""
    
    st.markdown("朴素贝叶斯算法使用默认参数，无需额外配置。")
    
    var_smoothing = st.slider("方差平滑参数", 1e-10, 1e-8, 1e-9, 1e-10,
                            help="用于稳定计算的平滑参数")
    
    return {
        'var_smoothing': var_smoothing
    }

def configure_gradient_boosting_params(default_params):
    """配置梯度提升参数"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        n_estimators = st.slider("提升轮数", 50, 300, 
                               default_params.get('n_estimators', 100), 10)
        
        learning_rate = st.slider("学习率", 0.01, 0.3, 
                                default_params.get('learning_rate', 0.1), 0.01)
    
    with col2:
        max_depth = st.slider("最大深度", 1, 10, 
                            default_params.get('max_depth', 3))
        
        subsample = st.slider("子样本比例", 0.5, 1.0, 
                            default_params.get('subsample', 1.0), 0.05)
    
    return {
        'n_estimators': n_estimators,
        'learning_rate': learning_rate,
        'max_depth': max_depth,
        'subsample': subsample,
        'random_state': 42
    }

def configure_xgboost_params(default_params):
    """配置XGBoost参数"""
    
    if not XGBOOST_AVAILABLE:
        st.error("XGBoost未安装，请先安装: pip install xgboost")
        return default_params
    
    col1, col2 = st.columns(2)
    
    with col1:
        n_estimators = st.slider("提升轮数", 50, 300, 
                               default_params.get('n_estimators', 100), 10)
        
        learning_rate = st.slider("学习率", 0.01, 0.3, 
                                default_params.get('learning_rate', 0.1), 0.01)
    
    with col2:
        max_depth = st.slider("最大深度", 1, 10, 
                            default_params.get('max_depth', 6))
        
        subsample = st.slider("子样本比例", 0.5, 1.0, 
                            default_params.get('subsample', 1.0), 0.05)
    
    return {
        'n_estimators': n_estimators,
        'learning_rate': learning_rate,
        'max_depth': max_depth,
        'subsample': subsample,
        'random_state': 42
    }

def configure_neural_network_params(default_params):
    """配置神经网络参数"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 隐藏层配置
        n_layers = st.slider("隐藏层数量", 1, 3, 1)
        
        hidden_layer_sizes = []
        for i in range(n_layers):
            size = st.slider(f"第{i+1}层神经元数量", 10, 200, 100, 10)
            hidden_layer_sizes.append(size)
        
        hidden_layer_sizes = tuple(hidden_layer_sizes)
    
    with col2:
        learning_rate_init = st.slider("初始学习率", 0.0001, 0.01, 0.001, 0.0001)
        
        max_iter = st.slider("最大迭代次数", 100, 1000, 200, 50)
        
        activation = st.selectbox("激活函数", ['relu', 'tanh', 'logistic'],
                                index=0)
    
    return {
        'hidden_layer_sizes': hidden_layer_sizes,
        'learning_rate_init': learning_rate_init,
        'max_iter': max_iter,
        'activation': activation,
        'random_state': 42
    }

def configure_lightgbm_params(default_params):
    """配置LightGBM参数"""
    
    if not LIGHTGBM_AVAILABLE:
        st.error("LightGBM未安装，请先安装: pip install lightgbm")
        return default_params
    
    col1, col2 = st.columns(2)
    
    with col1:
        n_estimators = st.slider("提升轮数", 50, 300, 
                               default_params.get('n_estimators', 100), 10)
        
        learning_rate = st.slider("学习率", 0.01, 0.3, 
                                default_params.get('learning_rate', 0.1), 0.01)
    
    with col2:
        max_depth = st.slider("最大深度", 1, 10, 
                            default_params.get('max_depth', -1))
        
        num_leaves = st.slider("叶子节点数", 10, 100, 
                             default_params.get('num_leaves', 31), 5)
    
    return {
        'n_estimators': n_estimators,
        'learning_rate': learning_rate,
        'max_depth': max_depth,
        'num_leaves': num_leaves,
        'random_state': 42
    }

def configure_generic_params(default_params, param_descriptions):
    """通用参数配置"""
    
    configured_params = {}
    
    for param_name, default_value in default_params.items():
        description = param_descriptions.get(param_name, '')
        
        if isinstance(default_value, bool):
            configured_params[param_name] = st.checkbox(
                param_name, value=default_value, help=description
            )
        elif isinstance(default_value, int):
            configured_params[param_name] = st.number_input(
                param_name, value=default_value, help=description
            )
        elif isinstance(default_value, float):
            configured_params[param_name] = st.number_input(
                param_name, value=default_value, format="%.4f", help=description
            )
        elif isinstance(default_value, str):
            configured_params[param_name] = st.text_input(
                param_name, value=default_value, help=description
            )
        else:
            configured_params[param_name] = default_value
    
    return configured_params

def get_parameter_preset(algorithm_name, preset_type):
    """获取参数预设"""
    
    presets = {
        'logistic_regression': {
            '快速训练': {'C': 1.0, 'max_iter': 100, 'solver': 'liblinear'},
            '高精度': {'C': 0.1, 'max_iter': 1000, 'solver': 'lbfgs'},
            '平衡性能': {'C': 1.0, 'max_iter': 500, 'solver': 'lbfgs'}
        },
        'random_forest': {
            '快速训练': {'n_estimators': 50, 'max_depth': 5},
            '高精度': {'n_estimators': 200, 'max_depth': 15},
            '平衡性能': {'n_estimators': 100, 'max_depth': 10}
        }
        # 可以为其他算法添加更多预设
    }
    
    return presets.get(algorithm_name, {}).get(preset_type, {})

def show_training_monitoring():
    """显示训练监控"""
    
    st.markdown("### 📊 训练进度监控")
    
    if 'training_history' not in st.session_state:
        st.info("暂无训练历史记录")
        return
    
    history = st.session_state.training_history
    
    # 训练进度
    if 'progress' in history:
        st.progress(history['progress'])
        st.markdown(f"**当前状态：** {history.get('status', '未知')}")
    
    # 训练指标图表
    if 'metrics' in history:
        metrics = history['metrics']
        
        # 创建指标图表
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['准确率', '损失', '训练时间', '内存使用'],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 添加指标曲线
        if 'accuracy' in metrics:
            fig.add_trace(
                go.Scatter(y=metrics['accuracy'], name='准确率'),
                row=1, col=1
            )
        
        if 'loss' in metrics:
            fig.add_trace(
                go.Scatter(y=metrics['loss'], name='损失'),
                row=1, col=2
            )
        
        fig.update_layout(height=400, title="训练指标监控")
        st.plotly_chart(fig, use_container_width=True)

def show_training_results():
    """显示训练结果"""
    
    st.markdown("### 📈 训练结果分析")
    
    if 'trained_model' not in st.session_state:
        st.info("请先训练模型")
        return
    
    results = st.session_state.training_results
    
    # 性能指标
    st.markdown("#### 📊 性能指标")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("准确率", f"{results['accuracy']:.4f}")
    
    with col2:
        st.metric("精确率", f"{results['precision']:.4f}")
    
    with col3:
        st.metric("召回率", f"{results['recall']:.4f}")
    
    with col4:
        st.metric("F1分数", f"{results['f1']:.4f}")
    
    # 标签页组织结果
    tab1, tab2, tab3, tab4 = st.tabs(["📈 性能分析", "🔍 详细结果", "📊 可视化", "💾 模型管理"])
    
    with tab1:
        # 交叉验证结果
        if 'cv_scores' in results and results['cv_scores'] is not None:
            st.markdown("#### ✅ 交叉验证结果")
            cv_scores = results['cv_scores']
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("平均分数", f"{cv_mean:.4f}")
            with col2:
                st.metric("标准差", f"{cv_std:.4f}")
            with col3:
                st.metric("置信区间", f"±{cv_std*2:.4f}")
            
            # 交叉验证分数图表
            cv_df = pd.DataFrame({
                '折数': range(1, len(cv_scores) + 1),
                '准确率': cv_scores
            })
            
            fig = px.bar(
                cv_df, x='折数', y='准确率',
                title="交叉验证结果",
                text='准确率'
            )
            fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        
        # 训练时间信息
        if 'training_time' in results:
            st.markdown("#### ⏱️ 训练信息")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("训练时间", f"{results['training_time']:.2f}秒")
            with col2:
                if 'test_predictions' in results:
                    st.metric("测试样本数", len(results['test_predictions']))
    
    with tab2:
        # 混淆矩阵
        if 'confusion_matrix' in results:
            st.markdown("#### 🔍 混淆矩阵")
            
            cm = results['confusion_matrix']
            fig = px.imshow(
                cm,
                title="混淆矩阵",
                color_continuous_scale="Blues",
                aspect="auto",
                text_auto=True
            )
            fig.update_layout(
                xaxis_title="预测标签",
                yaxis_title="真实标签"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 分类报告
        if 'test_predictions' in results:
            st.markdown("#### 📋 详细分类报告")
            try:
                # 这里需要从session state获取测试数据
                if 'y_test' in st.session_state and 'y_pred' in st.session_state:
                    y_test = st.session_state.y_test
                    y_pred = st.session_state.y_pred
                    
                    report = classification_report(y_test, y_pred, output_dict=True)
                    report_df = pd.DataFrame(report).transpose()
                    st.dataframe(report_df, use_container_width=True)
            except Exception as e:
                st.warning("无法生成详细分类报告")
        
        # 预测概率分布
        if 'test_probabilities' in results and results['test_probabilities'] is not None:
            st.markdown("#### 📊 预测概率分布")
            proba = results['test_probabilities']
            
            proba_df = pd.DataFrame(
                proba,
                columns=[f'类别 {i}' for i in range(proba.shape[1])]
            )
            
            fig = px.box(
                proba_df.melt(var_name='类别', value_name='概率'),
                x='类别', y='概率',
                title="各类别预测概率分布"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # ROC曲线
        if 'roc_curve' in results and results['roc_curve'] is not None:
            st.markdown("#### 📈 ROC曲线")
            
            fpr, tpr, auc_score = results['roc_curve']
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=fpr, y=tpr,
                name=f'ROC曲线 (AUC = {auc_score:.3f})',
                line=dict(color='blue', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1],
                name='随机分类器',
                line=dict(color='red', width=1, dash='dash')
            ))
            
            fig.update_layout(
                title='ROC曲线',
                xaxis_title='假正率 (FPR)',
                yaxis_title='真正率 (TPR)',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 特征重要性（如果模型支持）
        model = st.session_state.trained_model
        if hasattr(model, 'feature_importances_'):
            st.markdown("#### 🎯 特征重要性")
            
            importances = model.feature_importances_
            feature_names = [f'特征 {i+1}' for i in range(len(importances))]
            
            importance_df = pd.DataFrame({
                '特征': feature_names,
                '重要性': importances
            }).sort_values('重要性', ascending=True)
            
            fig = px.bar(
                importance_df, x='重要性', y='特征',
                orientation='h',
                title="特征重要性排序"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 学习曲线（如果有数据）
        if 'learning_curve_data' in st.session_state:
            st.markdown("#### 📈 学习曲线")
            curve_data = st.session_state.learning_curve_data
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=curve_data['train_sizes'],
                y=curve_data['train_scores_mean'],
                name='训练分数',
                line=dict(color='blue')
            ))
            
            fig.add_trace(go.Scatter(
                x=curve_data['train_sizes'],
                y=curve_data['val_scores_mean'],
                name='验证分数',
                line=dict(color='red')
            ))
            
            fig.update_layout(
                title='学习曲线',
                xaxis_title='训练样本数',
                yaxis_title='分数',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        show_model_management()
        
        # 模型操作
        if 'trained_model' in st.session_state:
            st.divider()
            st.markdown("**当前训练的模型操作**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                model_name = st.text_input(
                    "模型名称",
                    value=f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    help="为模型指定一个名称"
                )
                
                if st.button("💾 保存当前模型", use_container_width=True):
                    save_model_to_file(st.session_state.trained_model, model_name)
            
            with col2:
                if st.button("📤 导出训练结果", use_container_width=True):
                    if 'training_results' in st.session_state:
                        export_results(
                            st.session_state.training_results,
                            st.session_state.get('algorithm_name', 'unknown')
                        )
                    else:
                        st.warning("⚠️ 没有可导出的训练结果")
        else:
            st.info("📝 请先训练一个模型以进行保存和导出操作")

def show_model_management():
    """显示模型管理"""
    
    st.markdown("### 💾 模型管理")
    
    if 'trained_model' not in st.session_state:
        st.info("暂无已训练的模型")
        return
    
    model = st.session_state.trained_model
    
    # 模型信息
    st.markdown("#### ℹ️ 模型信息")
    
    model_info = {
        "算法类型": type(model).__name__,
        "训练时间": st.session_state.get('training_time', '未知'),
        "数据集大小": st.session_state.get('dataset_size', '未知'),
        "特征数量": st.session_state.get('n_features', '未知')
    }
    
    for key, value in model_info.items():
        st.markdown(f"**{key}：** {value}")
    
    # 模型保存
    st.markdown("#### 💾 模型保存")
    
    model_name = st.text_input("模型名称", value=f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
            if st.button("💾 保存模型", use_container_width=True):
                save_model_to_file(model, model_name)
    
    with col2:
        if st.button("📤 导出模型", use_container_width=True):
            export_model(model, model_name)
    
    # 模型加载
    st.markdown("#### 📁 模型加载")
    
    uploaded_model = st.file_uploader(
        "上传模型文件",
        type=['pkl', 'joblib'],
        help="上传之前保存的模型文件",
        key="training_model_uploader"
    )
    
    if uploaded_model is not None:
        if st.button("📁 加载模型"):
            load_model(uploaded_model)

def train_model(algorithm_name, X, y, test_size, random_state, 
               scale_features, validation_method, cv_folds, optimization_method):
    """训练模型"""
    
    # 初始化训练历史
    st.session_state.training_history = {
        'progress': 0,
        'status': '开始训练...',
        'metrics': {}
    }
    
    try:
        # 数据分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # 特征标准化
        if scale_features:
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)
            st.session_state.scaler = scaler
        
        # 更新进度
        st.session_state.training_history['progress'] = 0.2
        st.session_state.training_history['status'] = '准备模型...'
        
        # 创建模型
        model = create_model(algorithm_name)
        
        if model is None:
            st.error(f"无法创建 {algorithm_name} 模型")
            return
        
        # 更新进度
        st.session_state.training_history['progress'] = 0.4
        st.session_state.training_history['status'] = '训练中...'
        
        start_time = time.time()
        
        # 超参数优化
        if optimization_method != "无":
            param_grid = get_param_grid(algorithm_name)
            if param_grid:
                if optimization_method == "网格搜索":
                    search = GridSearchCV(
                        model, param_grid, cv=cv_folds, scoring='accuracy', n_jobs=-1
                    )
                else:  # 随机搜索
                    search_iterations = st.session_state.get('search_iterations', 20)
                    search = RandomizedSearchCV(
                        model, param_grid, n_iter=search_iterations,
                        cv=cv_folds, scoring='accuracy', n_jobs=-1, random_state=random_state
                    )
                
                search.fit(X_train, y_train)
                model = search.best_estimator_
                st.success(f"最佳参数: {search.best_params_}")
        else:
            # 应用配置的参数
            configured_params = st.session_state.get(f'{algorithm_name}_params', {})
            if configured_params:
                model.set_params(**configured_params)
            
            model.fit(X_train, y_train)
        
        training_time = time.time() - start_time
        
        # 更新进度
        st.session_state.training_history['progress'] = 0.8
        st.session_state.training_history['status'] = '评估模型...'
        
        # 预测
        y_pred = model.predict(X_test)
        y_pred_proba = None
        
        if hasattr(model, 'predict_proba'):
            y_pred_proba = model.predict_proba(X_test)
        
        # 计算指标
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        # 混淆矩阵
        cm = confusion_matrix(y_test, y_pred)
        
        # ROC曲线（仅适用于二分类）
        roc_data = None
        if len(np.unique(y)) == 2 and y_pred_proba is not None:
            fpr, tpr, _ = roc_curve(y_test, y_pred_proba[:, 1])
            auc_score = roc_auc_score(y_test, y_pred_proba[:, 1])
            roc_data = (fpr, tpr, auc_score)
        
        # 交叉验证
        cv_scores = None
        if validation_method != "简单分割":
            if validation_method == "分层交叉验证":
                cv_strategy = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
            else:
                cv_strategy = cv_folds
            cv_scores = cross_val_score(model, X_train, y_train, cv=cv_strategy)
        
        # 保存结果
        st.session_state.trained_model = model
        st.session_state.training_results = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'confusion_matrix': cm,
            'roc_curve': roc_data,
            'cv_scores': cv_scores,
            'training_time': training_time,
            'test_predictions': y_pred,
            'test_probabilities': y_pred_proba
        }
        
        st.session_state.training_time = f"{training_time:.2f}秒"
        st.session_state.dataset_size = len(X)
        st.session_state.n_features = X.shape[1]
        
        # 完成训练
        st.session_state.training_history['progress'] = 1.0
        st.session_state.training_history['status'] = '训练完成！'
        
        st.success(f"✅ 模型训练完成！准确率: {accuracy:.4f}")
        
        if cv_scores is not None:
            st.info(f"交叉验证平均分数: {cv_scores.mean():.4f} (±{cv_scores.std()*2:.4f})")
        
    except Exception as e:
        st.error(f"训练失败: {str(e)}")
        st.session_state.training_history['status'] = f'训练失败: {str(e)}'

def create_model(algorithm_name):
    """创建模型实例"""
    
    models = {
        'logistic_regression': LogisticRegression(),
        'decision_tree': DecisionTreeClassifier(),
        'random_forest': RandomForestClassifier(),
        'svm': SVC(probability=True),
        'knn': KNeighborsClassifier(),
        'naive_bayes': GaussianNB(),
        'gradient_boosting': GradientBoostingClassifier(),
        'neural_network': MLPClassifier()
    }
    
    # XGBoost
    if algorithm_name == 'xgboost' and XGBOOST_AVAILABLE:
        models['xgboost'] = xgb.XGBClassifier()
    
    # LightGBM
    if algorithm_name == 'lightgbm' and LIGHTGBM_AVAILABLE:
        models['lightgbm'] = lgb.LGBMClassifier()
    
    return models.get(algorithm_name)

def get_param_grid(algorithm_name):
    """获取网格搜索参数"""
    
    param_grids = {
        'logistic_regression': {
            'C': [0.01, 0.1, 1, 10, 100],
            'penalty': ['l1', 'l2'],
            'solver': ['liblinear', 'saga']
        },
        'decision_tree': {
            'max_depth': [3, 5, 7, 10, None],
            'min_samples_split': [2, 5, 10, 20],
            'min_samples_leaf': [1, 2, 4],
            'criterion': ['gini', 'entropy']
        },
        'random_forest': {
            'n_estimators': [50, 100, 200, 300],
            'max_depth': [3, 5, 7, 10, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        },
        'svm': {
            'C': [0.1, 1, 10, 100],
            'kernel': ['linear', 'rbf', 'poly'],
            'gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1]
        },
        'knn': {
            'n_neighbors': [3, 5, 7, 9, 11, 15],
            'weights': ['uniform', 'distance'],
            'metric': ['euclidean', 'manhattan', 'minkowski']
        },
        'naive_bayes': {
            'var_smoothing': [1e-10, 1e-9, 1e-8, 1e-7]
        },
        'gradient_boosting': {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7]
        },
        'xgboost': {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7],
            'subsample': [0.8, 0.9, 1.0]
        },
        'neural_network': {
            'hidden_layer_sizes': [(50,), (100,), (50, 50), (100, 50)],
            'alpha': [0.0001, 0.001, 0.01],
            'learning_rate': ['constant', 'adaptive']
        },
        'lightgbm': {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7],
            'num_leaves': [31, 50, 100]
        }
    }
    
    return param_grids.get(algorithm_name, {})

def save_model_to_file(model, model_name):
    """保存模型到文件"""
    try:
        filename = f"model_{model_name}_{int(time.time())}.joblib"
        joblib.dump(model, filename)
        st.success(f"✅ 模型已保存为: {filename}")
        
        # 保存模型元数据
        metadata = {
            'model_name': model_name,
            'algorithm': st.session_state.get('algorithm_name', 'Unknown'),
            'save_time': datetime.now().isoformat(),
            'metrics': st.session_state.get('training_metrics', {}),
            'training_time': st.session_state.get('training_time', 0)
        }
        
        metadata_filename = f"{model_name}_metadata.json"
        with open(metadata_filename, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        st.info(f"📋 模型元数据已保存为: {metadata_filename}")
        return filename
        
    except Exception as e:
        st.error(f"❌ 保存模型失败: {str(e)}")
        return None

def export_results(results, algorithm_name):
    """导出训练结果"""
    try:
        filename = f"results_{algorithm_name}_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            # 转换numpy数组为列表以便JSON序列化
            export_data = {}
            for key, value in results.items():
                if isinstance(value, np.ndarray):
                    export_data[key] = value.tolist()
                else:
                    export_data[key] = value
            
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        st.success(f"✅ 结果已导出为: {filename}")
        return filename
    except Exception as e:
        st.error(f"❌ 导出结果失败: {str(e)}")
        return None

def export_model(model, model_name):
    """导出模型和相关信息"""
    try:
        # 创建导出包
        export_data = {
            'model_name': model_name,
            'algorithm': st.session_state.get('algorithm_name', 'Unknown'),
            'export_time': datetime.now().isoformat(),
            'metrics': st.session_state.get('training_metrics', {}),
            'training_time': st.session_state.get('training_time', 0),
            'best_params': st.session_state.get('best_params', {}),
            'cv_scores': st.session_state.get('cv_scores', []).tolist() if st.session_state.get('cv_scores') is not None else None,
            'model_info': {
                'type': type(model).__name__,
                'parameters': model.get_params() if hasattr(model, 'get_params') else {}
            }
        }
        
        # 保存为JSON
        export_filename = f"{model_name}_export.json"
        with open(export_filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        st.success(f"📤 模型信息已导出为: {export_filename}")
        
        # 同时保存模型文件
        save_model_to_file(model, model_name)
        
    except Exception as e:
        st.error(f"❌ 导出模型失败: {str(e)}")

def load_saved_model(filename):
    """加载保存的模型"""
    try:
        model = joblib.load(filename)
        st.success(f"✅ 模型已从 {filename} 加载")
        return model
    except Exception as e:
        st.error(f"❌ 加载模型失败: {str(e)}")
        return None

def show_model_management():
    """显示模型管理页面"""
    st.subheader("📁 模型管理")
    
    # 模型加载
    st.markdown("**加载已保存的模型**")
    uploaded_file = st.file_uploader(
        "选择模型文件", 
        type=['joblib'],
        help="上传之前保存的.joblib模型文件",
        key="model_file_uploader"
    )
    
    if uploaded_file is not None:
        try:
            model = joblib.load(uploaded_file)
            st.session_state.loaded_model = model
            st.success(f"✅ 模型 {uploaded_file.name} 加载成功！")
            
            # 显示模型信息
            st.markdown("**模型信息**")
            model_info = {
                "模型类型": type(model).__name__,
                "参数数量": len(model.get_params()) if hasattr(model, 'get_params') else "未知"
            }
            
            for key, value in model_info.items():
                st.markdown(f"- **{key}**: {value}")
                
        except Exception as e:
            st.error(f"❌ 加载模型失败: {str(e)}")
    
    # 显示已保存的模型列表
    st.markdown("**本地模型文件**")
    import glob
    model_files = glob.glob("*.joblib")
    
    if model_files:
        selected_model = st.selectbox(
            "选择本地模型文件",
            model_files
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 加载选中模型"):
                model = load_saved_model(selected_model)
                if model:
                    st.session_state.loaded_model = model
        
        with col2:
            if st.button("🗑️ 删除选中模型"):
                try:
                    import os
                    os.remove(selected_model)
                    st.success(f"✅ 已删除模型: {selected_model}")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ 删除失败: {str(e)}")
    else:
        st.info("📝 暂无本地模型文件")

def export_model(model, model_name):
    """导出模型"""
    
    try:
        # 使用joblib序列化模型
        import io
        
        buffer = io.BytesIO()
        joblib.dump(model, buffer)
        buffer.seek(0)
        
        st.download_button(
            label="📤 下载模型文件",
            data=buffer.getvalue(),
            file_name=f"{model_name}.pkl",
            mime="application/octet-stream"
        )
        
    except Exception as e:
        st.error(f"模型导出失败: {str(e)}")

def load_model(uploaded_file):
    """加载模型"""
    
    try:
        model = joblib.load(uploaded_file)
        st.session_state.trained_model = model
        st.success("✅ 模型加载成功！")
        
    except Exception as e:
        st.error(f"模型加载失败: {str(e)}")