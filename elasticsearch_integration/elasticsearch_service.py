# -*- coding: utf-8 -*-
"""
Elasticsearch服务层
提供房源数据的分布式存储、检索和分析功能
"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional, Any

from elasticsearch_config import ElasticsearchManager, ElasticsearchConfig

logger = logging.getLogger(__name__)

class HouseSearchService:
    """房源搜索服务"""
    
    def __init__(self):
        self.es_manager = ElasticsearchManager()
        self.client = self.es_manager.client
        self.index_name = ElasticsearchConfig.INDEX_NAME
    
    def search_houses(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """高级房源搜索"""
        try:
            # 构建搜索查询
            search_body = self._build_search_query(query_params)
            
            # 执行搜索
            response = self.client.search(
                index=self.index_name,
                body=search_body
            )
            
            # 处理搜索结果
            return self._process_search_results(response)
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return {"error": str(e), "results": [], "total": 0}
    
    def _build_search_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """构建搜索查询"""
        query = {"bool": {"must": [], "filter": [], "should": []}}
        
        # 关键词搜索
        if params.get('keyword'):
            query["bool"]["must"].append({
                "multi_match": {
                    "query": params['keyword'],
                    "fields": [
                        "title^3",
                        "location.building^2",
                        "description",
                        "features.facilities"
                    ],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            })
        
        # 城市筛选
        if params.get('city'):
            query["bool"]["filter"].append({
                "term": {"location.city": params['city']}
            })
        
        # 区域筛选
        if params.get('district'):
            query["bool"]["filter"].append({
                "term": {"location.district": params['district']}
            })
        
        # 房源类型筛选
        if params.get('rental_type'):
            query["bool"]["filter"].append({
                "term": {"rental_type": params['rental_type']}
            })
        
        # 价格范围筛选
        if params.get('min_price') or params.get('max_price'):
            price_range = {}
            if params.get('min_price'):
                price_range['gte'] = params['min_price']
            if params.get('max_price'):
                price_range['lte'] = params['max_price']
            
            query["bool"]["filter"].append({
                "range": {"price.monthly_rent": price_range}
            })
        
        # 面积范围筛选
        if params.get('min_area') or params.get('max_area'):
            area_range = {}
            if params.get('min_area'):
                area_range['gte'] = params['min_area']
            if params.get('max_area'):
                area_range['lte'] = params['max_area']
            
            query["bool"]["filter"].append({
                "range": {"features.area": area_range}
            })
        
        # 地理位置搜索
        if params.get('lat') and params.get('lon') and params.get('distance'):
            query["bool"]["filter"].append({
                "geo_distance": {
                    "distance": f"{params['distance']}km",
                    "location.coordinates": {
                        "lat": params['lat'],
                        "lon": params['lon']
                    }
                }
            })
        
        # 标签筛选
        if params.get('tags'):
            for tag in params['tags']:
                query["bool"]["filter"].append({
                    "term": {"tags": tag}
                })
        
        # 构建完整查询体
        search_body = {
            "query": query,
            "from": params.get('from', 0),
            "size": params.get('size', 20),
            "sort": self._build_sort(params.get('sort', 'relevance')),
            "highlight": {
                "fields": {
                    "title": {},
                    "description": {}
                }
            }
        }
        
        # 添加聚合
        if params.get('include_aggregations', True):
            search_body["aggs"] = self._build_aggregations()
        
        return search_body
    
    def _build_sort(self, sort_type: str) -> List[Dict[str, Any]]:
        """构建排序"""
        sort_options = {
            'relevance': [{"_score": {"order": "desc"}}],
            'price_asc': [{"price.monthly_rent": {"order": "asc"}}],
            'price_desc': [{"price.monthly_rent": {"order": "desc"}}],
            'area_asc': [{"features.area": {"order": "asc"}}],
            'area_desc': [{"features.area": {"order": "desc"}}],
            'time_desc': [{"created_at": {"order": "desc"}}],
            'time_asc': [{"created_at": {"order": "asc"}}]
        }
        
        return sort_options.get(sort_type, sort_options['relevance'])
    
    def _build_aggregations(self) -> Dict[str, Any]:
        """构建聚合查询"""
        return {
            "city_stats": {
                "terms": {
                    "field": "location.city",
                    "size": 20
                },
                "aggs": {
                    "avg_price": {
                        "avg": {"field": "price.monthly_rent"}
                    }
                }
            },
            "district_stats": {
                "terms": {
                    "field": "location.district",
                    "size": 50
                }
            },
            "rental_type_stats": {
                "terms": {
                    "field": "rental_type",
                    "size": 10
                }
            },
            "price_histogram": {
                "histogram": {
                    "field": "price.monthly_rent",
                    "interval": 500,
                    "min_doc_count": 1
                }
            },
            "area_histogram": {
                "histogram": {
                    "field": "features.area",
                    "interval": 10,
                    "min_doc_count": 1
                }
            },
            "price_stats": {
                "stats": {"field": "price.monthly_rent"}
            },
            "area_stats": {
                "stats": {"field": "features.area"}
            }
        }
    
    def _process_search_results(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """处理搜索结果"""
        hits = response.get('hits', {})
        aggregations = response.get('aggregations', {})
        
        # 处理文档结果
        results = []
        for hit in hits.get('hits', []):
            source = hit['_source']
            result = {
                'id': hit['_id'],
                'score': hit['_score'],
                'source': source
            }
            
            # 添加高亮
            if 'highlight' in hit:
                result['highlight'] = hit['highlight']
            
            results.append(result)
        
        return {
            'total': hits.get('total', {}).get('value', 0),
            'max_score': hits.get('max_score', 0),
            'results': results,
            'aggregations': aggregations,
            'took': response.get('took', 0)
        }
    
    def get_house_by_id(self, house_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取房源详情"""
        try:
            response = self.client.get(
                index=self.index_name,
                id=house_id
            )
            return response['_source']
        except Exception as e:
            logger.error(f"获取房源详情失败: {e}")
            return None
    
    def get_similar_houses(self, house_id: str, size: int = 10) -> List[Dict[str, Any]]:
        """获取相似房源"""
        try:
            # 先获取目标房源
            target_house = self.get_house_by_id(house_id)
            if not target_house:
                return []
            
            # 构建相似性查询
            search_body = {
                "query": {
                    "more_like_this": {
                        "fields": ["title", "description", "location.building"],
                        "like": [
                            {
                                "_index": self.index_name,
                                "_id": house_id
                            }
                        ],
                        "min_term_freq": 1,
                        "max_query_terms": 12
                    }
                },
                "size": size
            }
            
            response = self.client.search(
                index=self.index_name,
                body=search_body
            )
            
            return [hit['_source'] for hit in response['hits']['hits']]
            
        except Exception as e:
            logger.error(f"获取相似房源失败: {e}")
            return []
    
    def get_market_analysis(self, city: str = None) -> Dict[str, Any]:
        """市场分析"""
        try:
            query = {"match_all": {}}
            if city:
                query = {"term": {"location.city": city}}
            
            search_body = {
                "query": query,
                "size": 0,
                "aggs": {
                    "price_trends": {
                        "date_histogram": {
                            "field": "created_at",
                            "calendar_interval": "month",
                            "format": "yyyy-MM"
                        },
                        "aggs": {
                            "avg_price": {"avg": {"field": "price.monthly_rent"}},
                            "house_count": {"value_count": {"field": "house_id"}}
                        }
                    },
                    "district_analysis": {
                        "terms": {
                            "field": "location.district",
                            "size": 20
                        },
                        "aggs": {
                            "avg_price": {"avg": {"field": "price.monthly_rent"}},
                            "avg_area": {"avg": {"field": "features.area"}},
                            "price_per_sqm": {
                                "avg": {"field": "price.price_per_sqm"}
                            }
                        }
                    },
                    "rental_type_analysis": {
                        "terms": {"field": "rental_type"},
                        "aggs": {
                            "avg_price": {"avg": {"field": "price.monthly_rent"}},
                            "count": {"value_count": {"field": "house_id"}}
                        }
                    }
                }
            }
            
            response = self.client.search(
                index=self.index_name,
                body=search_body
            )
            
            return response.get('aggregations', {})
            
        except Exception as e:
            logger.error(f"市场分析失败: {e}")
            return {}

