import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
import time
import warnings
warnings.filterwarnings('ignore')

# 导入所有算法
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
try:
    import xgboost as xgb
    import lightgbm as lgb
except ImportError:
    xgb = None
    lgb = None

def show_algorithm_comparison():
    """显示算法比较页面"""
    st.title("🔍 算法比较与分析")
    st.markdown("---")
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 比较配置")
        
        # 算法选择
        st.subheader("算法选择")
        available_algorithms = get_available_algorithms()
        
        selected_algorithms = st.multiselect(
            "选择要比较的算法",
            list(available_algorithms.keys()),
            default=list(available_algorithms.keys())[:5]
        )
        
        if len(selected_algorithms) < 2:
            st.warning("⚠️ 请至少选择2个算法进行比较")
            return
        
        # 评估配置
        st.subheader("评估配置")
        cv_folds = st.slider("交叉验证折数", 3, 10, 5)
        random_state = st.number_input("随机种子", 0, 1000, 42)
        
        # 评估指标
        st.subheader("评估指标")
        metrics = st.multiselect(
            "选择评估指标",
            ["准确率", "精确率", "召回率", "F1分数", "AUC", "训练时间"],
            default=["准确率", "F1分数", "AUC"]
        )
        
        # 数据预处理
        st.subheader("数据预处理")
        scale_features = st.checkbox("特征标准化", value=True)
        
        # 比较类型
        st.subheader("比较类型")
        comparison_type = st.selectbox(
            "选择比较方式",
            ["性能比较", "效率比较", "稳定性比较", "综合比较"]
        )
    
    # 数据输入
    st.header("📊 数据输入")
    data_source = st.radio(
        "选择数据源",
        ["使用示例数据", "上传数据文件", "从数据生成模块获取"]
    )
    
    X, y = None, None
    
    if data_source == "使用示例数据":
        X, y = generate_sample_data()
        st.success(f"✅ 已加载示例数据: {X.shape[0]} 样本, {X.shape[1]} 特征")
    
    elif data_source == "上传数据文件":
        uploaded_file = st.file_uploader("上传CSV文件", type=['csv'], key="comparison_csv_uploader")
        if uploaded_file is not None:
            try:
                data = pd.read_csv(uploaded_file)
                st.write("数据预览:", data.head())
                
                # 选择特征和标签列
                feature_cols = st.multiselect("选择特征列", data.columns.tolist())
                target_col = st.selectbox("选择标签列", data.columns.tolist())
                
                if feature_cols and target_col:
                    X = data[feature_cols].values
                    y = data[target_col].values
                    st.success(f"✅ 数据加载成功: {X.shape[0]} 样本, {X.shape[1]} 特征")
            except Exception as e:
                st.error(f"数据加载失败: {str(e)}")
    
    elif data_source == "从数据生成模块获取":
        if 'generated_data' in st.session_state:
            X = st.session_state.generated_data['X']
            y = st.session_state.generated_data['y']
            st.success(f"✅ 已获取生成的数据: {X.shape[0]} 样本, {X.shape[1]} 特征")
        else:
            st.warning("⚠️ 请先在数据生成模块中生成数据")
    
    # 开始比较
    if X is not None and y is not None:
        if st.button("🚀 开始算法比较", type="primary"):
            with st.spinner("正在进行算法比较..."):
                results = compare_algorithms(
                    X, y, selected_algorithms, available_algorithms,
                    cv_folds, random_state, metrics, scale_features
                )
                
                # 保存结果到session state
                st.session_state.comparison_results = results
        
        # 显示比较结果
        if 'comparison_results' in st.session_state:
            show_comparison_results(
                st.session_state.comparison_results,
                comparison_type,
                metrics
            )

