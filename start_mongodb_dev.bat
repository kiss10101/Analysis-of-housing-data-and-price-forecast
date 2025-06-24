@echo off
echo ========================================
echo MongoDB Development Environment Starter
echo ========================================
echo.

echo Stopping existing MongoDB processes...
taskkill /f /im mongod.exe >nul 2>&1
net stop MongoDB >nul 2>&1

echo Creating development configuration...
(
echo # MongoDB Development Configuration - No Auth
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
echo # Development: No authentication required
) > mongod_dev.conf

echo Ensuring data directories exist...
if not exist "data\db" mkdir data\db
if not exist "data\log" mkdir data\log

echo Starting MongoDB in development mode...
start "MongoDB-Dev" mongod --config mongod_dev.conf

echo Waiting for MongoDB to start...
timeout /t 5 >nul

echo Testing connection...
python -c "import pymongo; import time; time.sleep(2); client = pymongo.MongoClient('mongodb://127.0.0.1:27017/', serverSelectionTimeoutMS=5000); db = client.house_data; print('Houses count:', db.houses.count_documents({})); client.close(); print('SUCCESS: MongoDB development mode started')" 2>nul

if %errorlevel%==0 (
    echo.
    echo ========================================
    echo SUCCESS: MongoDB Development Mode Ready
    echo ========================================
    echo Connection: mongodb://127.0.0.1:27017/
    echo Authentication: DISABLED
    echo Database: house_data
    echo ========================================
) else (
    echo.
    echo ========================================
    echo WARNING: MongoDB started but connection failed
    echo This might be normal for first startup
    echo ========================================
)

echo.
echo Press any key to continue...
pause >nul
