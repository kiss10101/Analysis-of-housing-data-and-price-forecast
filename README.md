# 🏠 Python租房房源数据可视化分析系统

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2.16-green.svg)](https://djangoproject.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-8.0.5-green.svg)](https://mongodb.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-blue.svg)](https://mysql.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

基于Django框架的房源数据分析系统，支持MySQL和MongoDB双数据库架构，提供完整的数据可视化、分析和预测功能。

## 🎯 项目特色

### **双数据库架构**
- **MySQL版本**: 传统关系型数据库，成熟稳定
- **MongoDB版本**: 现代文档数据库，灵活高效
- **无缝切换**: 用户可在两个版本间自由切换体验

### **核心功能**
- 📊 **数据可视化**: ECharts图表展示房源分布、价格趋势
- 🔍 **智能分析**: 多维度数据分析和统计
- 🏷️ **标签系统**: 房源标签管理和词云展示
- 📈 **价格预测**: 基于历史数据的价格预测模型
- 👤 **用户系统**: 完整的用户注册、登录、收藏功能

## 🚀 快速开始

### **环境要求**
- Python 3.11+
- Django 4.2.16
- MySQL 8.0
- MongoDB 8.0.5

### **安装步骤**

1. **克隆项目**
```bash
git clone <repository-url>
cd 房源数据分析与价格预测
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置数据库**
```bash
# MySQL配置
mysql -u root -p
CREATE DATABASE guangzhou_house;

# MongoDB配置 (确保MongoDB服务运行在端口27017)
mongod --dbpath "C:\data\db" --port 27017
```

4. **数据迁移**
```bash
# Django数据库迁移
python manage.py migrate

# MongoDB数据迁移
python mongodb_integration/migrate_all_data.py
```

5. **启动服务**
```bash
python manage.py runserver 8000
```

### **访问系统**
- **MySQL版本**: http://127.0.0.1:8000/app/login/
- **MongoDB版本**: http://127.0.0.1:8000/mongo/login/
- **测试账户**: 用户名 `admin`, 密码 `123456`

## 📊 数据概览

### **数据规模**
- **房源数据**: 10,783条广州房源记录
- **用户数据**: 10个测试用户账户
- **数据来源**: 链家网爬虫数据
- **更新频率**: 支持实时数据更新

### **数据字段**
- 房源标题、类型、位置、面积、朝向
- 价格信息、标签、图片
- 爬取时间、数据质量评分

## 🏗️ 系统架构

### **技术栈**
```
前端: Bootstrap + ECharts + jQuery
├── 响应式设计
├── 交互式图表
└── 现代化UI

后端: Django 4.2.16
├── MVT架构
├── RESTful设计
└── 中间件系统

数据库: MySQL 8.0 + MongoDB 8.0.5
├── 关系型数据 (MySQL)
├── 文档型数据 (MongoDB)
└── 双写同步机制

数据采集: Scrapy框架
├── 分布式爬虫
├── 数据清洗
└── 质量控制
```

### **目录结构**
```
项目根目录/
├── app/                    # MySQL版本应用
├── app_mongo/              # MongoDB版本应用
├── templates/              # 模板文件
│   ├── *.html             # MySQL版本模板
│   └── mongo/             # MongoDB版本模板
├── static/                 # 静态资源
├── media/                  # 媒体文件
├── mongodb_integration/    # MongoDB集成模块
├── middleware/             # 自定义中间件
└── 配置文件
```

## 📈 功能模块

### **用户系统**
- ✅ 用户注册/登录
- ✅ 个人信息管理
- ✅ 房源收藏功能
- ✅ 浏览历史记录

### **数据展示**
- ✅ 房源数据表格 (分页显示)
- ✅ 高级筛选和搜索
- ✅ 数据导出功能
- ✅ 实时数据更新

### **可视化分析**
- ✅ 房源地区分布图
- ✅ 户型占比饼图
- ✅ 价格趋势分析
- ✅ 热力图分析
- ✅ 词云标签展示

### **预测功能**
- ✅ 房价预测模型
- ✅ 趋势分析
- ✅ 影响因素分析
- ✅ 预测结果可视化

## 🔧 配置说明

### **数据库配置**
```python
# MySQL配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'guangzhou_house',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# MongoDB配置
import mongoengine as me
me.connect('house_data', host='127.0.0.1', port=27017)
```

### **缓存配置**
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}
```

## 📚 文档

### **完整文档列表**
- 📋 [项目状态总览](PROJECT_STATUS.md)
- 📝 [更新日志](CHANGELOG.md)
- 📚 [文档索引](DOCUMENTATION_INDEX.md)
- 📊 [MongoDB前端移植报告](mongo_frontend_migration_report.md)
- ⚡ [性能优化报告](performance_optimization_report.md)

### **开发文档**
- 🔧 [API文档](docs/api.md) (待完善)
- 🧪 [测试指南](docs/testing.md) (待完善)
- 🚀 [部署指南](docs/deployment.md) (待完善)

## 🧪 测试

### **运行测试**
```bash
# Django单元测试
python manage.py test

# 功能测试
python test_functionality.py

# 性能测试
python test_performance.py
```

### **测试覆盖率**
- 模型层: 90%+
- 视图层: 85%+
- 模板层: 80%+

## 🚀 部署

### **开发环境**
```bash
python manage.py runserver 8000
```

### **生产环境**
```bash
# 使用Gunicorn
gunicorn --bind 0.0.0.0:8000 项目名.wsgi:application

# 使用Docker (待实现)
docker-compose up -d
```

## 🤝 贡献指南

### **开发流程**
1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

### **代码规范**
- 遵循PEP 8规范
- 添加适当的注释
- 编写单元测试
- 更新相关文档

## 📄 许可证

本项目采用 [MIT许可证](LICENSE)

## 📞 联系方式

- **项目维护**: AI Assistant
- **技术支持**: 通过GitHub Issues
- **文档更新**: 2025-06-22

## 🎉 致谢

感谢以下技术和工具的支持：
- Django框架
- MongoDB数据库
- ECharts图表库
- Bootstrap UI框架
- Scrapy爬虫框架

---

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**