def get_available_algorithms():
    """获取可用的算法列表"""
    algorithms = {
        "逻辑回归": LogisticRegression(random_state=42, max_iter=1000),
        "决策树": DecisionTreeClassifier(random_state=42),
        "随机森林": RandomForestClassifier(random_state=42, n_estimators=100),
        "支持向量机": SVC(random_state=42, probability=True),
        "K近邻": KNeighborsClassifier(),
        "朴素贝叶斯": GaussianNB(),
        "梯度提升": GradientBoostingClassifier(random_state=42),
        "神经网络": MLPClassifier(random_state=42, max_iter=500)
    }
    
    # 添加可选算法
    if xgb is not None:
        algorithms["XGBoost"] = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
    
    if lgb is not None:
        algorithms["LightGBM"] = lgb.LGBMClassifier(random_state=42, verbose=-1)
    
    return algorithms

def generate_sample_data():
    """生成示例数据"""
    from sklearn.datasets import make_classification
    
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_informative=5,
        n_redundant=2,
        n_classes=3,
        random_state=42
    )
    
    return X, y

def compare_algorithms(X, y, selected_algorithms, available_algorithms, 
                      cv_folds, random_state, metrics, scale_features):
    """比较多个算法的性能"""
    results = {}
    
    # 数据预处理
    if scale_features:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
    else:
        X_scaled = X
    
    # 交叉验证设置
    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, alg_name in enumerate(selected_algorithms):
        status_text.text(f"正在评估: {alg_name}...")
        
        algorithm = available_algorithms[alg_name]
        alg_results = {}
        
        try:
            # 训练时间
            start_time = time.time()
            
            # 交叉验证评估
            if "准确率" in metrics:
                scores = cross_val_score(algorithm, X_scaled, y, cv=cv, scoring='accuracy')
                alg_results['准确率'] = {
                    'mean': scores.mean(),
                    'std': scores.std(),
                    'scores': scores
                }
            
            if "精确率" in metrics:
                scores = cross_val_score(algorithm, X_scaled, y, cv=cv, scoring='precision_macro')
                alg_results['精确率'] = {
                    'mean': scores.mean(),
                    'std': scores.std(),
                    'scores': scores
                }
            
            if "召回率" in metrics:
                scores = cross_val_score(algorithm, X_scaled, y, cv=cv, scoring='recall_macro')
                alg_results['召回率'] = {
                    'mean': scores.mean(),
                    'std': scores.std(),
                    'scores': scores
                }
            
            if "F1分数" in metrics:
                scores = cross_val_score(algorithm, X_scaled, y, cv=cv, scoring='f1_macro')
                alg_results['F1分数'] = {
                    'mean': scores.mean(),
                    'std': scores.std(),
                    'scores': scores
                }
            
            if "AUC" in metrics and len(np.unique(y)) == 2:  # 仅二分类
                scores = cross_val_score(algorithm, X_scaled, y, cv=cv, scoring='roc_auc')
                alg_results['AUC'] = {
                    'mean': scores.mean(),
                    'std': scores.std(),
                    'scores': scores
                }
            
            training_time = time.time() - start_time
            
            if "训练时间" in metrics:
                alg_results['训练时间'] = {
                    'mean': training_time,
                    'std': 0,
                    'scores': [training_time]
                }
            
            # 算法特性
            alg_results['algorithm_info'] = get_algorithm_info(alg_name)
            
        except Exception as e:
            st.warning(f"算法 {alg_name} 评估失败: {str(e)}")
            continue
        
        results[alg_name] = alg_results
        progress_bar.progress((i + 1) / len(selected_algorithms))
    
    status_text.text("算法比较完成!")
    return results

