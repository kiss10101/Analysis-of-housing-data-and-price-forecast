@echo off
echo 关闭MongoDB以节省系统资源
echo ========================

echo 正在查找MongoDB进程...
tasklist /FI "IMAGENAME eq mongod.exe"

echo.
echo 关闭MongoDB进程...
taskkill /F /IM mongod.exe 2>nul

if %errorlevel% == 0 (
    echo ✅ MongoDB已关闭
) else (
    echo ℹ️  MongoDB未运行或已关闭
)

echo.
echo 下次工作时请运行: 快速恢复工作.bat
pause
