# -*- coding: utf-8 -*-
"""
Elasticsearch分布式存储配置
房源数据分析系统 - 大数据存储方案
"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElasticsearchConfig:
    """Elasticsearch配置类"""
    
    # 集群配置
    CLUSTER_NAME = "house-data-cluster"
    
    # 节点配置（模拟分布式集群）
    NODES = [
        {'host': 'localhost', 'port': 9200},  # 主节点
        {'host': 'localhost', 'port': 9201},  # 数据节点1
        {'host': 'localhost', 'port': 9202},  # 数据节点2
    ]
    
    # 索引配置
    INDEX_NAME = "house_data"
    INDEX_PATTERN = "house_data_*"
    
    # 分片配置
    SHARDS_CONFIG = {
        "number_of_shards": 3,      # 3个主分片
        "number_of_replicas": 1,    # 1个副本分片
        "refresh_interval": "1s",   # 实时刷新
        "max_result_window": 50000  # 最大查询结果数
    }
    
    # 映射配置
    MAPPING = {
        "properties": {
            "house_id": {
                "type": "keyword",
                "index": True
            },
            "title": {
                "type": "text",
                "analyzer": "ik_max_word",
                "search_analyzer": "ik_smart",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "rental_type": {
                "type": "keyword"
            },
            "location": {
                "properties": {
                    "city": {"type": "keyword"},
                    "district": {"type": "keyword"},
                    "street": {"type": "keyword"},
                    "building": {
                        "type": "text",
                        "analyzer": "ik_max_word",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "coordinates": {
                        "type": "geo_point"
                    },
                    "subway_info": {
                        "type": "text",
                        "analyzer": "ik_max_word"
                    }
                }
            },
            "price": {
                "properties": {
                    "monthly_rent": {"type": "integer"},
                    "deposit": {"type": "integer"},
                    "service_fee": {"type": "integer"},
                    "price_per_sqm": {"type": "float"}
                }
            },
            "features": {
                "properties": {
                    "area": {"type": "float"},
                    "room_type": {"type": "keyword"},
                    "direction": {"type": "keyword"},
                    "floor_info": {"type": "keyword"},
                    "decoration": {"type": "keyword"},
                    "facilities": {
                        "type": "text",
                        "analyzer": "ik_max_word"
                    }
                }
            },
            "tags": {
                "type": "keyword"
            },
            "images": {
                "type": "keyword",
                "index": False
            },
            "description": {
                "type": "text",
                "analyzer": "ik_max_word",
                "search_analyzer": "ik_smart"
            },
            "crawl_meta": {
                "properties": {
                    "source_url": {"type": "keyword", "index": False},
                    "crawl_time": {"type": "date"},
                    "update_time": {"type": "date"},
                    "data_source": {"type": "keyword"}
                }
            },
            "status": {
                "type": "keyword"
            },
            "created_at": {
                "type": "date"
            },
            "updated_at": {
                "type": "date"
            }
        }
    }

class ElasticsearchManager:
    """Elasticsearch管理器"""
    
    def __init__(self, config=None):
        self.config = config or ElasticsearchConfig()
        self.client = None
        self.connect()
    
    def connect(self):
        """连接Elasticsearch集群"""
        try:
            # 尝试连接集群
            self.client = Elasticsearch(
                self.config.NODES,
                # 连接配置
                timeout=30,
                max_retries=3,
                retry_on_timeout=True,
                # 集群配置
                sniff_on_start=True,
                sniff_on_connection_fail=True,
                sniffer_timeout=60,
                # 安全配置（如果需要）
                # http_auth=('username', 'password'),
                # use_ssl=True,
                # verify_certs=False,
            )
            
            # 测试连接
            if self.client.ping():
                logger.info("✅ Elasticsearch集群连接成功")
                self.log_cluster_info()
                return True
            else:
                logger.error("❌ Elasticsearch集群连接失败")
                return False
                
        except Exception as e:
            logger.error(f"❌ Elasticsearch连接异常: {e}")
            # 降级到单节点模式
            return self.connect_single_node()
    
    def connect_single_node(self):
        """降级到单节点模式"""
        try:
            self.client = Elasticsearch([{'host': 'localhost', 'port': 9200}])
            if self.client.ping():
                logger.info("✅ Elasticsearch单节点连接成功（降级模式）")
                return True
            else:
                logger.error("❌ Elasticsearch单节点连接失败")
                return False
        except Exception as e:
            logger.error(f"❌ Elasticsearch单节点连接异常: {e}")
            return False
    
    def log_cluster_info(self):
        """记录集群信息"""
        try:
            cluster_health = self.client.cluster.health()
            nodes_info = self.client.nodes.info()
            
            logger.info(f"集群名称: {cluster_health['cluster_name']}")
            logger.info(f"集群状态: {cluster_health['status']}")
            logger.info(f"节点数量: {cluster_health['number_of_nodes']}")
            logger.info(f"数据节点: {cluster_health['number_of_data_nodes']}")
            logger.info(f"活跃分片: {cluster_health['active_shards']}")
            
        except Exception as e:
            logger.warning(f"获取集群信息失败: {e}")
    
    def create_index(self, index_name=None):
        """创建索引"""
        index_name = index_name or self.config.INDEX_NAME
        
        try:
            if self.client.indices.exists(index=index_name):
                logger.info(f"索引 {index_name} 已存在")
                return True
            
            # 创建索引配置
            index_config = {
                "settings": {
                    "index": self.config.SHARDS_CONFIG,
                    "analysis": {
                        "analyzer": {
                            "ik_max_word": {
                                "type": "ik_max_word"
                            },
                            "ik_smart": {
                                "type": "ik_smart"
                            }
                        }
                    }
                },
                "mappings": self.config.MAPPING
            }
            
            # 创建索引
            response = self.client.indices.create(
                index=index_name,
                body=index_config
            )
            
            logger.info(f"✅ 索引 {index_name} 创建成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 创建索引失败: {e}")
            return False
    
    def delete_index(self, index_name=None):
        """删除索引"""
        index_name = index_name or self.config.INDEX_NAME
        
        try:
            if self.client.indices.exists(index=index_name):
                self.client.indices.delete(index=index_name)
                logger.info(f"✅ 索引 {index_name} 删除成功")
                return True
            else:
                logger.info(f"索引 {index_name} 不存在")
                return True
                
        except Exception as e:
            logger.error(f"❌ 删除索引失败: {e}")
            return False
    
    def get_index_info(self, index_name=None):
        """获取索引信息"""
        index_name = index_name or self.config.INDEX_NAME
        
        try:
            if not self.client.indices.exists(index=index_name):
                return None
            
            # 获取索引统计信息
            stats = self.client.indices.stats(index=index_name)
            settings = self.client.indices.get_settings(index=index_name)
            mapping = self.client.indices.get_mapping(index=index_name)
            
            return {
                'stats': stats,
                'settings': settings,
                'mapping': mapping
            }
            
        except Exception as e:
            logger.error(f"❌ 获取索引信息失败: {e}")
            return None

# 全局实例
es_manager = ElasticsearchManager()

def get_elasticsearch_client():
    """获取Elasticsearch客户端"""
    return es_manager.client

def test_elasticsearch_connection():
    """测试Elasticsearch连接"""
    try:
        client = get_elasticsearch_client()
        if client and client.ping():
            logger.info("✅ Elasticsearch连接测试成功")
            return True
        else:
            logger.error("❌ Elasticsearch连接测试失败")
            return False
    except Exception as e:
        logger.error(f"❌ Elasticsearch连接测试异常: {e}")
        return False

if __name__ == '__main__':
    # 测试连接
    test_elasticsearch_connection()
    
    # 创建索引
    es_manager.create_index()
    
    # 获取索引信息
    info = es_manager.get_index_info()
    if info:
        print("索引信息获取成功")
    else:
        print("索引信息获取失败")
