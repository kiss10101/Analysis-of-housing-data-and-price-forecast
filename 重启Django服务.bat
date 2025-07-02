@echo off
echo ========================================
echo Housing Data Analysis System - Restart
echo ========================================
echo.

echo Stopping Django service...
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 >nul

echo Starting MongoDB...
start /min "" "启动MongoDB版本.bat"
timeout /t 3 >nul

echo Starting Django service...
start /min "" "启动房源分析系统.bat"
timeout /t 5 >nul

echo.
echo Service restart completed!
echo.
echo Access URLs:
echo    Main System: http://127.0.0.1:8000/mongo/
echo    Smart QA: http://127.0.0.1:8000/mongo/rag/
echo.
echo Test Account:
echo    Username: test4071741
echo    Password: 0515
echo.
pause
