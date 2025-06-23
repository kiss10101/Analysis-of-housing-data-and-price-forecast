@echo off
title 房源数据分析与价格预测系统启动器
echo 正在启动房源数据分析与价格预测系统...
echo.

REM 检查虚拟环境
if exist .venv\Scripts\activate.bat (
    echo 正在激活虚拟环境...
    call .venv\Scripts\activate.bat
) else (
    echo 警告: 未找到虚拟环境，尝试使用系统Python环境
)

REM 检查依赖是否已安装
echo 正在检查依赖...
python -m pip install -r requirements.txt 2>nul

REM 检查数据库是否需要迁移
echo 正在检查数据库迁移...
python manage.py migrate

REM 启动服务器
echo.
echo 正在启动Web服务器...
echo.
echo 系统已启动！请访问: http://127.0.0.1:8000/app/login/
echo 按Ctrl+C可以停止服务器
echo.

REM 自动打开浏览器
start http://127.0.0.1:8000/app/login/

REM 启动Django服务器
python manage.py runserver 0.0.0.0:8000 