## 1. Architecture design

```mermaid
graph TD
    A[用户界面] --> B[Streamlit Web应用]
    B --> C[算法模块]
    B --> D[数据生成模块]
    B --> E[可视化模块]
    C --> F[Scikit-learn]
    C --> G[XGBoost]
    C --> H[LightGBM]
    C --> I[TensorFlow/Keras]
    D --> J[NumPy]
    D --> K[Pandas]
    E --> L[Matplotlib]
    E --> M[Plotly]
    E --> N[Seaborn]

    subgraph "前端展示层"
        A
        B
    end

    subgraph "核心算法层"
        C
        F
        G
        H
        I
    end

    subgraph "数据处理层"
        D
        J
        K
    end

    subgraph "可视化层"
        E
        L
        M
        N
    end
```

## 2. Technology Description

* **前端框架**: Streamlit - 快速构建数据科学Web应用

* **机器学习库**: Scikit-learn, XGBoost, LightGBM, TensorFlow/Keras

* **数据处理**: NumPy, Pandas

* **可视化**: Matplotlib, Plotly, Seaborn

* **数学公式渲染**: Streamlit-LaTeX

* **开发环境**: Python 3.8+, Jupyter Notebook(可选)

## 3. Route definitions

| Route                        | Purpose             |
| ---------------------------- | ------------------- |
| /                            | 主页面，显示项目介绍和算法选择菜单   |
| /algorithm/{algorithm\_name} | 算法学习页面，展示特定算法的原理和公式 |
| /data-generation             | 数据生成页面，创建和可视化训练数据   |
| /model-training              | 模型训练页面，配置参数并训练模型    |
| /results-analysis            | 结果分析页面，展示性能指标和可视化图表 |
| /algorithm-comparison        | 算法比较页面，对比多个算法的性能    |

## 4. API definitions

### 4.1 Core API

由于使用Streamlit框架，主要通过Python函数调用实现功能，无需传统REST API。

**算法训练接口**

```python
def train_algorithm(algorithm_name: str, X_train: np.ndarray, y_train: np.ndarray, params: dict) -> dict
```

参数说明:

| Param Name      | Param Type | isRequired | Description                                       |
| --------------- | ---------- | ---------- | ------------------------------------------------- |
| algorithm\_name | string     | true       | 算法名称 (logistic\_regression, decision\_tree, etc.) |
| X\_train        | np.ndarray | true       | 训练特征数据                                            |
| y\_train        | np.ndarray | true       | 训练标签数据                                            |
| params          | dict       | false      | 算法超参数配置                                           |

返回值:

| Param Name     | Param Type | Description |
| -------------- | ---------- | ----------- |
| model          | object     | 训练好的模型对象    |
| training\_time | float      | 训练耗时(秒)     |
| status         | string     | 训练状态        |

**数据生成接口**

```python
def generate_classification_data(n_samples: int, n_features: int, n_classes: int, noise: float) -> tuple
```

参数说明:

| Param Name  | Param Type | isRequired | Description |
| ----------- | ---------- | ---------- | ----------- |
| n\_samples  | int        | true       | 样本数量        |
| n\_features | int        | true       | 特征维度        |
| n\_classes  | int        | true       | 类别数量        |
| noise       | float      | false      | 噪声水平        |

**模型评估接口**

```python
def evaluate_model(model: object, X_test: np.ndarray, y_test: np.ndarray) -> dict
```

## 5. Server architecture diagram

```mermaid
graph TD
    A[Streamlit应用入口] --> B[页面路由控制器]
    B --> C[算法管理器]
    B --> D[数据管理器]
    B --> E[可视化管理器]
    C --> F[算法工厂]
    F --> G[逻辑回归]
    F --> H[决策树]
    F --> I[随机森林]
    F --> J[支持向量机]
    F --> K[其他算法...]
    D --> L[数据生成器]
    D --> M[数据预处理器]
    E --> N[图表生成器]
    E --> O[指标计算器]

    subgraph "应用层"
        A
        B
    end

    subgraph "业务逻辑层"
        C
        D
        E
    end

    subgraph "算法实现层"
        F
        G
        H
        I
        J
        K
    end

    subgraph "工具层"
        L
        M
        N
        O
    end
```

## 6. Data model

### 6.1 Data model definition

```mermaid
erDiagram
    ALGORITHM ||--o{ TRAINING_SESSION : has
    TRAINING_SESSION ||--|| DATASET : uses
    TRAINING_SESSION ||--|| MODEL_RESULT : produces
    MODEL_RESULT ||--o{ EVALUATION_METRIC : contains

    ALGORITHM {
        string name PK
        string display_name
        string description
        string formula
        dict default_params
        string category
    }
    
    DATASET {
        string id PK
        int n_samples
        int n_features
        int n_classes
        float noise_level
        datetime created_at
        array X_data
        array y_data
    }
    
    TRAINING_SESSION {
        string id PK
        string algorithm_name FK
        string dataset_id FK
        dict hyperparameters
        float training_time
        datetime created_at
        string status
    }
    
    MODEL_RESULT {
        string id PK
        string session_id FK
        object model_object
        array y_pred
        array y_pred_proba
        datetime created_at
    }
    
    EVALUATION_METRIC {
        string id PK
        string result_id FK
        string metric_name
        float metric_value
        string metric_type
    }
```

### 6.2 Data Definition Language

由于使用Python内存存储和Streamlit session state，无需传统数据库DDL。以下为主要数据结构定义：

**算法配置数据结构**

```python
# 算法注册表
ALGORITHMS = {
    'logistic_regression': {
        'name': '逻辑回归',
        'description': '基于逻辑函数的线性分类算法',
        'formula': 'P(y=1|x) = 1/(1+e^(-wx-b))',
        'default_params': {'C': 1.0, 'max_iter': 100},
        'category': 'linear'
    },
    'decision_tree': {
        'name': '决策树',
        'description': '基于树形结构的分类算法',
        'formula': 'Gini = 1 - Σ(p_i)^2',
        'default_params': {'max_depth': 5, 'min_samples_split': 2},
        'category': 'tree'
    },
    # ... 其他算法配置
}
```

**数据集结构**

```python
# 数据集类定义
class Dataset:
    def __init__(self, X, y, name="Generated Dataset"):
        self.X = X  # 特征矩阵
        self.y = y  # 标签向量
        self.name = name
        self.n_samples, self.n_features = X.shape
        self.n_classes = len(np.unique(y))
        self.created_at = datetime.now()
```

**训练会话结构**

```python
# 训练会话类定义
class TrainingSession:
    def __init__(self, algorithm_name, dataset, hyperparameters):
        self.id = str(uuid.uuid4())
        self.algorithm_name = algorithm_name
        self.dataset = dataset
        self.hyperparameters = hyperparameters
        self.model = None
        self.training_time = 0
        self.status = 'initialized'
        self.created_at = datetime.now()
        self.metrics = {}
```

**评估指标结构**

```python
# 评估指标类定义
class EvaluationMetrics:
    def __init__(self, y_true, y_pred, y_pred_proba=None):
        self.accuracy = accuracy_score(y_true, y_pred)
        self.precision = precision_score(y_true, y_pred, average='weighted')
        self.recall = recall_score(y_true, y_pred, average='weighted')
        self.f1_score = f1_score(y_true, y_pred, average='weighted')
        if y_pred_proba is not None:
            self.auc_score = roc_auc_score(y_true, y_pred_proba, multi_class='ovr')
        self.confusion_matrix = confusion_matrix(y_true, y_pred)
```

