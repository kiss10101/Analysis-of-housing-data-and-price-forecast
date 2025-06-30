@echo off
chcp 65001 >nul
echo ========================================
echo MongoDB 认证管理脚本
echo ========================================
echo.

:menu
echo 请选择操作：
echo 1. 启动开发环境（无认证）
echo 2. 启动生产环境（需要认证）
echo 3. 停止MongoDB服务
echo 4. 查看MongoDB状态
echo 5. 重置MongoDB数据（危险操作）
echo 6. 退出
echo.
set /p choice=请输入选择 (1-6): 

if "%choice%"=="1" goto dev_mode
if "%choice%"=="2" goto prod_mode
if "%choice%"=="3" goto stop_mongo
if "%choice%"=="4" goto check_status
if "%choice%"=="5" goto reset_data
if "%choice%"=="6" goto exit
echo 无效选择，请重新输入
goto menu

:dev_mode
echo.
echo 🔧 启动开发环境（无认证模式）...
echo 正在停止现有MongoDB服务...
taskkill /f /im mongod.exe >nul 2>&1
net stop MongoDB >nul 2>&1

echo 创建开发环境配置文件...
(
echo # MongoDB开发环境配置 - 无认证
echo storage:
echo   dbPath: ./data/db
echo   journal:
echo     enabled: true
echo.
echo net:
echo   port: 27017
echo   bindIp: 127.0.0.1
echo.
echo systemLog:
echo   destination: file
echo   logAppend: true
echo   path: ./data/log/mongod_dev.log
echo.
echo # 开发环境：禁用认证
echo # security:
echo #   authorization: disabled
) > mongod_dev.conf

echo 确保数据目录存在...
if not exist "data\db" mkdir data\db
if not exist "data\log" mkdir data\log

echo 启动MongoDB开发环境...
start "MongoDB开发环境" mongod --config mongod_dev.conf
timeout /t 3 >nul

echo 测试连接...
python -c "import pymongo; import time; time.sleep(2); client = pymongo.MongoClient('mongodb://127.0.0.1:27017/', serverSelectionTimeoutMS=3000); print('✅ MongoDB开发环境启动成功'); client.close()" 2>nul
if %errorlevel%==0 (
    echo ✅ MongoDB开发环境启动成功！
    echo 📍 连接地址: mongodb://127.0.0.1:27017/
    echo 🔓 认证状态: 无需认证
) else (
    echo ❌ MongoDB启动失败，请检查日志
)
echo.
pause
goto menu

:prod_mode
echo.
echo 🔒 启动生产环境（认证模式）...
echo 正在停止现有MongoDB服务...
taskkill /f /im mongod.exe >nul 2>&1

echo 创建生产环境配置文件...
(
echo # MongoDB生产环境配置 - 需要认证
echo storage:
echo   dbPath: ./data/db
echo   journal:
echo     enabled: true
echo.
echo net:
echo   port: 27017
echo   bindIp: 127.0.0.1
echo.
echo systemLog:
echo   destination: file
echo   logAppend: true
echo   path: ./data/log/mongod_prod.log
echo.
echo # 生产环境：启用认证
echo security:
echo   authorization: enabled
) > mongod_prod.conf

echo 启动MongoDB生产环境...
start "MongoDB生产环境" mongod --config mongod_prod.conf
timeout /t 3 >nul

echo ✅ MongoDB生产环境启动成功！
echo 📍 连接地址: mongodb://127.0.0.1:27017/
echo 🔒 认证状态: 需要用户名密码
echo ⚠️  请确保已创建管理员用户
echo.
pause
goto menu

:stop_mongo
echo.
echo 🛑 停止MongoDB服务...
taskkill /f /im mongod.exe >nul 2>&1
net stop MongoDB >nul 2>&1
echo ✅ MongoDB服务已停止
echo.
pause
goto menu

:check_status
echo.
echo 📊 检查MongoDB状态...
tasklist /fi "imagename eq mongod.exe" | find "mongod.exe" >nul
if %errorlevel%==0 (
    echo ✅ MongoDB进程正在运行
    python -c "import pymongo; client = pymongo.MongoClient('mongodb://127.0.0.1:27017/', serverSelectionTimeoutMS=3000); print('✅ MongoDB连接正常'); client.close()" 2>nul
    if %errorlevel%==0 (
        echo ✅ MongoDB连接测试成功
    ) else (
        echo ⚠️  MongoDB进程运行但连接失败（可能需要认证）
    )
) else (
    echo ❌ MongoDB进程未运行
)
echo.
pause
goto menu

:reset_data
echo.
echo ⚠️  危险操作：重置MongoDB数据
echo 这将删除所有数据库数据！
set /p confirm=确认重置？(输入 YES 确认): 
if not "%confirm%"=="YES" (
    echo 操作已取消
    goto menu
)

echo 停止MongoDB服务...
taskkill /f /im mongod.exe >nul 2>&1
timeout /t 2 >nul

echo 删除数据目录...
if exist "data\db" rmdir /s /q data\db
if exist "data\log" rmdir /s /q data\log

echo 重新创建目录...
mkdir data\db
mkdir data\log

echo ✅ MongoDB数据已重置
echo.
pause
goto menu

:exit
echo.
echo 👋 感谢使用MongoDB认证管理脚本
exit /b 0
