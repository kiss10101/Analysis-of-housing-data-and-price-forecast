# -*- coding: utf-8 -*-
"""
Django集成模块
将Elasticsearch分布式存储集成到Django应用中
"""

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import logging

from elasticsearch_service import get_search_service, get_data_service

logger = logging.getLogger(__name__)

class ElasticsearchDjangoViews:
    """Elasticsearch Django视图类"""
    
    @staticmethod
    @require_http_methods(["GET"])
    def search_houses_api(request):
        """房源搜索API"""
        try:
            # 获取查询参数
            query_params = {
                'keyword': request.GET.get('keyword', ''),
                'city': request.GET.get('city', ''),
                'district': request.GET.get('district', ''),
                'rental_type': request.GET.get('rental_type', ''),
                'min_price': request.GET.get('min_price'),
                'max_price': request.GET.get('max_price'),
                'min_area': request.GET.get('min_area'),
                'max_area': request.GET.get('max_area'),
                'tags': request.GET.getlist('tags'),
                'sort': request.GET.get('sort', 'relevance'),
                'from': int(request.GET.get('from', 0)),
                'size': int(request.GET.get('size', 20)),
                'include_aggregations': request.GET.get('include_aggs', 'true').lower() == 'true'
            }
            
            # 清理空值
            query_params = {k: v for k, v in query_params.items() if v not in [None, '', []]}
            
            # 类型转换
            for field in ['min_price', 'max_price']:
                if field in query_params:
                    try:
                        query_params[field] = int(query_params[field])
                    except (ValueError, TypeError):
                        del query_params[field]
            
            for field in ['min_area', 'max_area']:
                if field in query_params:
                    try:
                        query_params[field] = float(query_params[field])
                    except (ValueError, TypeError):
                        del query_params[field]
            
            # 执行搜索
            search_service = get_search_service()
            results = search_service.search_houses(query_params)
            
            return JsonResponse({
                'success': True,
                'data': results,
                'query_params': query_params
            })
            
        except Exception as e:
            logger.error(f"搜索API错误: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    @staticmethod
    @require_http_methods(["GET"])
    def get_house_detail_api(request, house_id):
        """获取房源详情API"""
        try:
            search_service = get_search_service()
            house_detail = search_service.get_house_by_id(house_id)
            
            if house_detail:
                return JsonResponse({
                    'success': True,
                    'data': house_detail
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': '房源不存在'
                }, status=404)
                
        except Exception as e:
            logger.error(f"获取房源详情错误: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    @staticmethod
    @require_http_methods(["GET"])
    def get_similar_houses_api(request, house_id):
        """获取相似房源API"""
        try:
            size = int(request.GET.get('size', 10))
            
            search_service = get_search_service()
            similar_houses = search_service.get_similar_houses(house_id, size)
            
            return JsonResponse({
                'success': True,
                'data': similar_houses,
                'count': len(similar_houses)
            })
            
        except Exception as e:
            logger.error(f"获取相似房源错误: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    @staticmethod
    @require_http_methods(["GET"])
    def market_analysis_api(request):
        """市场分析API"""
        try:
            city = request.GET.get('city')
            
            search_service = get_search_service()
            analysis_data = search_service.get_market_analysis(city)
            
            return JsonResponse({
                'success': True,
                'data': analysis_data,
                'city': city
            })
            
        except Exception as e:
            logger.error(f"市场分析错误: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    def add_house_api(request):
        """添加房源API"""
        try:
            house_data = json.loads(request.body)
            
            data_service = get_data_service()
            success = data_service.add_house(house_data)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': '房源添加成功'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': '房源添加失败'
                }, status=500)
                
        except Exception as e:
            logger.error(f"添加房源错误: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["PUT"])
    def update_house_api(request, house_id):
        """更新房源API"""
        try:
            update_data = json.loads(request.body)
            
            data_service = get_data_service()
            success = data_service.update_house(house_id, update_data)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': '房源更新成功'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': '房源更新失败'
                }, status=500)
                
        except Exception as e:
            logger.error(f"更新房源错误: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["DELETE"])
    def delete_house_api(request, house_id):
        """删除房源API"""
        try:
            data_service = get_data_service()
            success = data_service.delete_house(house_id)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': '房源删除成功'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': '房源删除失败'
                }, status=500)
                
        except Exception as e:
            logger.error(f"删除房源错误: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

# URL配置
def get_elasticsearch_urls():
    """获取Elasticsearch相关的URL配置"""
    from django.urls import path
    
    views = ElasticsearchDjangoViews
    
    return [
        path('api/es/search/', views.search_houses_api, name='es_search_houses'),
        path('api/es/house/<str:house_id>/', views.get_house_detail_api, name='es_house_detail'),
        path('api/es/house/<str:house_id>/similar/', views.get_similar_houses_api, name='es_similar_houses'),
        path('api/es/market-analysis/', views.market_analysis_api, name='es_market_analysis'),
        path('api/es/house/add/', views.add_house_api, name='es_add_house'),
        path('api/es/house/<str:house_id>/update/', views.update_house_api, name='es_update_house'),
        path('api/es/house/<str:house_id>/delete/', views.delete_house_api, name='es_delete_house'),
    ]

# Django管理命令
class ElasticsearchManagementCommands:
    """Elasticsearch管理命令"""
    
    @staticmethod
    def migrate_data_command():
        """数据迁移命令"""
        from data_migration import DataMigrator
        
        migrator = DataMigrator()
        success = migrator.migrate_data()
        
        if success:
            print("✅ 数据迁移完成")
            migrator.verify_migration()
        else:
            print("❌ 数据迁移失败")
    
    @staticmethod
    def create_index_command():
        """创建索引命令"""
        from elasticsearch_config import ElasticsearchManager
        
        manager = ElasticsearchManager()
        success = manager.create_index()
        
        if success:
            print("✅ 索引创建成功")
        else:
            print("❌ 索引创建失败")
    
    @staticmethod
    def delete_index_command():
        """删除索引命令"""
        from elasticsearch_config import ElasticsearchManager
        
        manager = ElasticsearchManager()
        success = manager.delete_index()
        
        if success:
            print("✅ 索引删除成功")
        else:
            print("❌ 索引删除失败")

# 中间件
class ElasticsearchMiddleware:
    """Elasticsearch中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 在请求处理前
        response = self.get_response(request)
        # 在请求处理后
        return response
    
    def process_exception(self, request, exception):
        """处理Elasticsearch相关异常"""
        if 'elasticsearch' in str(exception).lower():
            logger.error(f"Elasticsearch异常: {exception}")
        return None
