import streamlit as st
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.home import show_home_page
from modules.algorithm_learning import show_algorithm_learning_page
from modules.data_generation import show_data_generation_page
from modules.model_training import show_model_training_page
from modules.results_analysis import show_results_analysis_page
from modules.algorithm_comparison import show_algorithm_comparison

# 页面配置
st.set_page_config(
    page_title="Python数据分类学习小程序",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2563eb;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sidebar-header {
        font-size: 1.5rem;
        color: #1e40af;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .algorithm-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """主应用函数"""
    
    # 初始化session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'selected_algorithm' not in st.session_state:
        st.session_state.selected_algorithm = None
    if 'generated_data' not in st.session_state:
        st.session_state.generated_data = None
    if 'trained_models' not in st.session_state:
        st.session_state.trained_models = {}
    if 'training_results' not in st.session_state:
        st.session_state.training_results = {}
    
    # 侧边栏导航
    with st.sidebar:
        st.markdown('<div class="sidebar-header">📚 导航菜单</div>', unsafe_allow_html=True)
        
        # 页面选择
        pages = {
            'home': '🏠 主页面',
            'algorithm_learning': '📖 算法学习',
            'data_generation': '📊 数据生成',
            'model_training': '🔧 模型训练',
            'results_analysis': '📈 结果分析',
            'algorithm_comparison': '⚖️ 算法比较'
        }
        
        for page_key, page_name in pages.items():
            if st.button(page_name, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # 算法快速选择
        st.markdown("**🎯 快速选择算法**")
        algorithms = [
            'logistic_regression', 'decision_tree', 'random_forest',
            'svm', 'knn', 'naive_bayes', 'gradient_boosting',
            'xgboost', 'neural_network', 'lightgbm'
        ]
        
        algorithm_names = {
            'logistic_regression': '逻辑回归',
            'decision_tree': '决策树',
            'random_forest': '随机森林',
            'svm': '支持向量机',
            'knn': 'K近邻',
            'naive_bayes': '朴素贝叶斯',
            'gradient_boosting': '梯度提升',
            'xgboost': 'XGBoost',
            'neural_network': '神经网络',
            'lightgbm': 'LightGBM'
        }
        
        selected_algo = st.selectbox(
            "选择算法",
            options=[''] + algorithms,
            format_func=lambda x: '请选择算法' if x == '' else algorithm_names.get(x, x),
            key="sidebar_algorithm_select"
        )
        
        if selected_algo and selected_algo != '':
            st.session_state.selected_algorithm = selected_algo
            if st.button("📖 学习此算法", use_container_width=True):
                st.session_state.current_page = 'algorithm_learning'
                st.rerun()
    
    # 主内容区域
    current_page = st.session_state.current_page
    
    if current_page == 'home':
        show_home_page()
    elif current_page == 'algorithm_learning':
        show_algorithm_learning_page()
    elif current_page == 'data_generation':
        show_data_generation_page()
    elif current_page == 'model_training':
        show_model_training_page()
    elif current_page == 'results_analysis':
        show_results_analysis_page()
    elif current_page == 'algorithm_comparison':
        show_algorithm_comparison()

if __name__ == "__main__":
    main()