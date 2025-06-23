# -*- coding: utf-8 -*-
"""
MongoDB模型定义
使用MongoEngine替代Django ORM
"""

import mongoengine as me
from datetime import datetime
from mongoengine import fields

# 连接MongoDB - 无认证配置（修复版本）
try:
    # 先断开现有连接
    me.disconnect()
except:
    pass

# MongoDB连接配置 - 容错模式
MONGODB_CONNECTION_SUCCESS = False

def safe_mongodb_connect():
    """安全的MongoDB连接函数"""
    global MONGODB_CONNECTION_SUCCESS

    connection_attempts = [
        # 方案1：尝试无认证连接
        {
            'params': {
                'db': 'house_data',
                'host': '127.0.0.1',
                'port': 27017,
                'maxPoolSize': 10,
                'serverSelectionTimeoutMS': 3000,
                'connectTimeoutMS': 5000,
                'socketTimeoutMS': 10000
            },
            'name': '无认证连接'
        },
        # 方案2：尝试常见的管理员认证
        {
            'params': {
                'db': 'house_data',
                'host': '127.0.0.1',
                'port': 27017,
                'username': 'admin',
                'password': 'admin123',
                'authentication_source': 'admin',
                'maxPoolSize': 10,
                'serverSelectionTimeoutMS': 3000,
                'connectTimeoutMS': 5000,
                'socketTimeoutMS': 10000
            },
            'name': '管理员认证连接'
        }
    ]

    for attempt in connection_attempts:
        try:
            me.disconnect()
            me.connect(**attempt['params'])
            # 测试连接和数据操作
            me.connection.get_db().command('ping')

            # 测试实际的数据操作（这是关键）
            test_collection = me.connection.get_db().test_collection
            test_collection.find_one()  # 尝试查询操作

            print(f"✅ MongoDB {attempt['name']} 成功")
            MONGODB_CONNECTION_SUCCESS = True
            return True
        except Exception as e:
            print(f"❌ {attempt['name']} 失败: {e}")
            continue

    print("❌ 所有MongoDB连接方式都失败，将使用降级模式")
    MONGODB_CONNECTION_SUCCESS = False
    return False

# 尝试连接
safe_mongodb_connect()

class MongoUser(me.Document):
    """MongoDB用户模型"""

    username = fields.StringField(max_length=150, required=True, unique=True)
    password = fields.StringField(max_length=128, required=True)
    phone = fields.StringField(max_length=20)
    email = fields.EmailField()
    avatar = fields.StringField(max_length=500)  # 存储头像路径
    time = fields.DateTimeField(default=datetime.now)

    meta = {
        'collection': 'users',
        'indexes': [
            'username',
            'email',
            'time'
        ]
    }

    def __str__(self):
        return self.username

class MongoHistory(me.Document):
    """MongoDB收藏历史模型"""

    user = fields.ReferenceField(MongoUser, required=True)
    house = fields.ReferenceField('HouseDocument', required=True)  # 引用房源文档
    collected_time = fields.DateTimeField(default=datetime.now)

    meta = {
        'collection': 'history',
        'indexes': [
            'user',
            'house',
            'collected_time',
            ('user', 'house')  # 复合索引，防止重复收藏
        ]
    }

    def __str__(self):
        return f"{self.user.username} - {self.house.title}"

# 重新导入已有的房源模型
from mongodb_integration.models.mongo_models import HouseDocument

