@echo off
title 房源数据分析与价格预测系统
echo ====================================
echo    房源数据分析与价格预测系统
echo    双数据库架构 (MySQL + MongoDB)
echo ====================================
echo.

:: 设置编码为UTF-8
chcp 65001 >nul

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH
    echo 请安装Python 3.8+并添加到系统PATH
    pause
    exit /b 1
)

echo [2/3] 启动MongoDB服务...
start /min cmd /c "mongodb_integration\quick_start_mongodb.bat"
timeout /t 3 >nul

echo [3/3] 启动Django服务器...
echo.
echo 🚀 系统启动中，请稍候...
echo.
echo 📍 访问地址:
echo    MySQL版本:  http://127.0.0.1:8000/app/login/
echo    MongoDB版本: http://127.0.0.1:8000/mongo/login/
echo.
echo 👤 测试账户: test4071741 / 0515
echo.
echo ⚠️  关闭此窗口将停止系统运行
echo.

python manage.py runserver 8000

echo.
echo 系统已停止运行
pause