def get_algorithm_info(alg_name):
    """获取算法信息"""
    info = {
        "逻辑回归": {
            "类型": "线性模型",
            "复杂度": "低",
            "可解释性": "高",
            "适用场景": "线性可分数据",
            "优点": "简单快速，可解释性强",
            "缺点": "假设线性关系"
        },
        "决策树": {
            "类型": "树模型",
            "复杂度": "中",
            "可解释性": "高",
            "适用场景": "非线性数据",
            "优点": "易理解，处理非线性",
            "缺点": "容易过拟合"
        },
        "随机森林": {
            "类型": "集成学习",
            "复杂度": "中",
            "可解释性": "中",
            "适用场景": "大多数场景",
            "优点": "性能稳定，抗过拟合",
            "缺点": "模型较大"
        },
        "支持向量机": {
            "类型": "核方法",
            "复杂度": "高",
            "可解释性": "低",
            "适用场景": "高维数据",
            "优点": "处理高维数据好",
            "缺点": "训练时间长"
        },
        "K近邻": {
            "类型": "实例学习",
            "复杂度": "低",
            "可解释性": "中",
            "适用场景": "局部模式明显",
            "优点": "简单直观",
            "缺点": "对噪声敏感"
        },
        "朴素贝叶斯": {
            "类型": "概率模型",
            "复杂度": "低",
            "可解释性": "高",
            "适用场景": "文本分类",
            "优点": "训练快速",
            "缺点": "假设特征独立"
        },
        "梯度提升": {
            "类型": "集成学习",
            "复杂度": "高",
            "可解释性": "中",
            "适用场景": "结构化数据",
            "优点": "性能优秀",
            "缺点": "容易过拟合"
        },
        "XGBoost": {
            "类型": "集成学习",
            "复杂度": "高",
            "可解释性": "中",
            "适用场景": "竞赛和工业",
            "优点": "性能顶尖",
            "缺点": "参数复杂"
        },
        "神经网络": {
            "类型": "深度学习",
            "复杂度": "高",
            "可解释性": "低",
            "适用场景": "复杂模式",
            "优点": "表达能力强",
            "缺点": "需要大量数据"
        },
        "LightGBM": {
            "类型": "集成学习",
            "复杂度": "高",
            "可解释性": "中",
            "适用场景": "大数据集",
            "优点": "训练速度快",
            "缺点": "小数据集易过拟合"
        }
    }
    
    return info.get(alg_name, {
        "类型": "未知",
        "复杂度": "未知",
        "可解释性": "未知",
        "适用场景": "未知",
        "优点": "未知",
        "缺点": "未知"
    })

def show_comparison_results(results, comparison_type, metrics):
    """显示比较结果"""
    st.header("📈 比较结果")
    
    if comparison_type == "性能比较":
        show_performance_comparison(results, metrics)
    elif comparison_type == "效率比较":
        show_efficiency_comparison(results)
    elif comparison_type == "稳定性比较":
        show_stability_comparison(results, metrics)
    elif comparison_type == "综合比较":
        show_comprehensive_comparison(results, metrics)

def show_performance_comparison(results, metrics):
    """显示性能比较"""
    st.subheader("🎯 性能比较")
    
    # 创建性能对比表
    performance_data = []
    
    for alg_name, alg_results in results.items():
        row = {'算法': alg_name}
        for metric in metrics:
            if metric in alg_results and metric != '训练时间':
                mean_score = alg_results[metric]['mean']
                std_score = alg_results[metric]['std']
                row[metric] = f"{mean_score:.4f} ± {std_score:.4f}"
        performance_data.append(row)
    
    performance_df = pd.DataFrame(performance_data)
    st.dataframe(performance_df, use_container_width=True)
    
    # 性能对比图表
    if len(metrics) > 1:
        show_performance_radar_chart(results, metrics)
        show_performance_bar_chart(results, metrics)

def show_performance_radar_chart(results, metrics):
    """显示性能雷达图"""
    st.markdown("**性能雷达图**")
    
    fig = go.Figure()
    
    for alg_name, alg_results in results.items():
        values = []
        labels = []
        
        for metric in metrics:
            if metric in alg_results and metric != '训练时间':
                values.append(alg_results[metric]['mean'])
                labels.append(metric)
        
        if values:
            # 闭合雷达图
            values.append(values[0])
            labels.append(labels[0])
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=labels,
                fill='toself',
                name=alg_name
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        title="算法性能雷达图"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_performance_bar_chart(results, metrics):
    """显示性能条形图"""
    st.markdown("**性能条形图**")
    
    # 为每个指标创建子图
    valid_metrics = [m for m in metrics if m != '训练时间']
    
    if len(valid_metrics) > 0:
        fig = make_subplots(
            rows=1, cols=len(valid_metrics),
            subplot_titles=valid_metrics
        )
        
        for i, metric in enumerate(valid_metrics):
            alg_names = []
            mean_scores = []
            std_scores = []
            
            for alg_name, alg_results in results.items():
                if metric in alg_results:
                    alg_names.append(alg_name)
                    mean_scores.append(alg_results[metric]['mean'])
                    std_scores.append(alg_results[metric]['std'])
            
            fig.add_trace(
                go.Bar(
                    x=alg_names,
                    y=mean_scores,
                    error_y=dict(type='data', array=std_scores),
                    name=metric,
                    showlegend=False
                ),
                row=1, col=i+1
            )
        
        fig.update_layout(height=400, title="各算法性能对比")
        st.plotly_chart(fig, use_container_width=True)

