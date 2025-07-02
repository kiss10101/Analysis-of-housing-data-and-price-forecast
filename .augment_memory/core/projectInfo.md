# 项目基本信息

## 项目概述
- **项目名称**: 房源数据分析与智能问答系统
- **项目类型**: Django Web应用 + RAG智能问答系统
- **主要功能**: 房源数据可视化分析、价格预测、用户管理、智能问答
- **开发语言**: Python
- **框架**: Django + RAG (火山引擎Doubao)

## 技术栈
### 后端框架
- Django >= 4.0.0

### 数据处理与分析
- pandas >= 1.3.0 - 数据处理
- numpy >= 1.21.0 - 数值计算
- scikit-learn >= 1.0.0 - 机器学习

### 可视化
- matplotlib >= 3.5.0 - 图表绘制
- seaborn >= 0.11.0 - 统计可视化
- plotly >= 5.0.0 - 交互式图表
- wordcloud >= 1.8.0 - 词云生成

### 数据库与网络
- PyMySQL >= 1.0.0 - MySQL数据库连接
- pymongo >= 4.0.0 - MongoDB数据库连接
- mongoengine >= 0.24.0 - MongoDB ORM
- requests >= 2.25.0 - HTTP请求
- lxml >= 4.6.0 - XML/HTML解析

### RAG智能问答
- faiss-cpu >= 1.7.0 - 向量数据库
- volcengine >= 1.0.0 - 火山引擎API
- sentence-transformers >= 2.0.0 - 文本向量化

### 图像处理
- Pillow >= 8.0.0 - 图像处理

## 项目结构
```
房源数据分析与智能问答系统/
├── Python租房房源数据可视化分析/  # Django项目配置
├── app/                          # MySQL版本应用
├── app_mongo/                    # MongoDB版本应用
├── rag_module/                   # RAG智能问答模块
├── spider/                       # 爬虫模块
├── scrapy_spider/                # Scrapy爬虫框架
├── mongodb_integration/          # MongoDB集成模块
├── templates/                    # 模板文件
│   ├── mongo/                   # MongoDB版本模板
│   └── ...                      # MySQL版本模板
├── static/                       # 静态资源
├── media/                        # 媒体文件
├── middleware/                   # 中间件
├── docs/                         # 项目文档
├── .augment_memory/             # AI记忆系统
└── manage.py                     # Django管理脚本
```

## 核心功能模块
1. **数据采集**: spider/scrapy_spider模块负责房源数据爬取
2. **数据分析**: 房源分布、价格分析、热力图
3. **价格预测**: 基于机器学习的房价预测模型
4. **可视化**: Matplotlib+Seaborn+Plotly图表展示、词云分析
5. **用户系统**: 登录注册、个人信息管理
6. **智能问答**: RAG系统，基于火山引擎Doubao的智能问答

## 数据库
- **主数据库**: MongoDB (house_data) - 10,785条房源数据
- **备份数据库**: MySQL (guangzhou_house) - 10,783条房源数据
- **向量数据库**: FAISS - 1000条房源向量数据
- **数据文件**: guangzhou_house.sql, houses_1000_enhanced.json

## 模型文件
- **预训练模型**: house_price_model.joblib
- **用途**: 房价预测
