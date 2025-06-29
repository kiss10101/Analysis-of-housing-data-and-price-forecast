# -*- coding: utf-8 -*-
"""
数据迁移工具
从MongoDB迁移数据到Elasticsearch分布式存储
"""

import pymongo
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, parallel_bulk
import json
from datetime import datetime
import logging
from tqdm import tqdm
import time

from elasticsearch_config import ElasticsearchManager, ElasticsearchConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataMigrator:
    """数据迁移器"""
    
    def __init__(self):
        self.es_manager = ElasticsearchManager()
        self.mongo_client = None
        self.mongo_db = None
        self.mongo_collection = None
        self.setup_mongodb()
    
    def setup_mongodb(self):
        """设置MongoDB连接"""
        try:
            self.mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
            self.mongo_db = self.mongo_client['house_data']
            self.mongo_collection = self.mongo_db['houses']
            logger.info("✅ MongoDB连接成功")
        except Exception as e:
            logger.error(f"❌ MongoDB连接失败: {e}")
    
    def transform_document(self, mongo_doc):
        """转换MongoDB文档为Elasticsearch文档"""
        try:
            # 基础字段映射
            es_doc = {
                'house_id': str(mongo_doc.get('_id', '')),
                'title': mongo_doc.get('title', ''),
                'rental_type': mongo_doc.get('rental_type', ''),
                'status': mongo_doc.get('status', 'available'),
                'created_at': mongo_doc.get('created_at', datetime.now()),
                'updated_at': mongo_doc.get('updated_at', datetime.now())
            }
            
            # 位置信息
            location = mongo_doc.get('location', {})
            es_doc['location'] = {
                'city': location.get('city', ''),
                'district': location.get('district', ''),
                'street': location.get('street', ''),
                'building': location.get('building', ''),
                'subway_info': location.get('subway_info', '')
            }
            
            # 处理地理坐标
            coordinates = location.get('coordinates', [])
            if coordinates and len(coordinates) == 2:
                es_doc['location']['coordinates'] = {
                    'lat': coordinates[1],
                    'lon': coordinates[0]
                }
            
            # 价格信息
            price = mongo_doc.get('price', {})
            if isinstance(price, dict):
                es_doc['price'] = {
                    'monthly_rent': price.get('monthly_rent', 0),
                    'deposit': price.get('deposit', 0),
                    'service_fee': price.get('service_fee', 0),
                    'price_per_sqm': price.get('price_per_sqm', 0.0)
                }
            else:
                # 兼容旧格式
                es_doc['price'] = {
                    'monthly_rent': int(price) if price else 0,
                    'deposit': 0,
                    'service_fee': 0,
                    'price_per_sqm': 0.0
                }
            
            # 房源特征
            features = mongo_doc.get('features', {})
            es_doc['features'] = {
                'area': features.get('area', 0.0),
                'room_type': features.get('room_type', ''),
                'direction': features.get('direction', ''),
                'floor_info': features.get('floor_info', ''),
                'decoration': features.get('decoration', ''),
                'facilities': features.get('facilities', '')
            }
            
            # 标签和图片
            es_doc['tags'] = mongo_doc.get('tags', [])
            es_doc['images'] = mongo_doc.get('images', [])
            es_doc['description'] = mongo_doc.get('description', '')
            
            # 爬虫元数据
            crawl_meta = mongo_doc.get('crawl_meta', {})
            es_doc['crawl_meta'] = {
                'source_url': crawl_meta.get('source_url', ''),
                'crawl_time': crawl_meta.get('crawl_time', datetime.now()),
                'update_time': crawl_meta.get('update_time', datetime.now()),
                'data_source': crawl_meta.get('data_source', 'lianjia')
            }
            
            return es_doc
            
        except Exception as e:
            logger.error(f"文档转换失败: {e}")
            return None
    
    def generate_documents(self, batch_size=1000):
        """生成文档批次"""
        try:
            total_docs = self.mongo_collection.count_documents({})
            logger.info(f"开始迁移 {total_docs} 条文档")
            
            # 分批处理
            skip = 0
            while skip < total_docs:
                cursor = self.mongo_collection.find().skip(skip).limit(batch_size)
                batch_docs = []
                
                for mongo_doc in cursor:
                    es_doc = self.transform_document(mongo_doc)
                    if es_doc:
                        # 构造Elasticsearch批量操作格式
                        action = {
                            '_index': ElasticsearchConfig.INDEX_NAME,
                            '_id': es_doc['house_id'],
                            '_source': es_doc
                        }
                        batch_docs.append(action)
                
                if batch_docs:
                    yield batch_docs
                
                skip += batch_size
                
        except Exception as e:
            logger.error(f"生成文档批次失败: {e}")
    
    def migrate_data(self, batch_size=1000, parallel=True):
        """迁移数据"""
        try:
            # 确保索引存在
            if not self.es_manager.create_index():
                logger.error("创建索引失败，停止迁移")
                return False
            
            client = self.es_manager.client
            if not client:
                logger.error("Elasticsearch客户端未连接")
                return False
            
            total_docs = self.mongo_collection.count_documents({})
            success_count = 0
            error_count = 0
            
            logger.info(f"开始迁移 {total_docs} 条文档到Elasticsearch")
            
            # 使用进度条
            with tqdm(total=total_docs, desc="迁移进度") as pbar:
                if parallel:
                    # 并行批量写入
                    for success, info in parallel_bulk(
                        client,
                        self.generate_documents(batch_size),
                        chunk_size=batch_size,
                        max_chunk_bytes=10*1024*1024,  # 10MB
                        thread_count=4,
                        queue_size=8
                    ):
                        if success:
                            success_count += len(info)
                        else:
                            error_count += 1
                            logger.error(f"批量写入失败: {info}")
                        
                        pbar.update(len(info) if success else 1)
                else:
                    # 串行批量写入
                    for batch_docs in self.generate_documents(batch_size):
                        try:
                            response = bulk(client, batch_docs)
                            success_count += response[0]
                            if response[1]:
                                error_count += len(response[1])
                                for error in response[1]:
                                    logger.error(f"文档写入失败: {error}")
                            
                            pbar.update(len(batch_docs))
                            
                        except Exception as e:
                            logger.error(f"批量写入异常: {e}")
                            error_count += len(batch_docs)
                            pbar.update(len(batch_docs))
            
            # 刷新索引
            client.indices.refresh(index=ElasticsearchConfig.INDEX_NAME)
            
            logger.info(f"✅ 数据迁移完成")
            logger.info(f"成功: {success_count} 条")
            logger.info(f"失败: {error_count} 条")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据迁移失败: {e}")
            return False
    
    def verify_migration(self):
        """验证迁移结果"""
        try:
            client = self.es_manager.client
            if not client:
                return False
            
            # 获取Elasticsearch文档数量
            es_count = client.count(index=ElasticsearchConfig.INDEX_NAME)['count']
            
            # 获取MongoDB文档数量
            mongo_count = self.mongo_collection.count_documents({})
            
            logger.info(f"MongoDB文档数: {mongo_count}")
            logger.info(f"Elasticsearch文档数: {es_count}")
            
            if es_count == mongo_count:
                logger.info("✅ 数据迁移验证成功")
                return True
            else:
                logger.warning(f"⚠️ 数据数量不匹配，差异: {abs(es_count - mongo_count)}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 迁移验证失败: {e}")
            return False
    
    def sample_search_test(self):
        """样本搜索测试"""
        try:
            client = self.es_manager.client
            if not client:
                return False
            
            # 测试基本搜索
            search_body = {
                "query": {
                    "match_all": {}
                },
                "size": 5
            }
            
            response = client.search(
                index=ElasticsearchConfig.INDEX_NAME,
                body=search_body
            )
            
            logger.info(f"搜索测试成功，返回 {len(response['hits']['hits'])} 条结果")
            
            # 测试聚合查询
            agg_body = {
                "size": 0,
                "aggs": {
                    "city_distribution": {
                        "terms": {
                            "field": "location.city",
                            "size": 10
                        }
                    },
                    "price_stats": {
                        "stats": {
                            "field": "price.monthly_rent"
                        }
                    }
                }
            }
            
            agg_response = client.search(
                index=ElasticsearchConfig.INDEX_NAME,
                body=agg_body
            )
            
            logger.info("聚合查询测试成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 搜索测试失败: {e}")
            return False

def main():
    """主函数"""
    migrator = DataMigrator()
    
    # 执行迁移
    if migrator.migrate_data(batch_size=500, parallel=True):
        # 验证迁移
        migrator.verify_migration()
        
        # 搜索测试
        migrator.sample_search_test()
    else:
        logger.error("数据迁移失败")

if __name__ == '__main__':
    main()