def show_efficiency_comparison(results):
    """显示效率比较"""
    st.subheader("⚡ 效率比较")
    
    # 训练时间对比
    if any('训练时间' in alg_results for alg_results in results.values()):
        alg_names = []
        training_times = []
        
        for alg_name, alg_results in results.items():
            if '训练时间' in alg_results:
                alg_names.append(alg_name)
                training_times.append(alg_results['训练时间']['mean'])
        
        if training_times:
            fig = px.bar(
                x=alg_names,
                y=training_times,
                title="算法训练时间对比",
                labels={'x': '算法', 'y': '训练时间 (秒)'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 效率排名
            efficiency_data = list(zip(alg_names, training_times))
            efficiency_data.sort(key=lambda x: x[1])
            
            st.markdown("**训练速度排名 (从快到慢):**")
            for i, (alg_name, time_val) in enumerate(efficiency_data):
                st.write(f"{i+1}. {alg_name}: {time_val:.4f} 秒")

def show_stability_comparison(results, metrics):
    """显示稳定性比较"""
    st.subheader("📊 稳定性比较")
    
    # 计算变异系数 (CV = std/mean)
    stability_data = []
    
    for alg_name, alg_results in results.items():
        row = {'算法': alg_name}
        
        for metric in metrics:
            if metric in alg_results and metric != '训练时间':
                mean_val = alg_results[metric]['mean']
                std_val = alg_results[metric]['std']
                cv = std_val / mean_val if mean_val != 0 else 0
                row[f'{metric}_CV'] = cv
        
        stability_data.append(row)
    
    stability_df = pd.DataFrame(stability_data)
    
    # 显示变异系数表
    st.markdown("**变异系数 (越小越稳定):**")
    st.dataframe(stability_df, use_container_width=True)
    
    # 稳定性可视化
    if len(metrics) > 1:
        show_stability_visualization(results, metrics)

def show_stability_visualization(results, metrics):
    """显示稳定性可视化"""
    st.markdown("**稳定性箱线图**")
    
    valid_metrics = [m for m in metrics if m != '训练时间']
    
    for metric in valid_metrics:
        fig = go.Figure()
        
        for alg_name, alg_results in results.items():
            if metric in alg_results:
                scores = alg_results[metric]['scores']
                fig.add_trace(go.Box(
                    y=scores,
                    name=alg_name,
                    boxpoints='all'
                ))
        
        fig.update_layout(
            title=f"{metric} 分布比较",
            yaxis_title=metric
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_comprehensive_comparison(results, metrics):
    """显示综合比较"""
    st.subheader("🏆 综合比较")
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["性能排名", "算法特性", "推荐建议", "详细分析"])
    
    with tab1:
        show_algorithm_ranking(results, metrics)
    
    with tab2:
        show_algorithm_characteristics(results)
    
    with tab3:
        show_algorithm_recommendations(results, metrics)
    
    with tab4:
        show_detailed_analysis(results, metrics)

def show_algorithm_ranking(results, metrics):
    """显示算法排名"""
    st.markdown("**算法综合排名**")
    
    # 计算综合得分
    ranking_data = []
    
    for alg_name, alg_results in results.items():
        total_score = 0
        metric_count = 0
        
        for metric in metrics:
            if metric in alg_results and metric != '训练时间':
                total_score += alg_results[metric]['mean']
                metric_count += 1
        
        if metric_count > 0:
            avg_score = total_score / metric_count
            ranking_data.append({
                '算法': alg_name,
                '综合得分': avg_score,
                '排名': 0  # 将在排序后设置
            })
    
    # 排序
    ranking_data.sort(key=lambda x: x['综合得分'], reverse=True)
    
    # 设置排名
    for i, item in enumerate(ranking_data):
        item['排名'] = i + 1
    
    ranking_df = pd.DataFrame(ranking_data)
    st.dataframe(ranking_df, use_container_width=True)
    
    # 排名可视化
    fig = px.bar(
        ranking_df,
        x='算法',
        y='综合得分',
        title='算法综合得分排名',
        color='综合得分',
        color_continuous_scale='viridis'
    )
    st.plotly_chart(fig, use_container_width=True)

def show_algorithm_characteristics(results):
    """显示算法特性"""
    st.markdown("**算法特性对比**")
    
    characteristics_data = []
    
    for alg_name, alg_results in results.items():
        if 'algorithm_info' in alg_results:
            info = alg_results['algorithm_info']
            characteristics_data.append({
                '算法': alg_name,
                '类型': info['类型'],
                '复杂度': info['复杂度'],
                '可解释性': info['可解释性'],
                '适用场景': info['适用场景']
            })
    
    if characteristics_data:
        characteristics_df = pd.DataFrame(characteristics_data)
        st.dataframe(characteristics_df, use_container_width=True)
        
        # 特性分布
        col1, col2 = st.columns(2)
        
        with col1:
            type_counts = characteristics_df['类型'].value_counts()
            fig = px.pie(values=type_counts.values, names=type_counts.index, title='算法类型分布')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            complexity_counts = characteristics_df['复杂度'].value_counts()
            fig = px.pie(values=complexity_counts.values, names=complexity_counts.index, title='复杂度分布')
            st.plotly_chart(fig, use_container_width=True)

def show_algorithm_recommendations(results, metrics):
    """显示算法推荐"""
    st.markdown("**算法推荐建议**")
    
    # 基于性能的推荐
    best_performers = {}
    
    for metric in metrics:
        if metric != '训练时间':
            best_score = 0
            best_algorithm = None
            
            for alg_name, alg_results in results.items():
                if metric in alg_results:
                    score = alg_results[metric]['mean']
                    if score > best_score:
                        best_score = score
                        best_algorithm = alg_name
            
            if best_algorithm:
                best_performers[metric] = (best_algorithm, best_score)
    
    # 显示最佳性能算法
    st.markdown("**各指标最佳算法:**")
    for metric, (alg_name, score) in best_performers.items():
        st.write(f"- **{metric}**: {alg_name} ({score:.4f})")
    
    # 场景推荐
    st.markdown("**场景推荐:**")
    
    recommendations = {
        "🚀 追求最高性能": get_top_performer(results, metrics),
        "⚡ 需要快速训练": get_fastest_algorithm(results),
        "📊 需要可解释性": get_interpretable_algorithms(results),
        "🎯 平衡性能和速度": get_balanced_algorithm(results, metrics),
        "💾 内存受限": get_memory_efficient_algorithms(results)
    }
    
    for scenario, recommendation in recommendations.items():
        if recommendation:
            st.write(f"{scenario}: **{recommendation}**")

def get_top_performer(results, metrics):
    """获取性能最佳的算法"""
    best_score = 0
    best_algorithm = None
    
    for alg_name, alg_results in results.items():
        total_score = 0
        metric_count = 0
        
        for metric in metrics:
            if metric in alg_results and metric != '训练时间':
                total_score += alg_results[metric]['mean']
                metric_count += 1
        
        if metric_count > 0:
            avg_score = total_score / metric_count
            if avg_score > best_score:
                best_score = avg_score
                best_algorithm = alg_name
    
    return best_algorithm

def get_fastest_algorithm(results):
    """获取训练最快的算法"""
    fastest_time = float('inf')
    fastest_algorithm = None
    
    for alg_name, alg_results in results.items():
        if '训练时间' in alg_results:
            time_val = alg_results['训练时间']['mean']
            if time_val < fastest_time:
                fastest_time = time_val
                fastest_algorithm = alg_name
    
    return fastest_algorithm

def get_interpretable_algorithms(results):
    """获取可解释性强的算法"""
    interpretable = []
    
    for alg_name, alg_results in results.items():
        if 'algorithm_info' in alg_results:
            interpretability = alg_results['algorithm_info']['可解释性']
            if interpretability == '高':
                interpretable.append(alg_name)
    
    return ', '.join(interpretable) if interpretable else None

def get_balanced_algorithm(results, metrics):
    """获取平衡性能和速度的算法"""
    best_balance = 0
    best_algorithm = None
    
    for alg_name, alg_results in results.items():
        if '训练时间' in alg_results:
            # 计算性能得分
            performance_score = 0
            metric_count = 0
            
            for metric in metrics:
                if metric in alg_results and metric != '训练时间':
                    performance_score += alg_results[metric]['mean']
                    metric_count += 1
            
            if metric_count > 0:
                avg_performance = performance_score / metric_count
                training_time = alg_results['训练时间']['mean']
                
                # 平衡得分 = 性能 / 时间
                balance_score = avg_performance / max(training_time, 0.001)
                
                if balance_score > best_balance:
                    best_balance = balance_score
                    best_algorithm = alg_name
    
    return best_algorithm

def get_memory_efficient_algorithms(results):
    """获取内存效率高的算法"""
    memory_efficient = []
    
    # 基于算法特性判断
    efficient_algorithms = ['逻辑回归', '朴素贝叶斯', 'K近邻', '决策树']
    
    for alg_name in results.keys():
        if alg_name in efficient_algorithms:
            memory_efficient.append(alg_name)
    
    return ', '.join(memory_efficient) if memory_efficient else None

def show_detailed_analysis(results, metrics):
    """显示详细分析"""
    st.markdown("**详细分析报告**")
    
    # 选择算法进行详细分析
    selected_alg = st.selectbox(
        "选择算法查看详细信息",
        list(results.keys())
    )
    
    if selected_alg and selected_alg in results:
        alg_results = results[selected_alg]
        
        # 算法信息
        if 'algorithm_info' in alg_results:
            info = alg_results['algorithm_info']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**算法特性:**")
                st.write(f"- 类型: {info['类型']}")
                st.write(f"- 复杂度: {info['复杂度']}")
                st.write(f"- 可解释性: {info['可解释性']}")
                st.write(f"- 适用场景: {info['适用场景']}")
            
            with col2:
                st.markdown("**优缺点分析:**")
                st.write(f"- 优点: {info['优点']}")
                st.write(f"- 缺点: {info['缺点']}")
        
        # 性能详情
        st.markdown("**性能详情:**")
        
        performance_details = []
        for metric in metrics:
            if metric in alg_results:
                mean_val = alg_results[metric]['mean']
                std_val = alg_results[metric]['std']
                scores = alg_results[metric]['scores']
                
                performance_details.append({
                    '指标': metric,
                    '平均值': f"{mean_val:.4f}",
                    '标准差': f"{std_val:.4f}",
                    '最小值': f"{np.min(scores):.4f}",
                    '最大值': f"{np.max(scores):.4f}"
                })
        
        if performance_details:
            details_df = pd.DataFrame(performance_details)
            st.dataframe(details_df, use_container_width=True)
        
        # 性能分布图
        st.markdown("**性能分布:**")
        
        for metric in metrics:
            if metric in alg_results:
                scores = alg_results[metric]['scores']
                
                fig = px.histogram(
                    x=scores,
                    title=f"{selected_alg} - {metric} 分布",
                    labels={'x': metric, 'y': '频次'}
                )
                
                # 添加均值线
                mean_val = np.mean(scores)
                fig.add_vline(x=mean_val, line_dash="dash", line_color="red", 
                             annotation_text=f"均值: {mean_val:.4f}")
                
                st.plotly_chart(fig, use_container_width=True)