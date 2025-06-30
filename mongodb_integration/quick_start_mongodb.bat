@echo off
echo 快速启动MongoDB（临时方案）
echo ========================

echo 启动MongoDB服务器（本地访问，无认证）...
echo 数据目录: F:\Non-relational database technology\mongodb-windows-x86_64-8.0.5\data
echo 只允许本地访问（127.0.0.1）
echo.
echo 要停止MongoDB，请关闭此窗口
echo.

cd /d "F:\Non-relational database technology\mongodb-windows-x86_64-8.0.5\bin"
mongod.exe --dbpath "F:\Non-relational database technology\mongodb-windows-x86_64-8.0.5\data" --bind_ip 127.0.0.1

pause
