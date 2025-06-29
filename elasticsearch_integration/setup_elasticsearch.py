#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elasticsearch分布式集群安装和配置脚本
房源数据分析系统 - 大数据存储方案部署
"""

import os
import sys
import subprocess
import time
import requests
import json
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ElasticsearchSetup:
    """Elasticsearch安装配置类"""
    
    def __init__(self):
        self.es_version = "7.17.0"  # 使用稳定版本
        self.base_dir = Path("elasticsearch_cluster")
        self.nodes = [
            {"name": "node-1", "port": 9200, "transport_port": 9300},
            {"name": "node-2", "port": 9201, "transport_port": 9301},
            {"name": "node-3", "port": 9202, "transport_port": 9302}
        ]
        self.cluster_name = "house-data-cluster"
    
    def download_elasticsearch(self):
        """下载Elasticsearch"""
        logger.info("开始下载Elasticsearch...")
        
        # 创建目录
        self.base_dir.mkdir(exist_ok=True)
        
        # 检查是否已下载
        es_archive = self.base_dir / f"elasticsearch-{self.es_version}-windows-x86_64.zip"
        if es_archive.exists():
            logger.info("Elasticsearch已下载，跳过下载步骤")
            return True
        
        # 下载URL
        download_url = f"https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-{self.es_version}-windows-x86_64.zip"
        
        try:
            import urllib.request
            logger.info(f"正在下载: {download_url}")
            urllib.request.urlretrieve(download_url, es_archive)
            logger.info("✅ Elasticsearch下载完成")
            return True
        except Exception as e:
            logger.error(f"❌ 下载失败: {e}")
            logger.info("请手动下载Elasticsearch并放置在elasticsearch_cluster目录下")
            return False
    
    def extract_elasticsearch(self):
        """解压Elasticsearch"""
        logger.info("开始解压Elasticsearch...")
        
        es_archive = self.base_dir / f"elasticsearch-{self.es_version}-windows-x86_64.zip"
        if not es_archive.exists():
            logger.error("Elasticsearch压缩包不存在")
            return False
        
        try:
            import zipfile
            with zipfile.ZipFile(es_archive, 'r') as zip_ref:
                zip_ref.extractall(self.base_dir)
            
            logger.info("✅ Elasticsearch解压完成")
            return True
        except Exception as e:
            logger.error(f"❌ 解压失败: {e}")
            return False
    
    def create_node_configs(self):
        """创建节点配置文件"""
        logger.info("创建节点配置文件...")
        
        es_home = self.base_dir / f"elasticsearch-{self.es_version}"
        
        for i, node in enumerate(self.nodes):
            node_dir = self.base_dir / node["name"]
            node_dir.mkdir(exist_ok=True)
            
            # 创建数据和日志目录
            (node_dir / "data").mkdir(exist_ok=True)
            (node_dir / "logs").mkdir(exist_ok=True)
            
            # 生成配置文件
            config_content = self.generate_node_config(node, i == 0)
            
            config_file = node_dir / "elasticsearch.yml"
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            logger.info(f"✅ 节点 {node['name']} 配置创建完成")
        
        return True
    
    def generate_node_config(self, node, is_master=False):
        """生成节点配置"""
        config = f"""# Elasticsearch配置文件 - {node['name']}
# 集群配置
cluster.name: {self.cluster_name}
node.name: {node['name']}

# 节点角色
node.master: {"true" if is_master else "false"}
node.data: true
node.ingest: true

# 网络配置
network.host: 127.0.0.1
http.port: {node['port']}
transport.tcp.port: {node['transport_port']}

# 发现配置
discovery.seed_hosts: ["127.0.0.1:9300", "127.0.0.1:9301", "127.0.0.1:9302"]
cluster.initial_master_nodes: ["node-1"]

# 路径配置
path.data: {self.base_dir.absolute() / node['name'] / 'data'}
path.logs: {self.base_dir.absolute() / node['name'] / 'logs'}

# 内存配置
bootstrap.memory_lock: false

# 安全配置（开发环境）
xpack.security.enabled: false
xpack.monitoring.collection.enabled: false

# 性能配置
indices.query.bool.max_clause_count: 10000
search.max_buckets: 65536

# 分片配置
cluster.max_shards_per_node: 3000
"""
        return config
    
    def create_startup_scripts(self):
        """创建启动脚本"""
        logger.info("创建启动脚本...")
        
        es_home = self.base_dir / f"elasticsearch-{self.es_version}"
        
        # 创建单节点启动脚本
        for node in self.nodes:
            script_content = f"""@echo off
echo 启动Elasticsearch节点: {node['name']}
cd /d "{es_home.absolute()}"
set ES_PATH_CONF={self.base_dir.absolute() / node['name']}
bin\\elasticsearch.bat
pause
"""
            script_file = self.base_dir / f"start_{node['name']}.bat"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
        
        # 创建集群启动脚本
        cluster_script = """@echo off
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
"""
        
        cluster_script_file = self.base_dir / "start_cluster.bat"
        with open(cluster_script_file, 'w', encoding='utf-8') as f:
            f.write(cluster_script)
        
        # 创建停止脚本
        stop_script = """@echo off
