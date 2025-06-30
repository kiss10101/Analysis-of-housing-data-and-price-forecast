@echo off
echo 停止Elasticsearch集群...
taskkill /f /im java.exe /fi "WINDOWTITLE eq ES-*"
echo 集群已停止
pause
