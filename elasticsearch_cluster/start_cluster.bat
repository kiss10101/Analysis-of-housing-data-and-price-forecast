@echo off
echo 启动Elasticsearch集群...
echo.

echo 启动节点1 (主节点)...
start "ES-Node-1" cmd /c "start_node-1.bat"
timeout /t 10

echo 启动节点2...
start "ES-Node-2" cmd /c "start_node-2.bat"
timeout /t 5

echo 启动节点3...
start "ES-Node-3" cmd /c "start_node-3.bat"

echo.
echo 集群启动完成！
echo 等待30秒后检查集群状态...
timeout /t 30

echo 检查集群状态:
curl -X GET "localhost:9200/_cluster/health?pretty"
pause
