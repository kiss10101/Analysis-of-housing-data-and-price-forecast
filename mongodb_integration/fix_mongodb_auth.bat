@echo off
echo 修复MongoDB服务配置 - 禁用认证
echo ================================

echo 1. 停止MongoDB服务...
net stop MongoDB

echo 2. 删除现有服务...
sc delete MongoDB

echo 3. 创建新服务（无认证）...
sc create MongoDB binPath= ""F:\Non-relational database technology\mongodb-windows-x86_64-8.0.5\bin\mongod.exe" --dbpath "F:\Non-relational database technology\mongodb-windows-x86_64-8.0.5\data" --logpath "F:\Non-relational database technology\mongodb-windows-x86_64-8.0.5\conf\mongod.log" --bind_ip_all --service" DisplayName= "MongoDB" start= auto

echo 4. 启动MongoDB服务...
net start MongoDB

echo 5. 检查服务状态...
sc query MongoDB

echo.
echo 修复完成！
echo 现在可以无认证访问MongoDB了
pause
