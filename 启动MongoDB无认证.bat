@echo off
chcp 65001 >nul
echo 🍃 启动MongoDB（无认证模式）
echo ================================

echo 正在检查MongoDB进程...
tasklist /FI "IMAGENAME eq mongod.exe" 2>nul | find /I /N "mongod.exe">nul
if "%ERRORLEVEL%"=="0" (
    echo ✅ MongoDB已在运行
    echo 尝试连接测试...
    python mongodb_integration/simple_mongodb_test.py
    pause
    exit /b 0
)

echo 📍 启动MongoDB服务（无认证模式）...

REM 尝试多种MongoDB启动方式
echo 方式1: 尝试启动MongoDB服务...
net start MongoDB 2>nul
if "%ERRORLEVEL%"=="0" (
    echo ✅ MongoDB服务启动成功
    goto :test_connection
)

echo 方式2: 尝试直接启动mongod...
start "MongoDB" mongod --dbpath "C:\data\db" --noauth --bind_ip 127.0.0.1 --port 27017
timeout /t 5 >nul

echo 方式3: 尝试默认配置启动...
start "MongoDB" mongod --noauth
timeout /t 5 >nul

:test_connection
echo 等待MongoDB启动...
timeout /t 10 >nul

echo 测试连接...
python mongodb_integration/simple_mongodb_test.py

echo ================================
echo MongoDB启动完成
pause