class HouseDataService:
    """房源数据服务"""
    
    def __init__(self):
        self.es_manager = ElasticsearchManager()
        self.client = self.es_manager.client
        self.index_name = ElasticsearchConfig.INDEX_NAME
    
    def add_house(self, house_data: Dict[str, Any]) -> bool:
        """添加房源"""
        try:
            house_data['created_at'] = datetime.now()
            house_data['updated_at'] = datetime.now()
            
            response = self.client.index(
                index=self.index_name,
                id=house_data.get('house_id'),
                body=house_data
            )
            
            logger.info(f"房源添加成功: {response['_id']}")
            return True
            
        except Exception as e:
            logger.error(f"添加房源失败: {e}")
            return False
    
    def update_house(self, house_id: str, update_data: Dict[str, Any]) -> bool:
        """更新房源"""
        try:
            update_data['updated_at'] = datetime.now()
            
            response = self.client.update(
                index=self.index_name,
                id=house_id,
                body={"doc": update_data}
            )
            
            logger.info(f"房源更新成功: {house_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新房源失败: {e}")
            return False
    
    def delete_house(self, house_id: str) -> bool:
        """删除房源"""
        try:
            response = self.client.delete(
                index=self.index_name,
                id=house_id
            )
            
            logger.info(f"房源删除成功: {house_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除房源失败: {e}")
            return False
    
    def bulk_add_houses(self, houses_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """批量添加房源"""
        try:
            actions = []
            for house_data in houses_data:
                house_data['created_at'] = datetime.now()
                house_data['updated_at'] = datetime.now()
                
                action = {
                    '_index': self.index_name,
                    '_id': house_data.get('house_id'),
                    '_source': house_data
                }
                actions.append(action)
            
            success, failed = bulk(self.client, actions)
            
            logger.info(f"批量添加完成 - 成功: {success}, 失败: {len(failed)}")
            return {"success": success, "failed": len(failed)}
            
        except Exception as e:
            logger.error(f"批量添加失败: {e}")
            return {"success": 0, "failed": len(houses_data)}

# 全局服务实例
search_service = None
data_service = None

def get_search_service():
    """获取搜索服务"""
    global search_service
    if search_service is None:
        search_service = HouseSearchService()
    return search_service

def get_data_service():
    """获取数据服务"""
    global data_service
    if data_service is None:
        data_service = HouseDataService()
    return data_service

def test_elasticsearch_services():
    """测试Elasticsearch服务"""
    try:
        # 测试搜索服务
        search_svc = get_search_service()
        test_query = {
            'keyword': '广州',
            'size': 5
        }
        results = search_svc.search_houses(test_query)
        logger.info(f"搜索测试成功，返回 {len(results.get('results', []))} 条结果")

        # 测试数据服务
        data_svc = get_data_service()
        test_house = {
            'house_id': 'test_' + str(int(datetime.now().timestamp())),
            'title': '测试房源',
            'rental_type': '整租',
            'location': {
                'city': '广州',
                'district': '天河区'
            },
            'price': {
                'monthly_rent': 3000
            }
        }

        if data_svc.add_house(test_house):
            logger.info("数据服务测试成功")
            # 清理测试数据
            data_svc.delete_house(test_house['house_id'])

        return True

    except Exception as e:
        logger.error(f"服务测试失败: {e}")
        return False

if __name__ == '__main__':
    test_elasticsearch_services()
