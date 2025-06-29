# PowerShell脚本：清理Git中不需要的文件
# 适用于Windows PowerShell

Write-Host "🧹 开始清理Git中不需要跟踪的文件..." -ForegroundColor Green

# 清理Python缓存文件
Write-Host "清理Python缓存文件..." -ForegroundColor Yellow
try {
    git rm -r --cached __pycache__/ 2>$null
    Write-Host "✅ 清理__pycache__/完成" -ForegroundColor Green
} catch {
    Write-Host "ℹ️  __pycache__/未被跟踪或已清理" -ForegroundColor Cyan
}

# 清理数据库文件
Write-Host "清理数据库文件..." -ForegroundColor Yellow
try {
    git rm -r --cached data/db/ 2>$null
    Write-Host "✅ 清理data/db/完成" -ForegroundColor Green
} catch {
    Write-Host "ℹ️  data/db/未被跟踪或已清理" -ForegroundColor Cyan
}

try {
    git rm -r --cached data/db_dev/ 2>$null
    Write-Host "✅ 清理data/db_dev/完成" -ForegroundColor Green
} catch {
    Write-Host "ℹ️  data/db_dev/未被跟踪或已清理" -ForegroundColor Cyan
}

# 清理日志文件
Write-Host "清理日志文件..." -ForegroundColor Yellow
try {
    git rm --cached *.log 2>$null
    Write-Host "✅ 清理*.log完成" -ForegroundColor Green
} catch {
    Write-Host "ℹ️  *.log未被跟踪或已清理" -ForegroundColor Cyan
}

try {
    git rm --cached django.log 2>$null
    Write-Host "✅ 清理django.log完成" -ForegroundColor Green
} catch {
    Write-Host "ℹ️  django.log未被跟踪或已清理" -ForegroundColor Cyan
}

# 清理调试HTML文件
Write-Host "清理调试HTML文件..." -ForegroundColor Yellow
$debugFiles = @(
    "debug_*.html",
    "*_debug.html",
    "tabledata_debug.html",
    "housetyperank_debug.html",
    "servicemoney_debug.html",
    "heatmap_analysis_debug.html",
    "browser_console_check.html"
)

foreach ($pattern in $debugFiles) {
    try {
        git rm --cached $pattern 2>$null
        Write-Host "✅ 清理$pattern完成" -ForegroundColor Green
    } catch {
        Write-Host "ℹ️  $pattern未被跟踪或已清理" -ForegroundColor Cyan
    }
}

# 清理测试文件
Write-Host "清理测试文件..." -ForegroundColor Yellow
$testFiles = @(
    "test_*.py",
    "debug_*.py",
    "check_*.py",
    "analyze_*.py",
    "explore_*.py",
    "implement_*.py",
    "optimize_*.py",
    "verify_*.py"
)

foreach ($pattern in $testFiles) {
    try {
        git rm --cached $pattern 2>$null
        Write-Host "✅ 清理$pattern完成" -ForegroundColor Green
    } catch {
        Write-Host "ℹ️  $pattern未被跟踪或已清理" -ForegroundColor Cyan
    }
}

# 清理Elasticsearch文件
Write-Host "清理Elasticsearch文件..." -ForegroundColor Yellow
try {
    git rm -r --cached elasticsearch_cluster/node-*/ 2>$null
    Write-Host "✅ 清理elasticsearch_cluster/node-*/完成" -ForegroundColor Green
} catch {
    Write-Host "ℹ️  elasticsearch_cluster/node-*/未被跟踪或已清理" -ForegroundColor Cyan
}

# 清理Scrapy输出文件
Write-Host "清理Scrapy输出文件..." -ForegroundColor Yellow
try {
    git rm -r --cached scrapy_spider/output/ 2>$null
    Write-Host "✅ 清理scrapy_spider/output/完成" -ForegroundColor Green
} catch {
    Write-Host "ℹ️  scrapy_spider/output/未被跟踪或已清理" -ForegroundColor Cyan
}

# 清理机器学习模型文件
Write-Host "清理机器学习模型文件..." -ForegroundColor Yellow
$modelFiles = @(
    "*.joblib",
    "*.pkl",
    "*.pickle",
    "house_price_model.joblib"
)

foreach ($pattern in $modelFiles) {
    try {
        git rm --cached $pattern 2>$null
        Write-Host "✅ 清理$pattern完成" -ForegroundColor Green
    } catch {
        Write-Host "ℹ️  $pattern未被跟踪或已清理" -ForegroundColor Cyan
    }
}

# 清理配置文件
Write-Host "清理配置文件..." -ForegroundColor Yellow
$configFiles = @(
    "mongod_*.conf",
    "*.bat",
    "settings.py.backup"
)

foreach ($pattern in $configFiles) {
    try {
        git rm --cached $pattern 2>$null
        Write-Host "✅ 清理$pattern完成" -ForegroundColor Green
    } catch {
        Write-Host "ℹ️  $pattern未被跟踪或已清理" -ForegroundColor Cyan
    }
}

Write-Host "🎉 Git清理完成！" -ForegroundColor Green
Write-Host "📝 现在可以提交.gitignore文件了" -ForegroundColor Yellow