echo 停止Elasticsearch集群...
taskkill /f /im java.exe /fi "WINDOWTITLE eq ES-*"
echo 集群已停止
pause
"""
        
        stop_script_file = self.base_dir / "stop_cluster.bat"
        with open(stop_script_file, 'w', encoding='utf-8') as f:
            f.write(stop_script)
        
        logger.info("✅ 启动脚本创建完成")
        return True
    
    def install_ik_analyzer(self):
        """安装IK中文分词器"""
        logger.info("安装IK中文分词器...")
        
        es_home = self.base_dir / f"elasticsearch-{self.es_version}"
        plugins_dir = es_home / "plugins" / "ik"
        plugins_dir.mkdir(parents=True, exist_ok=True)
        
        # IK分词器下载URL
        ik_url = f"https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v{self.es_version}/elasticsearch-analysis-ik-{self.es_version}.zip"
        
        try:
            import urllib.request
            ik_archive = self.base_dir / f"elasticsearch-analysis-ik-{self.es_version}.zip"
            
            if not ik_archive.exists():
                logger.info(f"下载IK分词器: {ik_url}")
                urllib.request.urlretrieve(ik_url, ik_archive)
            
            # 解压到plugins目录
            import zipfile
            with zipfile.ZipFile(ik_archive, 'r') as zip_ref:
                zip_ref.extractall(plugins_dir)
            
            logger.info("✅ IK中文分词器安装完成")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ IK分词器安装失败: {e}")
            logger.info("可以手动安装IK分词器以支持中文搜索")
            return False
    
    def create_test_script(self):
        """创建测试脚本"""
        test_script = """@echo off
echo 测试Elasticsearch集群...
echo.

echo 1. 检查集群健康状态:
curl -X GET "localhost:9200/_cluster/health?pretty"
echo.

echo 2. 检查节点信息:
curl -X GET "localhost:9200/_nodes?pretty"
echo.

echo 3. 创建测试索引:
curl -X PUT "localhost:9200/test_index" -H "Content-Type: application/json" -d "{\\"settings\\": {\\"number_of_shards\\": 3, \\"number_of_replicas\\": 1}}"
echo.

echo 4. 检查索引状态:
curl -X GET "localhost:9200/_cat/indices?v"
echo.

echo 5. 删除测试索引:
curl -X DELETE "localhost:9200/test_index"
echo.

echo 测试完成！
pause
"""
        
        test_script_file = self.base_dir / "test_cluster.bat"
        with open(test_script_file, 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        logger.info("✅ 测试脚本创建完成")
    
    def create_readme(self):
        """创建说明文档"""
        readme_content = f"""# Elasticsearch分布式集群部署指南

## 集群配置
- 集群名称: {self.cluster_name}
- Elasticsearch版本: {self.es_version}
- 节点数量: 3个节点
- 分片配置: 3个主分片，1个副本分片

## 节点信息
"""
        for node in self.nodes:
            readme_content += f"- {node['name']}: HTTP端口 {node['port']}, 传输端口 {node['transport_port']}\n"
        
        readme_content += """
## 启动步骤
1. 运行 `start_cluster.bat` 启动整个集群
2. 等待所有节点启动完成（约30-60秒）
3. 运行 `test_cluster.bat` 测试集群状态

## 单节点启动
如果需要单独启动节点：
- 运行 `start_node-1.bat` 启动主节点
- 运行 `start_node-2.bat` 启动数据节点2
- 运行 `start_node-3.bat` 启动数据节点3

## 停止集群
运行 `stop_cluster.bat` 停止所有节点

## 访问地址
- 主节点: http://localhost:9200
- 节点2: http://localhost:9201
- 节点3: http://localhost:9202

## 集群管理
- 集群健康: GET /_cluster/health
- 节点信息: GET /_nodes
- 索引状态: GET /_cat/indices?v
- 分片信息: GET /_cat/shards?v

## 注意事项
1. 确保Java 8+已安装
2. 确保端口9200-9202和9300-9302未被占用
3. 首次启动可能需要较长时间
4. 如果启动失败，检查logs目录下的日志文件

## 数据迁移
使用Python脚本进行数据迁移：
```bash
python data_migration.py
```

## Django集成
在Django项目中添加Elasticsearch支持：
```python
from elasticsearch_integration.django_integration import get_elasticsearch_urls
```
"""
        
        readme_file = self.base_dir / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        logger.info("✅ 说明文档创建完成")
    
    def setup_complete(self):
        """完成安装"""
        logger.info("🎉 Elasticsearch分布式集群安装完成！")
        logger.info(f"📁 安装目录: {self.base_dir.absolute()}")
        logger.info("📋 下一步操作:")
        logger.info("   1. 进入elasticsearch_cluster目录")
        logger.info("   2. 运行start_cluster.bat启动集群")
        logger.info("   3. 运行test_cluster.bat测试集群")
        logger.info("   4. 运行Python数据迁移脚本")
        logger.info("🔗 访问地址: http://localhost:9200")

def main():
    """主函数"""
    setup = ElasticsearchSetup()
    
    logger.info("开始安装Elasticsearch分布式集群...")
    
    # 执行安装步骤
    steps = [
        ("下载Elasticsearch", setup.download_elasticsearch),
        ("解压Elasticsearch", setup.extract_elasticsearch),
        ("创建节点配置", setup.create_node_configs),
        ("创建启动脚本", setup.create_startup_scripts),
        ("安装IK分词器", setup.install_ik_analyzer),
        ("创建测试脚本", setup.create_test_script),
        ("创建说明文档", setup.create_readme)
    ]
    
    for step_name, step_func in steps:
        logger.info(f"执行步骤: {step_name}")
        if not step_func():
            logger.error(f"步骤失败: {step_name}")
            return False
    
    setup.setup_complete()
    return True

if __name__ == '__main__':
    main()
