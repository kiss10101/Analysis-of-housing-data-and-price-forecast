@echo off
echo 测试Elasticsearch集群...
echo.

echo 1. 检查集群健康状态:
curl -X GET "localhost:9200/_cluster/health?pretty"
echo.

echo 2. 检查节点信息:
curl -X GET "localhost:9200/_nodes?pretty"
echo.

echo 3. 创建测试索引:
curl -X PUT "localhost:9200/test_index" -H "Content-Type: application/json" -d "{\"settings\": {\"number_of_shards\": 3, \"number_of_replicas\": 1}}"
echo.

echo 4. 检查索引状态:
curl -X GET "localhost:9200/_cat/indices?v"
echo.

echo 5. 删除测试索引:
curl -X DELETE "localhost:9200/test_index"
echo.

echo 测试完成！
pause
