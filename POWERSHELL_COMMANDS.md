# PowerShell Git 清理命令

## 🚀 快速清理命令（逐个执行）

```powershell
# 清理Python缓存
git rm -r --cached __pycache__/ -ErrorAction SilentlyContinue

# 清理数据库文件
git rm -r --cached data/db/ -ErrorAction SilentlyContinue
git rm -r --cached data/db_dev/ -ErrorAction SilentlyContinue

# 清理日志文件
git rm --cached *.log -ErrorAction SilentlyContinue
git rm --cached django.log -ErrorAction SilentlyContinue

# 清理调试HTML文件
git rm --cached *_debug.html -ErrorAction SilentlyContinue
git rm --cached debug_*.html -ErrorAction SilentlyContinue
git rm --cached tabledata_debug.html -ErrorAction SilentlyContinue
git rm --cached housetyperank_debug.html -ErrorAction SilentlyContinue
git rm --cached servicemoney_debug.html -ErrorAction SilentlyContinue
git rm --cached heatmap_analysis_debug.html -ErrorAction SilentlyContinue
git rm --cached browser_console_check.html -ErrorAction SilentlyContinue

# 清理测试文件
git rm --cached test_*.py -ErrorAction SilentlyContinue
git rm --cached debug_*.py -ErrorAction SilentlyContinue
git rm --cached check_*.py -ErrorAction SilentlyContinue
git rm --cached analyze_*.py -ErrorAction SilentlyContinue
git rm --cached explore_*.py -ErrorAction SilentlyContinue
git rm --cached implement_*.py -ErrorAction SilentlyContinue
git rm --cached optimize_*.py -ErrorAction SilentlyContinue
git rm --cached verify_*.py -ErrorAction SilentlyContinue

# 清理Elasticsearch文件
git rm -r --cached elasticsearch_cluster/node-1/ -ErrorAction SilentlyContinue
git rm -r --cached elasticsearch_cluster/node-2/ -ErrorAction SilentlyContinue
git rm -r --cached elasticsearch_cluster/node-3/ -ErrorAction SilentlyContinue

# 清理Scrapy输出
git rm -r --cached scrapy_spider/output/ -ErrorAction SilentlyContinue

# 清理模型文件
git rm --cached *.joblib -ErrorAction SilentlyContinue
git rm --cached *.pkl -ErrorAction SilentlyContinue
git rm --cached house_price_model.joblib -ErrorAction SilentlyContinue

# 清理配置文件
git rm --cached mongod_*.conf -ErrorAction SilentlyContinue
git rm --cached *.bat -ErrorAction SilentlyContinue
git rm --cached settings.py.backup -ErrorAction SilentlyContinue
```

## 🎯 或者使用PowerShell脚本

```powershell
# 运行清理脚本
.\POWERSHELL_GIT_CLEANUP.ps1
```

## 📝 最后提交

```powershell
# 添加.gitignore文件
git add .gitignore

# 提交更改
git commit -m "Add comprehensive .gitignore for house analysis system"

# 查看状态
git status
```

## ⚠️ 注意事项

1. **-ErrorAction SilentlyContinue**: 这个参数让命令在文件不存在时不报错
2. **逐个执行**: 建议逐个执行命令，而不是一次性复制所有命令
3. **检查结果**: 每个命令执行后可以用 `git status` 检查状态

## 🔍 检查清理结果

```powershell
# 查看Git状态
git status

# 查看被忽略的文件
git status --ignored

# 查看.gitignore是否生效
git check-ignore -v data/db_dev/
```
