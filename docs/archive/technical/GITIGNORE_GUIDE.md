# 房源数据分析系统 .gitignore 配置指南

## 📋 完整的 .gitignore 文件内容

```gitignore
# ================================
# Python 相关
# ================================

# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# ================================
# Django 项目特定
# ================================

# Django migrations (可选择性忽略)
# */migrations/*.py
# */migrations/*.pyc
# !*/migrations/__init__.py

# Django settings
settings_local.py
local_settings.py

# Django static files (生产环境收集的)
/staticfiles/
/static_root/

# Django media files (用户上传的文件)
/media/
/uploads/

# Django session files
django_session/

# Django cache
django_cache/

# ================================
# 数据库相关
# ================================

# SQLite
*.sqlite3
*.sqlite3-journal
*.db

# MySQL
*.sql
*.dump

# PostgreSQL
*.backup

# MongoDB 数据文件
/data/db/
/data/db_dev/
/data/log/
mongod.lock

# MongoDB 配置文件 (包含敏感信息的)
mongod_production.conf

# ================================
# Elasticsearch 相关
# ================================

# Elasticsearch 数据目录
/elasticsearch_cluster/node-*/data/
/elasticsearch_cluster/node-*/logs/
/elasticsearch_cluster/elasticsearch-*/

# Elasticsearch 压缩包
*.zip
*.tar.gz

# ================================
# 机器学习模型
# ================================

# 训练好的模型文件
*.joblib
*.pkl
*.pickle
*.h5
*.model

# 数据集文件
*.csv
*.json
*.xlsx
*.xls

# ================================
# 日志文件
# ================================

# 应用日志
*.log
logs/
log/

# Scrapy 日志
scrapy_spider.log
spider.log

# Django 日志
django.log

# ================================
# 临时文件和缓存
# ================================

# 临时文件
*.tmp
*.temp
*~

# 系统缓存
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE 缓存
.vscode/
.idea/
*.swp
*.swo
*~

# ================================
# 测试和调试文件
# ================================

# 测试脚本
test_*.py
debug_*.py
check_*.py

# 调试输出
*_debug.html
*_debug.txt
*_debug.json

# 测试报告
test_report_*.txt
migration_report_*.txt

# ================================
# 文档和说明文件 (可选)
# ================================

# 临时文档
*.docx~
*.doc~
*.tmp

# 个人笔记
notes.md
todo.md
personal_*.md

# ================================
# 项目特定文件
# ================================

# 启动脚本的日志输出
startup_*.log
final_test_*.log

# 浏览器测试文件
browser_console_check.html
tabledata_debug.html
housetyperank_debug.html
servicemoney_debug.html
python_*_debug.html

# 项目清理脚本
项目清理脚本.py

# 临时创建的测试文件
create_*.py
generate_*.py
manual_test_*.py

# ================================
# 生产环境配置
# ================================

# 环境变量文件
.env.production
.env.local
.env.development

# 密钥文件
secret_key.txt
*.key
*.pem

# 配置备份
*.backup
settings.py.backup

# ================================
# 第三方服务
# ================================

# Redis
dump.rdb

# Nginx
nginx.conf.local

# Docker
docker-compose.override.yml
.dockerignore

# ================================
# 操作系统相关
# ================================

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini
$RECYCLE.BIN/

# macOS
.DS_Store
.AppleDouble
.LSOverride
Icon?

# Linux
*~
.nfs*

# ================================
# 编辑器相关
# ================================

# Visual Studio Code
.vscode/
*.code-workspace

# PyCharm
.idea/
*.iml
*.iws

# Sublime Text
*.sublime-project
*.sublime-workspace

# Vim
*.swp
*.swo
*~

# Emacs
*~
\#*\#
/.emacs.desktop
/.emacs.desktop.lock
*.elc
auto-save-list
tramp
.\#*

# ================================
# 网络和安全
# ================================

# SSL 证书
*.crt
*.key
*.pem
*.p12

# API 密钥
api_keys.txt
credentials.json

# ================================
# 性能分析
# ================================

# 性能分析报告
*.prof
*.profile

# 内存分析
*.hprof

# ================================
# 备份文件
# ================================

# 自动备份
*.bak
*.backup
*.old
*.orig

# 版本控制备份
*.rej
*.patch
```

## 📝 使用说明

### 1. 创建 .gitignore 文件
在项目根目录创建 `.gitignore` 文件，将上述内容复制进去。

### 2. 应用到现有项目
如果项目已经有一些不应该被跟踪的文件，需要先从 Git 中移除：

```bash
# 移除已经被跟踪的文件
git rm -r --cached __pycache__/
git rm -r --cached *.pyc
git rm -r --cached data/db/
git rm -r --cached *.log

# 提交更改
git add .gitignore
git commit -m "Add comprehensive .gitignore"
```

### 3. 特殊考虑

#### 数据库迁移文件
```gitignore
# 如果团队协作，建议保留迁移文件
# */migrations/*.py
# */migrations/*.pyc
# !*/migrations/__init__.py
```

#### 静态文件
```gitignore
# 开发环境可以忽略收集的静态文件
/staticfiles/
# 但保留源静态文件
!/static/
```

#### 配置文件
```gitignore
# 忽略本地配置
local_settings.py
# 但保留示例配置
!settings_example.py
```

## 🎯 项目特定建议

### 当前项目应该忽略的重要文件：
1. **数据库文件**: `data/db/`, `*.sqlite3`
2. **日志文件**: `*.log`, `django.log`
3. **调试文件**: `*_debug.html`, `debug_*.py`
4. **测试文件**: `test_*.py`, `check_*.py`
5. **模型文件**: `*.joblib`, `*.pkl`
6. **Elasticsearch数据**: `elasticsearch_cluster/node-*/data/`
7. **媒体文件**: `media/`
8. **Python缓存**: `__pycache__/`, `*.pyc`

### 应该保留的文件：
1. **源代码**: 所有 `.py` 文件
2. **模板文件**: `templates/`
3. **静态资源**: `static/`
4. **配置文件**: `settings.py`, `urls.py`
5. **文档文件**: `*.md`, `requirements.txt`
6. **启动脚本**: `*.bat`

## ⚠️ 注意事项

1. **敏感信息**: 确保数据库密码、API密钥等不被提交
2. **大文件**: 避免提交大型数据文件和模型文件
3. **个人配置**: 忽略个人IDE配置和临时文件
4. **环境差异**: 考虑不同开发环境的差异

## 🔧 维护建议

定期检查和更新 `.gitignore` 文件，确保：
- 新增的文件类型被正确忽略
- 团队成员的开发环境差异被考虑
- 生产环境的安全性要求被满足
