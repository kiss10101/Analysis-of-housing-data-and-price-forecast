# 项目架构文档

## 系统架构

### MVC架构模式
```
用户请求 → URLs路由 → Views视图 → Models模型 → 数据库
                    ↓
                Templates模板 → 响应返回
```

### 目录结构详解

#### 1. 核心Django配置 (`Python租房房源数据可视化分析/`)
- `settings.py` - 项目配置
- `urls.py` - 主URL路由
- `wsgi.py` - WSGI部署配置
- `asgi.py` - ASGI异步配置

#### 2. 主应用模块 (`app/`)
- `models.py` - 数据模型定义
- `views.py` - 视图逻辑
- `urls.py` - 应用URL路由
- `admin.py` - 后台管理
- `utils/` - 工具函数
- `migrations/` - 数据库迁移文件

#### 3. 数据采集模块 (`spider/`)
- `SpiderMain.py` - 主爬虫程序
- 负责从各大房产网站采集房源数据

#### 4. 前端资源
- `templates/` - HTML模板
  - `index.html` - 首页
  - `login.html` - 登录页
  - `pricePredict.html` - 价格预测页
  - `heatmap_analysis.html` - 热力图分析
  - 其他功能页面...
- `static/` - 静态资源
  - `css/` - 样式文件
  - `js/` - JavaScript文件
  - `bootstrap/` - Bootstrap框架
  - `picture/` - 图片资源

#### 5. 中间件 (`middleware/`)
- `userInfoMiddleWare.py` - 用户信息中间件

### 启动脚本
- `manage.py` - Django标准管理脚本
- `一键启动.bat` - Windows一键启动
- `quick_start.py` - 快速启动脚本
- `enhanced_start.py` - 增强启动脚本

### 数据流
1. **数据采集**: Spider → 原始数据
2. **数据处理**: pandas/numpy → 清洗后数据
3. **数据存储**: MySQL数据库
4. **数据分析**: scikit-learn → 分析结果
5. **数据展示**: matplotlib/wordcloud → 可视化图表
6. **Web展示**: Django → 用户界面

### 核心功能流程
1. **房源数据展示**: 数据库 → Views → Templates → 用户
2. **价格预测**: 用户输入 → 模型预测 → 结果展示
3. **数据分析**: 数据处理 → 图表生成 → 页面展示
4. **用户管理**: 注册/登录 → 会话管理 → 权限控制