class MongoStats(me.Document):
    """MongoDB统计缓存模型"""

    stat_type = fields.StringField(max_length=50, required=True)  # 统计类型
    stat_key = fields.StringField(max_length=100)  # 统计键
    stat_value = fields.DynamicField()  # 动态字段，可存储任意类型
    created_time = fields.DateTimeField(default=datetime.now)
    updated_time = fields.DateTimeField(default=datetime.now)

    meta = {
        'collection': 'stats_cache',
        'indexes': [
            'stat_type',
            ('stat_type', 'stat_key'),
            'updated_time'
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_time = datetime.now()
        return super().save(*args, **kwargs)

# 数据迁移工具类
class DataMigrator:
    """数据迁移工具"""

    @staticmethod
    def migrate_users_from_mysql():
        """从MySQL迁移用户数据到MongoDB"""
        import pymysql

        # 连接MySQL
        mysql_conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='guangzhou_house',
            charset='utf8mb4'
        )

        cursor = mysql_conn.cursor()
        cursor.execute("SELECT username, password, phone, email, avatar, time FROM user")

        migrated_count = 0

        for row in cursor.fetchall():
            try:
                # 检查是否已存在
                if not MongoUser.objects(username=row[0]).first():
                    mongo_user = MongoUser(
                        username=row[0],
                        password=row[1],
                        phone=row[2] or '',
                        email=row[3] or '',
                        avatar=row[4] or '',
                        time=row[5] or datetime.now()
                    )
                    mongo_user.save()
                    migrated_count += 1
            except Exception as e:
                print(f"迁移用户失败: {row[0]} - {e}")

        cursor.close()
        mysql_conn.close()

        return migrated_count

    @staticmethod
    def migrate_history_from_mysql():
        """从MySQL迁移收藏历史到MongoDB"""
        import pymysql

        # 连接MySQL
        mysql_conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='guangzhou_house',
            charset='utf8mb4'
        )

        cursor = mysql_conn.cursor()
        cursor.execute("""
            SELECT h.user_id, h.house_id, u.username, house.title
            FROM history h
            JOIN user u ON h.user_id = u.id
            JOIN house house ON h.house_id = house.id
        """)

        migrated_count = 0

        for row in cursor.fetchall():
            try:
                # 查找对应的MongoDB用户和房源
                mongo_user = MongoUser.objects(username=row[2]).first()  # row[2] 是 username
                mongo_house = HouseDocument.objects(title=row[3]).first()  # row[3] 是 house.title

                if mongo_user and mongo_house:
                    # 检查是否已存在
                    existing = MongoHistory.objects(user=mongo_user, house=mongo_house).first()
                    if not existing:
                        mongo_history = MongoHistory(
                            user=mongo_user,
                            house=mongo_house,
                            collected_time=datetime.now()  # 使用当前时间，因为原表没有时间字段
                        )
                        mongo_history.save()
                        migrated_count += 1
            except Exception as e:
                print(f"迁移收藏记录失败: {e}")

        cursor.close()
        mysql_conn.close()

        return migrated_count

