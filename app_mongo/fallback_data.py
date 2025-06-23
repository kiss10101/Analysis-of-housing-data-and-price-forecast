# -*- coding: utf-8 -*-
"""
MongoDB连接失败时的降级数据
提供基本的演示功能
"""

from datetime import datetime

# 模拟用户数据
FALLBACK_USERS = [
    {
        'username': 'admin',
        'password': 'admin123',
        'phone': '13800138000',
        'email': 'admin@test.com',
        'avatar': '',
        'time': datetime.now()
    },
    {
        'username': 'test',
        'password': '123456',
        'phone': '13800138001',
        'email': 'test@test.com',
        'avatar': '',
        'time': datetime.now()
    },
    {
        'username': 'demo',
        'password': 'demo123',
        'phone': '13800138002',
        'email': 'demo@test.com',
        'avatar': '',
        'time': datetime.now()
    }
]

# 模拟房源数据
FALLBACK_HOUSES = [
    {
        '_id': '1',
        'title': '天河区精装修两房 - 地铁直达',
        'rental_type': '整租',
        'city': '广州',
        'district': '天河区',
        'street': '体育西路',
        'building': '天河大厦',
        'price': 4500.0,
        'area': 85.0,
        'room_type': '2室1厅',
        'floor': '15/25',
        'orientation': '南北',
        'description': '精装修，家电齐全，地铁3号线体育西路站',
        'crawl_time': datetime.now()
    },
    {
        '_id': '2',
        'title': '越秀区地铁房 - 单间出租',
        'rental_type': '合租',
        'city': '广州',
        'district': '越秀区',
        'street': '中山路',
        'building': '中山大厦',
        'price': 1800.0,
        'area': 25.0,
        'room_type': '1室0厅',
        'floor': '8/20',
        'orientation': '南',
        'description': '地铁1号线公园前站，交通便利',
        'crawl_time': datetime.now()
    },
    {
        '_id': '3',
        'title': '海珠区江景房 - 三房两厅',
        'rental_type': '整租',
        'city': '广州',
        'district': '海珠区',
        'street': '滨江路',
        'building': '江景花园',
        'price': 6800.0,
        'area': 120.0,
        'room_type': '3室2厅',
        'floor': '20/30',
        'orientation': '南',
        'description': '珠江江景，高层视野开阔',
        'crawl_time': datetime.now()
    },
    {
        '_id': '4',
        'title': '番禺区大学城 - 学生公寓',
        'rental_type': '合租',
        'city': '广州',
        'district': '番禺区',
        'street': '大学城路',
        'building': '学生公寓',
        'price': 1200.0,
        'area': 20.0,
        'room_type': '1室0厅',
        'floor': '5/10',
        'orientation': '东',
        'description': '适合学生，价格实惠',
        'crawl_time': datetime.now()
    },
    {
        '_id': '5',
        'title': '白云区新装修 - 两房一厅',
        'rental_type': '整租',
        'city': '广州',
        'district': '白云区',
        'street': '机场路',
        'building': '白云新城',
        'price': 3200.0,
        'area': 75.0,
        'room_type': '2室1厅',
        'floor': '12/18',
        'orientation': '南北',
        'description': '新装修，近地铁站',
        'crawl_time': datetime.now()
    }
]

class FallbackUser:
    """模拟用户类"""
    def __init__(self, data):
        self.username = data['username']
        self.password = data['password']
        self.phone = data['phone']
        self.email = data['email']
        self.avatar = data['avatar']
        self.time = data['time']

class FallbackQuerySet:
    """模拟查询集"""
    def __init__(self, data):
        self.data = data
    
    def filter(self, **kwargs):
        filtered_data = []
        for item in self.data:
            match = True
            for key, value in kwargs.items():
                if key in item and item[key] != value:
                    match = False
                    break
            if match:
                filtered_data.append(item)
        return FallbackQuerySet(filtered_data)
    
    def first(self):
        if self.data:
            return FallbackUser(self.data[0]) if 'username' in self.data[0] else self.data[0]
        return None
    
    def count(self):
        return len(self.data)
    
    def __iter__(self):
        return iter(self.data)
    
    def __len__(self):
        return len(self.data)

class FallbackMongoUser:
    """模拟MongoUser类"""
    @staticmethod
    def objects(**kwargs):
        return FallbackQuerySet(FALLBACK_USERS).filter(**kwargs)

def get_fallback_stats():
    """获取降级模式统计数据"""
    return {
        'total_users': len(FALLBACK_USERS),
        'total_houses': len(FALLBACK_HOUSES),
        'cities': list(set(house['city'] for house in FALLBACK_HOUSES)),
        'districts': list(set(house['district'] for house in FALLBACK_HOUSES)),
        'rental_types': list(set(house['rental_type'] for house in FALLBACK_HOUSES)),
        'avg_price': sum(house['price'] for house in FALLBACK_HOUSES) / len(FALLBACK_HOUSES),
        'price_range': {
            'min': min(house['price'] for house in FALLBACK_HOUSES),
            'max': max(house['price'] for house in FALLBACK_HOUSES)
        }
    }

def search_fallback_houses(filters=None, page=1, page_size=20):
    """搜索降级模式房源"""
    houses = FALLBACK_HOUSES.copy()
    
    if filters:
        if filters.get('city'):
            houses = [h for h in houses if h['city'] == filters['city']]
        if filters.get('district'):
            houses = [h for h in houses if h['district'] == filters['district']]
        if filters.get('rental_type'):
            houses = [h for h in houses if h['rental_type'] == filters['rental_type']]
        if filters.get('min_price'):
            houses = [h for h in houses if h['price'] >= filters['min_price']]
        if filters.get('max_price'):
            houses = [h for h in houses if h['price'] <= filters['max_price']]
        if filters.get('keyword'):
            keyword = filters['keyword'].lower()
            houses = [h for h in houses if keyword in h['title'].lower() or keyword in h['description'].lower()]
    
    total = len(houses)
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        'houses': houses[start:end],
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }
