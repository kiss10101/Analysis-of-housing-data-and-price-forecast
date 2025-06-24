# -*- coding: utf-8 -*-
"""
MongoDB连接失败时的降级数据
提供基本的演示功能
"""

from datetime import datetime
import re

# 模拟用户数据
FALLBACK_USERS = [
    {
        'username': 'test4071741',
        'password': '0515',
        'phone': '13800138000',
        'email': 'test4071741@test.com',
        'avatar': '',
        'time': datetime.now()
    },
    {
        'username': 'admin',
        'password': 'admin123',
        'phone': '13800138001',
        'email': 'admin@test.com',
        'avatar': '',
        'time': datetime.now()
    },
    {
        'username': 'test',
        'password': '123456',
        'phone': '13800138002',
        'email': 'test@test.com',
        'avatar': '',
        'time': datetime.now()
    },
    {
        'username': 'demo',
        'password': 'demo123',
        'phone': '13800138003',
        'email': 'demo@test.com',
        'avatar': '',
        'time': datetime.now()
    }
]

# 模拟房源数据 - 500条数据用于图表展示
def generate_fallback_houses():
    """生成500条模拟房源数据"""
    import random

    districts = ['天河区', '越秀区', '海珠区', '荔湾区', '白云区', '黄埔区', '番禺区', '花都区', '南沙区', '从化区', '增城区']
    streets = {
        '天河区': ['珠江新城', '体育西路', '天河北路', '五山路', '龙口东路', '石牌路', '林和路', '黄埔大道'],
        '越秀区': ['北京路', '中山五路', '环市东路', '东风东路', '建设六马路', '淘金路', '农林路', '先烈路'],
        '海珠区': ['滨江东路', '江南大道', '新港东路', '工业大道', '昌岗路', '宝岗大道', '南华路', '同福路'],
        '荔湾区': ['上下九路', '中山八路', '芳村大道', '花地大道', '龙津路', '康王路', '多宝路', '恩宁路'],
        '白云区': ['机场路', '白云大道', '同和路', '京溪路', '永泰路', '新市路', '三元里大道', '广园路'],
        '黄埔区': ['黄埔大道', '开发大道', '科学城', '萝岗大道', '香雪大道', '开创大道', '水西路', '丰乐路'],
        '番禺区': ['市桥路', '大学城', '万博中心', '南村路', '石基路', '清河路', '桥南路', '东环路'],
        '花都区': ['新华路', '花城路', '迎宾大道', '建设路', '云山大道', '凤凰路', '雅瑶路', '花东路'],
        '南沙区': ['港前大道', '海滨路', '进港大道', '蕉门路', '双山大道', '南沙大道', '环市大道', '黄阁路'],
        '从化区': ['河滨北路', '街口路', '从城大道', '温泉大道', '105国道', '从化大道', '新城路', '太平路'],
        '增城区': ['荔城大道', '增江大道', '新塘大道', '广园快速', '324国道', '荔新路', '府前路', '东桥路']
    }

    buildings = ['花园小区', '城市广场', '阳光家园', '绿地公园', '万科城', '保利花园', '恒大名都', '碧桂园',
                '富力城', '中海花园', '华润城', '龙湖天街', '时代广场', '星河湾', '雅居乐', '金地花园']

    rental_types = ['整租', '合租', '单间']
    room_types = ['1室0厅', '1室1厅', '2室1厅', '2室2厅', '3室1厅', '3室2厅', '4室2厅', '4室3厅']
    orientations = ['南', '北', '东', '西', '东南', '西南', '东北', '西北', '南北', '东西']

    title_templates = [
        '{district}{style}{room_type} - {feature}',
        '{district}精装{room_type} - {feature}',
        '{district}{style}装修 - {feature}',
        '{street}附近{room_type} - {feature}'
    ]

    styles = ['精装修', '豪华', '温馨', '舒适', '现代', '简约', '欧式', '中式']
    features = ['地铁直达', '交通便利', '环境优美', '配套齐全', '商圈核心', '学区房', '江景房', '公园旁']

    houses = []
    for i in range(1, 501):  # 生成500条数据
        district = random.choice(districts)
        street = random.choice(streets[district])
        building = f"{street}{random.choice(buildings)}"
        room_type = random.choice(room_types)
        style = random.choice(styles)
        feature = random.choice(features)

        # 根据房型设置合理的面积和价格
        if '1室' in room_type:
            area = random.randint(30, 60)
            base_price = random.randint(1500, 3500)
        elif '2室' in room_type:
            area = random.randint(60, 100)
            base_price = random.randint(2500, 5500)
        elif '3室' in room_type:
            area = random.randint(90, 150)
            base_price = random.randint(4000, 8000)
        else:  # 4室
            area = random.randint(130, 200)
            base_price = random.randint(6000, 12000)

        # 根据区域调整价格
        if district in ['天河区', '越秀区']:
            price = base_price * random.uniform(1.2, 1.8)
        elif district in ['海珠区', '荔湾区']:
            price = base_price * random.uniform(1.0, 1.4)
        elif district in ['白云区', '黄埔区']:
            price = base_price * random.uniform(0.8, 1.2)
        else:
            price = base_price * random.uniform(0.6, 1.0)

        title = random.choice(title_templates).format(
            district=district,
            street=street,
            style=style,
            room_type=room_type,
            feature=feature
        )

        house = {
            '_id': str(i),
            'title': title,
            'rental_type': random.choice(rental_types),
            'city': '广州',
            'district': district,
            'street': street,
            'building': building,
            'price': round(price, 2),
            'area': float(area),
            'room_type': room_type,
            'floor': f"{random.randint(1, 30)}/{random.randint(20, 35)}",
            'orientation': random.choice(orientations),
            'description': f'{style}，{feature}，{room_type}',
            'crawl_time': datetime.now()
        }
        houses.append(house)

    return houses

# 朝向数据验证和清洗函数
def validate_orientation(orientation):
    """验证和清洗朝向数据"""
    if not orientation:
        return '未知'

    # 检查是否为数字
    if isinstance(orientation, (int, float)) or (isinstance(orientation, str) and orientation.isdigit()):
        return '未知'

    # 检查是否包含数字
    if isinstance(orientation, str) and re.search(r'\d', orientation):
        return '未知'

    # 有效朝向列表
    valid_orientations = ['东', '南', '西', '北', '东南', '东北', '西南', '西北', '南北', '东西']

    # 清理字符串
    clean_orientation = str(orientation).strip()

    # 检查是否为有效朝向
    if clean_orientation in valid_orientations:
        return clean_orientation

    # 尝试匹配部分朝向
    for valid in valid_orientations:
        if valid in clean_orientation:
            return valid

    return '未知'

def clean_house_data(house_data):
    """清洗房源数据"""
    if isinstance(house_data, dict):
        # 清洗朝向字段
        if 'orientation' in house_data:
            house_data['orientation'] = validate_orientation(house_data['orientation'])
        if 'direction' in house_data:
            house_data['direction'] = validate_orientation(house_data['direction'])

    return house_data

# 生成500条房源数据
FALLBACK_HOUSES = [clean_house_data(house) for house in generate_fallback_houses()]

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
