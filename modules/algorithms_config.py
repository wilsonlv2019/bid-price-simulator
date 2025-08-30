"""算法配置文件
定义所有分类算法的基本信息、参数和公式
"""

# 算法配置字典
ALGORITHMS_CONFIG = {
    'logistic_regression': {
        'name': '逻辑回归',
        'description': '基于逻辑函数的线性分类算法，通过最大似然估计学习参数',
        'formula': r'P(y=1|x) = \frac{1}{1+e^{-(w^T x + b)}}',
        'formula_explanation': {
            'P(y=1|x)': '给定特征x时标签为1的概率',
            'w': '权重向量',
            'x': '特征向量',
            'b': '偏置项',
            'e': '自然常数'
        },
        'default_params': {
            'C': 1.0,
            'max_iter': 100,
            'solver': 'lbfgs',
            'random_state': 42
        },
        'param_descriptions': {
            'C': '正则化强度的倒数，值越小正则化越强',
            'max_iter': '最大迭代次数',
            'solver': '优化算法',
            'random_state': '随机种子'
        },
        'advantages': ['计算效率高', '可解释性强', '不需要特征缩放', '输出概率'],
        'disadvantages': ['假设线性关系', '对异常值敏感', '需要大样本'],
        'use_cases': ['二分类问题', '医疗诊断', '营销响应预测', '风险评估'],
        'category': 'linear'
    },
    
    'decision_tree': {
        'name': '决策树',
        'description': '基于树形结构的分类算法，通过递归分割特征空间进行决策',
        'formula': r'Gini = 1 - \sum_{i=1}^{c} p_i^2',
        'formula_explanation': {
            'Gini': '基尼不纯度，衡量节点的混乱程度',
            'c': '类别数量',
            'p_i': '类别i在节点中的比例'
        },
        'default_params': {
            'max_depth': 5,
            'min_samples_split': 2,
            'min_samples_leaf': 1,
            'random_state': 42
        },
        'param_descriptions': {
            'max_depth': '树的最大深度',
            'min_samples_split': '分割内部节点所需的最小样本数',
            'min_samples_leaf': '叶节点所需的最小样本数',
            'random_state': '随机种子'
        },
        'advantages': ['易于理解和解释', '不需要数据预处理', '处理数值和分类特征', '自动特征选择'],
        'disadvantages': ['容易过拟合', '对噪声敏感', '偏向多值特征', '不稳定'],
        'use_cases': ['医疗诊断', '信贷审批', '客户分类', '规则提取'],
        'category': 'tree'
    },
    
    'random_forest': {
        'name': '随机森林',
        'description': '集成多个决策树的算法，通过投票机制提高预测准确性',
        'formula': r'\hat{y} = \text{mode}\{h_1(x), h_2(x), ..., h_B(x)\}',
        'formula_explanation': {
            '\hat{y}': '最终预测结果',
            'mode': '众数函数',
            'h_i(x)': '第i个决策树的预测',
            'B': '决策树的数量'
        },
        'default_params': {
            'n_estimators': 100,
            'max_depth': None,
            'min_samples_split': 2,
            'random_state': 42
        },
        'param_descriptions': {
            'n_estimators': '决策树的数量',
            'max_depth': '树的最大深度',
            'min_samples_split': '分割内部节点所需的最小样本数',
            'random_state': '随机种子'
        },
        'advantages': ['减少过拟合', '处理大数据集', '特征重要性', '鲁棒性强'],
        'disadvantages': ['内存消耗大', '训练时间长', '黑盒模型', '参数调优复杂'],
        'use_cases': ['图像分类', '基因分析', '股票预测', '推荐系统'],
        'category': 'ensemble'
    },
    
    'svm': {
        'name': '支持向量机',
        'description': '通过寻找最优分离超平面进行分类的算法',
        'formula': r'f(x) = \text{sign}\left(\sum_{i=1}^{n} \alpha_i y_i K(x_i, x) + b\right)',
        'formula_explanation': {
            'f(x)': '决策函数',
            'α_i': '拉格朗日乘数',
            'y_i': '训练样本标签',
            'K(x_i, x)': '核函数',
            'b': '偏置项'
        },
        'default_params': {
            'C': 1.0,
            'kernel': 'rbf',
            'gamma': 'scale',
            'random_state': 42
        },
        'param_descriptions': {
            'C': '正则化参数',
            'kernel': '核函数类型',
            'gamma': 'RBF核的参数',
            'random_state': '随机种子'
        },
        'advantages': ['高维数据有效', '内存效率高', '核技巧', '泛化能力强'],
        'disadvantages': ['大数据集慢', '特征缩放敏感', '无概率输出', '参数选择困难'],
        'use_cases': ['文本分类', '图像识别', '生物信息学', '手写识别'],
        'category': 'kernel'
    },
    
    'knn': {
        'name': 'K近邻',
        'description': '基于距离的懒惰学习算法，通过K个最近邻居进行分类',
        'formula': r'\hat{y} = \text{mode}\{y_{(1)}, y_{(2)}, ..., y_{(k)}\}',
        'formula_explanation': {
            '\hat{y}': '预测标签',
            'mode': '众数函数',
            'y_{(i)}': '第i个最近邻的标签',
            'k': '邻居数量'
        },
        'default_params': {
            'n_neighbors': 5,
            'weights': 'uniform',
            'algorithm': 'auto',
            'metric': 'minkowski'
        },
        'param_descriptions': {
            'n_neighbors': '邻居数量K',
            'weights': '权重函数',
            'algorithm': '计算最近邻的算法',
            'metric': '距离度量'
        },
        'advantages': ['简单易懂', '无参数假设', '适应局部模式', '多类分类'],
        'disadvantages': ['计算成本高', '维度诅咒', '对噪声敏感', '需要特征缩放'],
        'use_cases': ['推荐系统', '模式识别', '异常检测', '图像分类'],
        'category': 'instance_based'
    },
    
    'naive_bayes': {
        'name': '朴素贝叶斯',
        'description': '基于贝叶斯定理和特征独立假设的概率分类算法',
        'formula': r'P(y|x) = \frac{P(x|y)P(y)}{P(x)} = \frac{P(y)\prod_{i=1}^{n}P(x_i|y)}{P(x)}',
        'formula_explanation': {
            'P(y|x)': '后验概率',
            'P(x|y)': '似然概率',
            'P(y)': '先验概率',
            'P(x)': '边际概率',
            'P(x_i|y)': '特征i在类别y下的条件概率'
        },
        'default_params': {
            'alpha': 1.0,
            'fit_prior': True,
            'class_prior': None
        },
        'param_descriptions': {
            'alpha': '拉普拉斯平滑参数',
            'fit_prior': '是否学习类先验概率',
            'class_prior': '类的先验概率'
        },
        'advantages': ['训练快速', '需要少量训练数据', '处理多类分类', '对缺失值不敏感'],
        'disadvantages': ['强独立假设', '分类性能一般', '需要平滑处理', '对特征分布敏感'],
        'use_cases': ['文本分类', '垃圾邮件过滤', '情感分析', '医疗诊断'],
        'category': 'probabilistic'
    },
    
    'gradient_boosting': {
        'name': '梯度提升',
        'description': '通过梯度下降优化损失函数的集成学习算法',
        'formula': r'F_m(x) = F_{m-1}(x) + \gamma_m h_m(x)',
        'formula_explanation': {
            'F_m(x)': '第m轮的模型',
            'F_{m-1}(x)': '前一轮的模型',
            'γ_m': '学习率',
            'h_m(x)': '第m个弱学习器'
        },
        'default_params': {
            'n_estimators': 100,
            'learning_rate': 0.1,
            'max_depth': 3,
            'random_state': 42
        },
        'param_descriptions': {
            'n_estimators': '弱学习器数量',
            'learning_rate': '学习率',
            'max_depth': '每个弱学习器的最大深度',
            'random_state': '随机种子'
        },
        'advantages': ['预测精度高', '处理混合数据', '特征重要性', '鲁棒性好'],
        'disadvantages': ['容易过拟合', '训练时间长', '参数敏感', '内存消耗大'],
        'use_cases': ['竞赛建模', '排序问题', '回归分析', '特征选择'],
        'category': 'boosting'
    },
    
    'xgboost': {
        'name': 'XGBoost',
        'description': '极端梯度提升算法，优化的梯度提升框架',
        'formula': r'\text{obj}(\theta) = \sum_{i=1}^{n} l(y_i, \hat{y}_i) + \sum_{k=1}^{K} \Omega(f_k)',
        'formula_explanation': {
            'obj(θ)': '目标函数',
            'l': '损失函数',
            'y_i': '真实标签',
            '\hat{y}_i': '预测值',
            'Ω(f_k)': '正则化项'
        },
        'default_params': {
            'n_estimators': 100,
            'learning_rate': 0.1,
            'max_depth': 6,
            'random_state': 42
        },
        'param_descriptions': {
            'n_estimators': '弱学习器数量',
            'learning_rate': '学习率',
            'max_depth': '树的最大深度',
            'random_state': '随机种子'
        },
        'advantages': ['性能优异', '并行计算', '处理缺失值', '内置正则化'],
        'disadvantages': ['参数复杂', '内存消耗', '过拟合风险', '调参困难'],
        'use_cases': ['Kaggle竞赛', '点击率预测', '风险建模', '排序学习'],
        'category': 'boosting'
    },
    
    'neural_network': {
        'name': '神经网络',
        'description': '多层感知机，通过反向传播算法学习非线性映射',
        'formula': r'y = f(W_2 \cdot \sigma(W_1 \cdot x + b_1) + b_2)',
        'formula_explanation': {
            'y': '输出',
            'f': '激活函数',
            'W_1, W_2': '权重矩阵',
            'b_1, b_2': '偏置向量',
            'σ': '隐层激活函数',
            'x': '输入'
        },
        'default_params': {
            'hidden_layer_sizes': (100,),
            'activation': 'relu',
            'solver': 'adam',
            'max_iter': 200,
            'random_state': 42
        },
        'param_descriptions': {
            'hidden_layer_sizes': '隐层神经元数量',
            'activation': '激活函数',
            'solver': '优化算法',
            'max_iter': '最大迭代次数',
            'random_state': '随机种子'
        },
        'advantages': ['学习非线性', '通用逼近器', '自动特征学习', '适应性强'],
        'disadvantages': ['训练时间长', '需要大数据', '超参数多', '黑盒模型'],
        'use_cases': ['图像识别', '自然语言处理', '语音识别', '游戏AI'],
        'category': 'neural'
    },
    
    'lightgbm': {
        'name': 'LightGBM',
        'description': '轻量级梯度提升机，基于决策树的梯度提升框架',
        'formula': r'F(x) = \sum_{m=1}^{M} \gamma_m h_m(x)',
        'formula_explanation': {
            'F(x)': '最终模型',
            'M': '树的数量',
            'γ_m': '第m棵树的权重',
            'h_m(x)': '第m棵决策树'
        },
        'default_params': {
            'n_estimators': 100,
            'learning_rate': 0.1,
            'max_depth': -1,
            'num_leaves': 31,
            'random_state': 42
        },
        'param_descriptions': {
            'n_estimators': '弱学习器数量',
            'learning_rate': '学习率',
            'max_depth': '树的最大深度',
            'num_leaves': '叶子节点数量',
            'random_state': '随机种子'
        },
        'advantages': ['训练速度快', '内存占用少', '精度高', '支持并行'],
        'disadvantages': ['小数据集过拟合', '参数敏感', '对噪声敏感', '调参复杂'],
        'use_cases': ['大规模数据', '在线学习', '特征工程', '时间序列'],
        'category': 'boosting'
    }
}

# 算法类别
ALGORITHM_CATEGORIES = {
    'linear': '线性模型',
    'tree': '树模型',
    'ensemble': '集成学习',
    'kernel': '核方法',
    'instance_based': '基于实例',
    'probabilistic': '概率模型',
    'boosting': '提升方法',
    'neural': '神经网络'
}

# 获取算法信息的辅助函数
def get_algorithm_info(algorithm_name):
    """获取指定算法的配置信息"""
    return ALGORITHMS_CONFIG.get(algorithm_name, {})

def get_algorithms_by_category(category):
    """根据类别获取算法列表"""
    return [name for name, config in ALGORITHMS_CONFIG.items() 
            if config.get('category') == category]

def get_all_algorithm_names():
    """获取所有算法名称"""
    return list(ALGORITHMS_CONFIG.keys())

def get_algorithm_display_name(algorithm_name):
    """获取算法的显示名称"""
    return ALGORITHMS_CONFIG.get(algorithm_name, {}).get('name', algorithm_name)