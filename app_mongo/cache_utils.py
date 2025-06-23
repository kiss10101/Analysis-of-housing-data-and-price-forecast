# -*- coding: utf-8 -*-
"""
缓存工具模块
提供查询结果缓存功能
"""

from django.core.cache import cache
from django.views.decorators.cache import cache_page
from functools import wraps
import hashlib
import json
import time

def cache_query_result(timeout=300, key_prefix='query'):
    """
    查询结果缓存装饰器
    
    Args:
        timeout: 缓存超时时间（秒）
        key_prefix: 缓存键前缀
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key_data = {
                'func_name': func.__name__,
                'args': str(args),
                'kwargs': str(sorted(kwargs.items()))
            }
            cache_key_str = json.dumps(cache_key_data, sort_keys=True)
            cache_key = f"{key_prefix}:{hashlib.md5(cache_key_str.encode()).hexdigest()}"
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行查询
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # 存储到缓存
            cache.set(cache_key, result, timeout)
            
            # 记录性能信息
            if execution_time > 0.1:  # 超过100ms的查询记录日志
                print(f"Slow query cached: {func.__name__} took {execution_time:.3f}s")
            
            return result
        return wrapper
    return decorator

def cache_aggregation_result(timeout=600, key_prefix='agg'):
    """
    聚合查询结果缓存装饰器（更长的缓存时间）
    """
    return cache_query_result(timeout=timeout, key_prefix=key_prefix)

def clear_cache_by_pattern(pattern):
    """
    根据模式清除缓存
    """
    try:
        # 注意：这个功能在生产环境中需要Redis等支持模式匹配的缓存后端
        # 当前使用的LocMemCache不支持模式匹配，这里只是示例
        cache.clear()  # 简单清除所有缓存
        return True
    except Exception as e:
        print(f"清除缓存失败: {e}")
        return False

class CacheManager:
    """缓存管理器"""
    
    @staticmethod
    def get_cache_stats():
        """获取缓存统计信息"""
        try:
            # 这里可以添加缓存统计逻辑
            return {
                'cache_backend': 'LocMemCache',
                'status': 'active'
            }
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }
    
    @staticmethod
    def warm_up_cache():
        """预热缓存"""
        try:
            from app_mongo.models import MongoQueryHelper
            
            # 预热常用查询
            print("开始缓存预热...")
            
            # 预热房源统计
            MongoQueryHelper.get_house_stats()
            print("✅ 房源统计缓存预热完成")
            
            # 预热城市分布
            MongoQueryHelper.get_city_distribution()
            print("✅ 城市分布缓存预热完成")
            
            # 预热房型分布
            MongoQueryHelper.get_type_distribution()
            print("✅ 房型分布缓存预热完成")
            
            print("🎉 缓存预热完成")
            return True
            
        except Exception as e:
            print(f"❌ 缓存预热失败: {e}")
            return False
