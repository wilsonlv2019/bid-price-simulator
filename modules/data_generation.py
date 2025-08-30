"""数据生成页面模块
生成各种类型的模拟数据集用于算法训练和测试
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.datasets import (
    make_classification, make_blobs, make_circles, make_moons,
    make_gaussian_quantiles, make_multilabel_classification, make_hastie_10_2
)
from sklearn.preprocessing import StandardScaler
import seaborn as sns

def show_data_generation_page():
    """显示数据生成页面"""
    
    st.markdown('<div class="main-header">🎲 数据生成中心</div>', unsafe_allow_html=True)
    
    # 侧边栏配置
    with st.sidebar:
        st.markdown("### 📊 数据集配置")
        
        # 数据集类型选择
        dataset_type = st.selectbox(
            "选择数据集类型",
            [
                "线性可分数据",
                "非线性数据",
                "聚类数据",
                "环形数据",
                "月牙形数据",
                "高斯分布数据",
                "不平衡数据",
                "多标签数据",
                "噪声数据",
                "Hastie数据",
                "自定义数据"
            ]
        )
        
        # 基本参数
        st.markdown("#### 基本参数")
        n_samples = st.slider("样本数量", 100, 2000, 500, 50)
        n_features = st.slider("特征数量", 2, 10, 2)
        n_classes = st.slider("类别数量", 2, 5, 2)
        
        # 高级参数
        st.markdown("#### 高级参数")
        random_state = st.number_input("随机种子", 0, 1000, 42)
        noise_level = st.slider("噪声水平", 0.0, 1.0, 0.1, 0.05)
        
        # 生成数据按钮
        if st.button("🎲 生成数据集", use_container_width=True):
            generate_dataset(dataset_type, n_samples, n_features, n_classes, random_state, noise_level)
    
    # 主要内容区域
    if 'generated_data' not in st.session_state:
        show_data_generation_intro()
    else:
        show_generated_data_analysis()

def show_data_generation_intro():
    """显示数据生成介绍"""
    
    st.markdown("## 🎯 数据生成工具")
    st.markdown("""
    这个工具可以帮助您生成各种类型的模拟数据集，用于测试和学习不同的机器学习算法。
    每种数据集类型都有其特定的特征和适用场景。
    """)
    
    # 数据集类型介绍
    st.markdown("### 📋 数据集类型说明")
    
    dataset_info = {
        "线性可分数据": {
            "description": "类别之间可以用直线完全分开的数据",
            "suitable_algorithms": ["逻辑回归", "线性SVM", "感知机"],
            "characteristics": ["简单", "易分类", "适合入门"]
        },
        "非线性数据": {
            "description": "需要非线性决策边界才能分开的复杂数据",
            "suitable_algorithms": ["决策树", "随机森林", "神经网络", "RBF SVM"],
            "characteristics": ["复杂", "真实场景", "挑战性"]
        },
        "聚类数据": {
            "description": "具有明显聚类结构的数据",
            "suitable_algorithms": ["K近邻", "朴素贝叶斯", "聚类算法"],
            "characteristics": ["聚类明显", "密度不同", "距离敏感"]
        },
        "环形数据": {
            "description": "呈同心圆分布的数据",
            "suitable_algorithms": ["RBF SVM", "神经网络", "核方法"],
            "characteristics": ["非线性", "径向分布", "核技巧"]
        },
        "月牙形数据": {
            "description": "呈月牙形分布的数据",
            "suitable_algorithms": ["SVM", "神经网络", "集成方法"],
            "characteristics": ["弯曲边界", "非凸分布", "复杂形状"]
        }
    }
    
    # 创建数据集类型卡片
    for i, (dataset_name, info) in enumerate(list(dataset_info.items())[:3]):
        if i % 3 == 0:
            cols = st.columns(3)
        
        with cols[i % 3]:
            with st.container():
                st.markdown(f"#### 📊 {dataset_name}")
                st.markdown(f"**描述：** {info['description']}")
                st.markdown("**适用算法：**")
                for algo in info['suitable_algorithms']:
                    st.markdown(f"• {algo}")
                st.markdown("**特点：**")
                for char in info['characteristics']:
                    st.markdown(f"• {char}")
    
    # 数据生成流程
    st.markdown("---")
    st.markdown("### 🔄 数据生成流程")
    
    flow_steps = [
        "选择数据集类型",
        "配置参数",
        "生成数据",
        "可视化分析",
        "导出数据"
    ]
    
    cols = st.columns(len(flow_steps))
    for i, (col, step) in enumerate(zip(cols, flow_steps)):
        with col:
            st.markdown(f"**步骤 {i+1}**")
            st.markdown(f"📌 {step}")
            if i < len(flow_steps) - 1:
                st.markdown("⬇️")
    
    # 使用提示
    st.markdown("---")
    st.markdown("### 💡 使用提示")
    
    tips = [
        "🎯 **选择合适的数据类型**：根据要测试的算法选择相应的数据集类型",
        "📊 **调整样本数量**：更多样本可以更好地展示算法性能，但计算时间更长",
        "🔧 **控制噪声水平**：适量噪声可以模拟真实数据，过多噪声会影响学习效果",
        "🎲 **固定随机种子**：使用相同的随机种子可以重现相同的数据集",
        "📈 **多维特征**：增加特征维度可以测试算法的高维数据处理能力"
    ]
    
    for tip in tips:
        st.markdown(tip)

def generate_dataset(dataset_type, n_samples, n_features, n_classes, random_state, noise_level):
    """生成指定类型的数据集"""
    
    np.random.seed(random_state)
    
    try:
        if dataset_type == "线性可分数据":
            X, y = make_classification(
                n_samples=n_samples,
                n_features=n_features,
                n_redundant=0,
                n_informative=n_features,
                n_clusters_per_class=1,
                n_classes=n_classes,
                class_sep=2.0,
                random_state=random_state
            )
        
        elif dataset_type == "非线性数据":
            X, y = make_classification(
                n_samples=n_samples,
                n_features=n_features,
                n_redundant=0,
                n_informative=n_features,
                n_clusters_per_class=2,
                n_classes=n_classes,
                class_sep=0.8,
                random_state=random_state
            )
        
        elif dataset_type == "聚类数据":
            X, y = make_blobs(
                n_samples=n_samples,
                centers=n_classes,
                n_features=n_features,
                cluster_std=1.0,
                random_state=random_state
            )
        
        elif dataset_type == "环形数据":
            if n_features != 2:
                st.warning("环形数据只支持2维特征，已自动调整")
                n_features = 2
            X, y = make_circles(
                n_samples=n_samples,
                noise=noise_level,
                factor=0.5,
                random_state=random_state
            )
        
        elif dataset_type == "月牙形数据":
            if n_features != 2:
                st.warning("月牙形数据只支持2维特征，已自动调整")
                n_features = 2
            X, y = make_moons(
                n_samples=n_samples,
                noise=noise_level,
                random_state=random_state
            )
        
        elif dataset_type == "高斯分布数据":
            X, y = make_gaussian_quantiles(
                n_samples=n_samples,
                n_features=n_features,
                n_classes=n_classes,
                random_state=random_state
            )
        
        elif dataset_type == "不平衡数据":
            # 创建不平衡的类别分布
            weights = [0.9] + [0.1/(n_classes-1)] * (n_classes-1)
            X, y = make_classification(
                n_samples=n_samples,
                n_features=n_features,
                n_redundant=0,
                n_informative=n_features,
                n_classes=n_classes,
                weights=weights,
                random_state=random_state
            )
        
        elif dataset_type == "多标签数据":
            X, y = make_multilabel_classification(
                n_samples=n_samples,
                n_features=n_features,
                n_classes=n_classes,
                n_labels=2,
                random_state=random_state
            )
            # 转换为单标签
            y = np.argmax(y, axis=1)
        
        elif dataset_type == "噪声数据":
            X, y = make_classification(
                n_samples=n_samples,
                n_features=n_features,
                n_redundant=0,
                n_informative=max(1, n_features//2),
                n_classes=n_classes,
                flip_y=noise_level,
                random_state=random_state
            )
        
        elif dataset_type == "Hastie数据":
            # 生成Hastie等人的10维2分类数据
            X, y = make_hastie_10_2(
                n_samples=n_samples,
                random_state=random_state
            )
            # 如果需要不同的特征数，进行调整
            if n_features != 10:
                if n_features < 10:
                    X = X[:, :n_features]
                else:
                    # 添加噪声特征
                    noise_features = np.random.RandomState(random_state).randn(n_samples, n_features - 10)
                    X = np.hstack([X, noise_features])
        
        elif dataset_type == "自定义数据":
            # 用户可以自定义数据生成逻辑
            X, y = create_custom_dataset(n_samples, n_features, n_classes, random_state)
        
        else:
            st.error(f"不支持的数据集类型: {dataset_type}")
            return
        
        # 添加噪声（除了已经包含噪声的数据类型）
        if dataset_type not in ["环形数据", "月牙形数据", "噪声数据"] and noise_level > 0:
            noise = np.random.normal(0, noise_level, X.shape)
            X += noise
        
        # 保存到session state
        st.session_state.generated_data = {
            'X': X,
            'y': y,
            'dataset_type': dataset_type,
            'n_samples': n_samples,
            'n_features': n_features,
            'n_classes': n_classes,
            'random_state': random_state,
            'noise_level': noise_level
        }
        
        st.success(f"✅ 成功生成 {dataset_type} 数据集！")
        st.rerun()
        
    except Exception as e:
        st.error(f"数据生成失败: {str(e)}")

def create_custom_dataset(n_samples, n_features, n_classes, random_state):
    """创建自定义数据集"""
    
    np.random.seed(random_state)
    
    # 生成螺旋形数据
    if n_features == 2 and n_classes == 2:
        t = np.linspace(0, 4*np.pi, n_samples//2)
        
        # 第一类：内螺旋
        r1 = t / (2*np.pi)
        x1 = r1 * np.cos(t) + np.random.normal(0, 0.1, len(t))
        y1 = r1 * np.sin(t) + np.random.normal(0, 0.1, len(t))
        
        # 第二类：外螺旋
        r2 = (t + np.pi) / (2*np.pi)
        x2 = r2 * np.cos(t + np.pi) + np.random.normal(0, 0.1, len(t))
        y2 = r2 * np.sin(t + np.pi) + np.random.normal(0, 0.1, len(t))
        
        X = np.vstack([np.column_stack([x1, y1]), np.column_stack([x2, y2])])
        y = np.hstack([np.zeros(len(t)), np.ones(len(t))])
        
        # 补充样本到指定数量
        if len(X) < n_samples:
            additional = n_samples - len(X)
            X_add, y_add = make_classification(
                n_samples=additional,
                n_features=2,
                n_classes=2,
                random_state=random_state
            )
            X = np.vstack([X, X_add])
            y = np.hstack([y, y_add])
    else:
        # 默认生成分类数据
        X, y = make_classification(
            n_samples=n_samples,
            n_features=n_features,
            n_classes=n_classes,
            random_state=random_state
        )
    
    return X, y

def show_generated_data_analysis():
    """显示生成数据的分析结果"""
    
    data = st.session_state.generated_data
    X, y = data['X'], data['y']
    
    # 数据集信息
    st.markdown("## 📊 数据集分析")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("数据集类型", data['dataset_type'])
    
    with col2:
        st.metric("样本数量", data['n_samples'])
    
    with col3:
        st.metric("特征数量", data['n_features'])
    
    with col4:
        st.metric("类别数量", len(np.unique(y)))
    
    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 数据可视化", "📋 统计信息", "🔍 特征分析", "⚖️ 类别分布", "💾 数据导出"])
    
    with tab1:
        show_data_visualization(X, y, data)
    
    with tab2:
        show_statistical_info(X, y, data)
    
    with tab3:
        show_feature_analysis(X, y, data)
    
    with tab4:
        show_class_distribution(X, y, data)
    
    with tab5:
        show_data_export(X, y, data)

def show_data_visualization(X, y, data):
    """显示数据可视化"""
    
    st.markdown("### 📈 数据分布可视化")
    
    n_features = X.shape[1]
    
    if n_features == 2:
        # 2D散点图
        fig = px.scatter(
            x=X[:, 0], y=X[:, 1], color=y.astype(str),
            title=f"{data['dataset_type']} - 2D分布",
            labels={'x': '特征1', 'y': '特征2', 'color': '类别'},
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
    elif n_features == 3:
        # 3D散点图
        fig = px.scatter_3d(
            x=X[:, 0], y=X[:, 1], z=X[:, 2], color=y.astype(str),
            title=f"{data['dataset_type']} - 3D分布",
            labels={'x': '特征1', 'y': '特征2', 'z': '特征3', 'color': '类别'}
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        # 高维数据：显示前两个主成分
        from sklearn.decomposition import PCA
        
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X)
        
        fig = px.scatter(
            x=X_pca[:, 0], y=X_pca[:, 1], color=y.astype(str),
            title=f"{data['dataset_type']} - PCA降维可视化",
            labels={'x': f'PC1 ({pca.explained_variance_ratio_[0]:.2%})', 
                   'y': f'PC2 ({pca.explained_variance_ratio_[1]:.2%})', 
                   'color': '类别'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"**说明：** 原始数据有{n_features}个特征，这里使用PCA降维到2D进行可视化")
        st.markdown(f"**方差解释比例：** PC1: {pca.explained_variance_ratio_[0]:.2%}, PC2: {pca.explained_variance_ratio_[1]:.2%}")
    
    # 特征分布直方图
    if n_features <= 6:
        st.markdown("### 📊 特征分布直方图")
        
        n_cols = min(3, n_features)
        n_rows = (n_features + n_cols - 1) // n_cols
        
        fig = make_subplots(
            rows=n_rows, cols=n_cols,
            subplot_titles=[f'特征 {i+1}' for i in range(n_features)]
        )
        
        for i in range(n_features):
            row = i // n_cols + 1
            col = i % n_cols + 1
            
            for class_label in np.unique(y):
                mask = y == class_label
                fig.add_trace(
                    go.Histogram(
                        x=X[mask, i],
                        name=f'类别 {class_label}',
                        opacity=0.7,
                        showlegend=(i == 0)
                    ),
                    row=row, col=col
                )
        
        fig.update_layout(height=300*n_rows, title="特征分布对比")
        st.plotly_chart(fig, use_container_width=True)

def show_statistical_info(X, y, data):
    """显示统计信息"""
    
    st.markdown("### 📋 基本统计信息")
    
    # 创建DataFrame
    feature_names = [f'特征_{i+1}' for i in range(X.shape[1])]
    df = pd.DataFrame(X, columns=feature_names)
    df['类别'] = y
    
    # 显示描述性统计
    st.markdown("#### 📊 描述性统计")
    st.dataframe(df.describe(), use_container_width=True)
    
    # 类别统计
    st.markdown("#### 🏷️ 类别统计")
    class_counts = pd.Series(y).value_counts().sort_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(class_counts.to_frame('样本数量'), use_container_width=True)
    
    with col2:
        # 类别分布饼图
        fig = px.pie(
            values=class_counts.values,
            names=[f'类别 {i}' for i in class_counts.index],
            title="类别分布"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 特征相关性
    if X.shape[1] <= 10:
        st.markdown("#### 🔗 特征相关性矩阵")
        
        corr_matrix = df[feature_names].corr()
        
        fig = px.imshow(
            corr_matrix,
            title="特征相关性热力图",
            color_continuous_scale="RdBu_r",
            aspect="auto"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # 数据质量检查
    st.markdown("#### ✅ 数据质量检查")
    
    quality_checks = {
        "缺失值数量": df.isnull().sum().sum(),
        "重复样本数量": df.duplicated().sum(),
        "数值特征数量": len([col for col in df.columns if df[col].dtype in ['int64', 'float64']]),
        "类别平衡度": f"{class_counts.min()}/{class_counts.max()} = {class_counts.min()/class_counts.max():.2f}"
    }
    
    for check, result in quality_checks.items():
        st.markdown(f"• **{check}**: {result}")

def show_feature_analysis(X, y, data):
    """显示特征分析"""
    
    st.markdown("### 🔍 特征重要性分析")
    
    # 使用随机森林计算特征重要性
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_selection import mutual_info_classif
    
    try:
        # 随机森林特征重要性
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X, y)
        rf_importance = rf.feature_importances_
        
        # 互信息特征重要性
        mi_importance = mutual_info_classif(X, y, random_state=42)
        
        # 创建特征重要性对比图
        feature_names = [f'特征_{i+1}' for i in range(X.shape[1])]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=feature_names,
            y=rf_importance,
            name='随机森林重要性',
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            x=feature_names,
            y=mi_importance,
            name='互信息重要性',
            marker_color='lightcoral'
        ))
        
        fig.update_layout(
            title="特征重要性对比",
            xaxis_title="特征",
            yaxis_title="重要性分数",
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 特征重要性排名
        st.markdown("#### 📊 特征重要性排名")
        
        importance_df = pd.DataFrame({
            '特征': feature_names,
            '随机森林重要性': rf_importance,
            '互信息重要性': mi_importance
        })
        
        importance_df['综合排名'] = (importance_df['随机森林重要性'].rank(ascending=False) + 
                                importance_df['互信息重要性'].rank(ascending=False)) / 2
        
        importance_df = importance_df.sort_values('综合排名')
        st.dataframe(importance_df, use_container_width=True)
        
    except Exception as e:
        st.warning(f"特征重要性分析失败: {str(e)}")
    
    # 特征分离度分析
    st.markdown("### 📏 特征分离度分析")
    
    if X.shape[1] <= 6:
        separability_scores = []
        
        for i in range(X.shape[1]):
            feature_data = X[:, i]
            
            # 计算类间距离和类内距离比值
            class_means = []
            class_stds = []
            
            for class_label in np.unique(y):
                mask = y == class_label
                class_means.append(np.mean(feature_data[mask]))
                class_stds.append(np.std(feature_data[mask]))
            
            # 类间距离
            between_class_distance = np.std(class_means)
            # 平均类内距离
            within_class_distance = np.mean(class_stds)
            
            # 分离度分数
            separability = between_class_distance / (within_class_distance + 1e-8)
            separability_scores.append(separability)
        
        # 创建分离度图表
        fig = go.Figure(data=go.Bar(
            x=[f'特征_{i+1}' for i in range(len(separability_scores))],
            y=separability_scores,
            marker_color='lightgreen'
        ))
        
        fig.update_layout(
            title="特征分离度分析",
            xaxis_title="特征",
            yaxis_title="分离度分数",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("**说明：** 分离度分数越高，该特征对类别区分的贡献越大")

def show_class_distribution(X, y, data):
    """显示类别分布分析"""
    
    st.markdown("### ⚖️ 类别分布详细分析")
    
    unique_classes = np.unique(y)
    n_classes = len(unique_classes)
    
    # 类别统计表
    class_stats = []
    for class_label in unique_classes:
        mask = y == class_label
        class_data = X[mask]
        
        stats = {
            '类别': f'类别 {class_label}',
            '样本数量': np.sum(mask),
            '占比': f'{np.sum(mask)/len(y)*100:.1f}%',
            '特征均值': np.mean(class_data, axis=0).tolist(),
            '特征标准差': np.std(class_data, axis=0).tolist()
        }
        class_stats.append(stats)
    
    # 显示类别统计
    st.markdown("#### 📊 类别统计表")
    
    for i, stats in enumerate(class_stats):
        with st.expander(f"📋 {stats['类别']} 详细信息"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**样本数量：** {stats['样本数量']}")
                st.markdown(f"**占比：** {stats['占比']}")
            
            with col2:
                if X.shape[1] <= 5:
                    st.markdown("**特征均值：**")
                    for j, mean_val in enumerate(stats['特征均值']):
                        st.markdown(f"• 特征{j+1}: {mean_val:.3f}")
    
    # 类别平衡性分析
    st.markdown("#### ⚖️ 类别平衡性分析")
    
    class_counts = pd.Series(y).value_counts().sort_index()
    
    # 计算不平衡指标
    imbalance_ratio = class_counts.max() / class_counts.min()
    entropy = -np.sum((class_counts / len(y)) * np.log2(class_counts / len(y) + 1e-8))
    max_entropy = np.log2(n_classes)
    balance_score = entropy / max_entropy
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("不平衡比例", f"{imbalance_ratio:.2f}")
    
    with col2:
        st.metric("平衡度分数", f"{balance_score:.3f}")
    
    with col3:
        balance_level = "高" if balance_score > 0.9 else "中" if balance_score > 0.7 else "低"
        st.metric("平衡等级", balance_level)
    
    # 类别分布可视化
    col1, col2 = st.columns(2)
    
    with col1:
        # 柱状图
        fig = px.bar(
            x=[f'类别 {i}' for i in class_counts.index],
            y=class_counts.values,
            title="类别样本数量分布",
            color=class_counts.values,
            color_continuous_scale="viridis"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 饼图
        fig = px.pie(
            values=class_counts.values,
            names=[f'类别 {i}' for i in class_counts.index],
            title="类别比例分布"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 建议
    st.markdown("#### 💡 数据集建议")
    
    suggestions = []
    
    if imbalance_ratio > 5:
        suggestions.append("⚠️ 数据集严重不平衡，建议使用SMOTE、权重调整或集成方法")
    elif imbalance_ratio > 2:
        suggestions.append("⚠️ 数据集轻微不平衡，可考虑使用类权重或重采样")
    else:
        suggestions.append("✅ 数据集相对平衡，适合大多数算法")
    
    if len(y) < 100:
        suggestions.append("⚠️ 样本数量较少，建议增加样本或使用简单模型")
    elif len(y) > 10000:
        suggestions.append("✅ 样本数量充足，可以使用复杂模型")
    
    if X.shape[1] > len(y) / 10:
        suggestions.append("⚠️ 特征维度相对较高，建议进行特征选择或降维")
    
    for suggestion in suggestions:
        st.markdown(suggestion)

def show_data_export(X, y, data):
    """显示数据导出选项"""
    
    st.markdown("### 💾 数据导出")
    
    # 创建DataFrame
    feature_names = [f'feature_{i+1}' for i in range(X.shape[1])]
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y
    
    # 数据预览
    st.markdown("#### 👀 数据预览")
    st.dataframe(df.head(10), use_container_width=True)
    
    # 导出选项
    st.markdown("#### 📤 导出选项")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV导出
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📄 下载CSV文件",
            data=csv_data,
            file_name=f"{data['dataset_type']}_dataset.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # JSON导出
        json_data = df.to_json(orient='records', indent=2)
        st.download_button(
            label="📋 下载JSON文件",
            data=json_data,
            file_name=f"{data['dataset_type']}_dataset.json",
            mime="application/json",
            use_container_width=True
        )
    
    # 数据集信息导出
    st.markdown("#### 📊 数据集信息")
    
    dataset_info = {
        "数据集类型": data['dataset_type'],
        "样本数量": data['n_samples'],
        "特征数量": data['n_features'],
        "类别数量": data['n_classes'],
        "随机种子": data['random_state'],
        "噪声水平": data['noise_level'],
        "生成时间": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    info_json = pd.Series(dataset_info).to_json(indent=2)
    st.download_button(
        label="ℹ️ 下载数据集信息",
        data=info_json,
        file_name=f"{data['dataset_type']}_info.json",
        mime="application/json",
        use_container_width=True
    )
    
    # 使用说明
    st.markdown("#### 📖 使用说明")
    st.markdown("""
    **CSV格式：** 适合在Excel、pandas等工具中使用
    
    **JSON格式：** 适合在Web应用或API中使用
    
    **数据集信息：** 包含生成参数，便于重现相同的数据集
    
    **特征命名：** feature_1, feature_2, ... 表示特征列，target表示目标变量
    """)