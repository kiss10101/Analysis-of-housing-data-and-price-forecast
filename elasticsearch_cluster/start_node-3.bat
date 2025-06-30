@echo off
echo 启动Elasticsearch节点: node-3
cd /d "D:\Program Files\cursor-workpace\房源数据分析与价格预测\elasticsearch_cluster\elasticsearch-7.17.0"
set ES_PATH_CONF=D:\Program Files\cursor-workpace\房源数据分析与价格预测\elasticsearch_cluster\node-3
bin\elasticsearch.bat
pause