# MongoDB查询工具类
class MongoQueryHelper:
    """MongoDB查询助手"""

    @staticmethod
    def get_house_stats():
        """获取房源统计信息"""
        from .cache_utils import cache_aggregation_result

        @cache_aggregation_result(timeout=600, key_prefix='house_stats')
        def _get_stats():
            pipeline = [
                {
                    '$group': {
                        '_id': None,
                        'total_count': {'$sum': 1},
                        'avg_price': {'$avg': '$price.monthly_rent'},
                        'max_price': {'$max': '$price.monthly_rent'},
                        'min_price': {'$min': '$price.monthly_rent'},
                        'avg_area': {'$avg': '$features.area'}  # 修正字段名
                    }
                }
            ]
            result = list(HouseDocument.objects.aggregate(pipeline))
            return result[0] if result else {}

        return _get_stats()

    @staticmethod
    def get_city_distribution():
        """获取城市分布统计"""
        from .cache_utils import cache_aggregation_result

        @cache_aggregation_result(timeout=600, key_prefix='city_dist')
        def _get_distribution():
            pipeline = [
                {
                    '$group': {
                        '_id': '$location.city',
                        'count': {'$sum': 1}
                    }
                },
                {
                    '$sort': {'count': -1}
                }
            ]
            return list(HouseDocument.objects.aggregate(pipeline))

        return _get_distribution()

    @staticmethod
    def get_type_distribution():
        """获取房型分布统计"""
        from .cache_utils import cache_aggregation_result

        @cache_aggregation_result(timeout=600, key_prefix='type_dist')
        def _get_distribution():
            pipeline = [
                {
                    '$group': {
                        '_id': '$rental_type',
                        'count': {'$sum': 1}
                    }
                },
                {
                    '$sort': {'count': -1}
                }
            ]
            return list(HouseDocument.objects.aggregate(pipeline))

        return _get_distribution()

    @staticmethod
    def get_price_range_distribution():
        """获取价格区间分布"""
        pipeline = [
            {
                '$bucket': {
                    'groupBy': '$price.monthly_rent',
                    'boundaries': [0, 1000, 2000, 3000, 4000, 5000, 10000],
                    'default': '5000+',
                    'output': {
                        'count': {'$sum': 1}
                    }
                }
            }
        ]

        return list(HouseDocument.objects.aggregate(pipeline))

    @staticmethod
    def search_houses(filters=None, page=1, page_size=20):
        """高级房源搜索 - 性能优化版本"""
        from .cache_utils import cache_query_result

        # 为搜索结果添加缓存（较短的缓存时间）
        cache_key = f"search_{hash(str(filters))}_{page}_{page_size}"

        # 对于显示全部数据的请求，不使用缓存以避免内存问题
        if page_size >= 1000:  # 大数据量请求不缓存
            def _search_with_cache():
                query = HouseDocument.objects
        else:
            @cache_query_result(timeout=180, key_prefix='search')  # 小数据量请求使用缓存
            def _search_with_cache():
                query = HouseDocument.objects

                # 只选择必要的字段以提高性能
                query = query.only(
                    'title', 'rental_type', 'location.city', 'location.street',
                    'location.building', 'price.monthly_rent', 'features.area',
                    'features.room_type', 'images'
                )

                if filters:
                    # 城市筛选
                    if filters.get('city'):
                        query = query.filter(location__city=filters['city'])

                    # 房型筛选
                    if filters.get('rental_type'):
                        query = query.filter(rental_type=filters['rental_type'])

                    # 价格范围筛选
                    if filters.get('min_price'):
                        query = query.filter(price__monthly_rent__gte=filters['min_price'])
                    if filters.get('max_price'):
                        query = query.filter(price__monthly_rent__lte=filters['max_price'])

                    # 面积范围筛选 - 修正字段名
                    if filters.get('min_area'):
                        query = query.filter(features__area__gte=filters['min_area'])
                    if filters.get('max_area'):
                        query = query.filter(features__area__lte=filters['max_area'])

                    # 关键词搜索
                    if filters.get('keyword'):
                        query = query.filter(title__icontains=filters['keyword'])

                # 优化分页查询
                offset = (page - 1) * page_size

                # 使用聚合查询获取总数（更高效）
                total_pipeline = [
                    {'$match': query._query if hasattr(query, '_query') else {}},
                    {'$count': 'total'}
                ]
                total_result = list(HouseDocument.objects.aggregate(total_pipeline))
                total = total_result[0]['total'] if total_result else 0

                # 获取分页数据 - 处理显示全部的情况
                if page_size >= total:
                    # 显示全部数据，不使用分页
                    houses = list(query)
                else:
                    # 正常分页
                    houses = list(query.skip(offset).limit(page_size))

                return {
                    'houses': houses,
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total + page_size - 1) // page_size
                }

        return _search_with_cache()

# 性能监控工具
class PerformanceMonitor:
    """性能监控工具"""

    @staticmethod
    def compare_query_performance(query_func, *args, **kwargs):
        """比较查询性能"""
        import time

        start_time = time.time()
        result = query_func(*args, **kwargs)
        end_time = time.time()

        return {
            'result': result,
            'execution_time': end_time - start_time,
            'query_type': 'MongoDB'
        }
