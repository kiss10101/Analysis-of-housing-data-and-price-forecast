@echo off
:: One-Click Startup Script for Housing Data Analysis System
:: Version: 2025-07-02
:: Encoding: ANSI to avoid PowerShell issues

title Housing Data Analysis System - One Click Start
color 0A

echo.
echo ================================================================
echo          Housing Data Analysis and AI Q&A System
echo                    One-Click Startup Script
echo                      Version: 2025-07-02
echo ================================================================
echo.
echo Starting system components...
echo.

:: Step 1: Start MongoDB without authentication
echo [Step 1] Starting MongoDB...
echo --------------------------------
net stop MongoDB >nul 2>&1
timeout /t 2 >nul

start "MongoDB NoAuth" /min mongod --dbpath "C:\data\db" --noauth --bind_ip 127.0.0.1 --port 27017
echo MongoDB starting in no-auth mode...
timeout /t 8 >nul

:: Test MongoDB connection
python -c "import pymongo; client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000); client.server_info(); db = client['house_data']; count = db.houses.count_documents({}); print('MongoDB connected successfully, Housing data:', count, 'records'); client.close()" 2>nul
if %errorlevel% neq 0 (
    echo MongoDB connection failed!
    echo Please check MongoDB installation.
    pause
    exit /b 1
)

:: Step 2: Database migration
echo.
echo [Step 2] Preparing Django...
echo --------------------------------
python manage.py migrate --run-syncdb >nul 2>&1

:: Step 3: Start Django server
echo.
echo [Step 3] Starting Django Web Server...
echo --------------------------------
start "Django Server" python manage.py runserver 8000
echo Django server starting...
timeout /t 5 >nul

:: Step 4: Test web server
python -c "import requests; import time; time.sleep(2); r = requests.get('http://127.0.0.1:8000/mongo/login/', timeout=5); print('Django server is running!' if r.status_code == 200 else 'Django server check failed')" 2>nul

:: Step 5: Run 1-minute spider test
echo.
echo [Step 5] Running 1-minute spider test...
echo --------------------------------
echo Starting spider for 60 seconds...

cd scrapy_spider
timeout 60 python -m scrapy crawl lianjia -a pages=2 -s DOWNLOAD_DELAY=3 -s CONCURRENT_REQUESTS=1 >nul 2>&1
cd ..
echo Spider test completed.

:: Startup complete
echo.
echo ================================================================
echo                     STARTUP COMPLETED!
echo ================================================================
echo.
echo System Status:
echo   MongoDB Database: Running (No-Auth mode)
echo   Django Web Server: Running (Background)
echo   Spider Test: Completed
echo.
echo Access URLs:
echo   MongoDB Version: http://127.0.0.1:8000/mongo/login/
echo   RAG AI Q&A: http://127.0.0.1:8000/mongo/rag/
echo   Data Overview: http://127.0.0.1:8000/mongo/tableData/
echo   Word Cloud: http://127.0.0.1:8000/mongo/housewordcloud/
echo   Price Prediction: http://127.0.0.1:8000/mongo/predict-all-prices/
echo.
echo Test Account:
echo   Username: test4071741
echo   Password: 0515
echo.
echo Tips:
echo   - Django server is running in background
echo   - Close this window will NOT stop the server
echo   - Use Task Manager to stop if needed
echo.
echo Press any key to exit this startup script...
pause >nul
exit /b 0
