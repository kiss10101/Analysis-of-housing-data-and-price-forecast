# -*- coding: utf-8 -*-
"""
性能监控中间件
监控请求响应时间和数据库查询性能
"""

import time
import logging
from django.conf import settings
from django.db import connection

logger = logging.getLogger(__name__)

class PerformanceMonitoringMiddleware:
    """性能监控中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录数据库查询开始状态
        initial_queries = len(connection.queries)
        
        # 处理请求
        response = self.get_response(request)
        
        # 计算响应时间
        end_time = time.time()
        response_time = end_time - start_time
        
        # 计算数据库查询数量
        db_queries = len(connection.queries) - initial_queries
        
        # 添加性能头信息
        response['X-Response-Time'] = f'{response_time:.3f}s'
        response['X-DB-Queries'] = str(db_queries)
        
        # 记录慢请求
        if response_time > 1.0:  # 超过1秒的请求
            logger.warning(
                f'Slow request: {request.method} {request.path} '
                f'took {response_time:.3f}s with {db_queries} DB queries'
            )
        
        # 在开发模式下添加调试信息
        if settings.DEBUG:
            print(f'🚀 {request.method} {request.path} - {response_time:.3f}s - {db_queries} queries')
        
        return response

class CacheControlMiddleware:
    """缓存控制中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # 为静态资源添加缓存头
        if request.path.startswith('/static/'):
            response['Cache-Control'] = 'public, max-age=31536000'  # 1年
            response['Expires'] = 'Thu, 31 Dec 2025 23:59:59 GMT'
        
        # 为API响应添加适当的缓存头
        elif request.path.startswith('/mongo/'):
            if request.method == 'GET':
                response['Cache-Control'] = 'public, max-age=300'  # 5分钟
            else:
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        
        return response

class CompressionMiddleware:
    """响应压缩中间件（简化版）"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # 添加压缩提示头
        if 'gzip' in request.META.get('HTTP_ACCEPT_ENCODING', ''):
            response['Vary'] = 'Accept-Encoding'
        
        return response
