# -*- coding: utf-8 -*-
"""
MongoDB连接失败时的降级数据 - 10000条完整数据
提供充足的数据用于所有图表展示
"""

from datetime import datetime
import random
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

def generate_10k_houses():
    """生成10000条模拟房源数据"""
    
    # 扩展城市列表，包含多个城市
    cities = ['广州', '深圳', '佛山', '东莞', '中山', '珠海', '惠州', '江门']
    
    districts = {
        '广州': ['天河区', '越秀区', '海珠区', '荔湾区', '白云区', '黄埔区', '番禺区', '花都区', '南沙区', '从化区', '增城区'],
        '深圳': ['福田区', '罗湖区', '南山区', '宝安区', '龙岗区', '盐田区', '龙华区', '坪山区', '光明区', '大鹏新区'],
        '佛山': ['禅城区', '南海区', '顺德区', '高明区', '三水区'],
        '东莞': ['莞城区', '南城区', '东城区', '万江区', '石碣镇', '石龙镇', '茶山镇', '石排镇'],
        '中山': ['石岐区', '东区', '西区', '南区', '五桂山区', '火炬开发区'],
        '珠海': ['香洲区', '斗门区', '金湾区'],
        '惠州': ['惠城区', '惠阳区', '博罗县', '惠东县', '龙门县'],
        '江门': ['蓬江区', '江海区', '新会区', '台山市', '开平市', '鹤山市', '恩平市']
    }
    
    streets = {
        '广州': ['珠江新城', '体育西路', '天河北路', '五山路', '龙口东路', '石牌路', '林和路', '黄埔大道', '北京路', '中山五路', '环市东路', '东风东路', '建设六马路', '淘金路', '农林路', '先烈路'],
        '深圳': ['华强北路', '深南大道', '彩田路', '益田路', '红荔路', '莲花路', '新洲路', '皇岗路', '人民南路', '深南东路', '建设路', '宝安南路', '东门路', '春风路', '爱国路', '文锦路'],
        '佛山': ['季华路', '汾江路', '岭南大道', '魁奇路', '佛山大道', '同济路', '普君路', '文华路', '桂城路', '南海大道', '海八路', '灯湖路', '佛平路', '狮山大道', '桂澜路', '海三路'],
        '东莞': ['东城大道', '南城大道', '莞城大道', '万江大道', '石碣大道', '石龙大道', '茶山大道', '石排大道'],
        '中山': ['中山路', '兴中道', '岐江路', '博爱路', '孙文路', '起湾道', '长江路', '沙岗路'],
        '珠海': ['情侣路', '迎宾大道', '珠海大道', '香洲路', '吉大路', '拱北路', '前山路', '唐家路'],
        '惠州': ['惠州大道', '江北大道', '河南岸路', '麦地路', '下埔路', '演达路', '惠城大道', '三环路'],
        '江门': ['建设路', '胜利路', '跃进路', '江华路', '港口路', '白沙大道', '江门大道', '迎宾大道']
    }
    
    buildings = ['花园', '广场', '大厦', '公寓', '小区', '城', '苑', '居', '庭', '轩', '阁', '园', '府', '邸', '湾', '港', '汇', '中心', '世界', '天地', '名都', '豪庭', '雅苑', '华府']
    room_types = ['1室1厅1卫', '1室1厅1卫', '2室1厅1卫', '2室2厅1卫', '2室2厅2卫', '3室1厅1卫', '3室2厅1卫', '3室2厅2卫', '4室2厅2卫', '4室3厅2卫', '5室2厅3卫']
    rental_types = ['整租', '合租', '单间', '公寓']
    orientations = ['东', '南', '西', '北', '东南', '东北', '西南', '西北', '南北', '东西', '朝南', '朝北', '朝东', '朝西']
    styles = ['精装修', '简装修', '毛坯房', '豪华装修', '现代简约', '欧式风格', '中式风格', '美式风格']
    features = ['近地铁', '配套齐全', '交通便利', '环境优美', '商圈繁华', '学区房', '景观房', '新装修', '拎包入住', '停车位']

    houses = []
    for i in range(1, 10001):  # 生成10000条数据
        city = random.choice(cities)
        district = random.choice(districts[city])
        street = random.choice(streets[city])
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
        elif '4室' in room_type:
            area = random.randint(130, 200)
            base_price = random.randint(6000, 12000)
        else:  # 5室
            area = random.randint(180, 300)
            base_price = random.randint(8000, 15000)

        # 根据城市调整价格
        city_multiplier = {
            '广州': 1.0,
            '深圳': 1.5,
            '佛山': 0.7,
            '东莞': 0.8,
            '中山': 0.6,
            '珠海': 0.9,
            '惠州': 0.5,
            '江门': 0.4
        }
        
        # 根据朝向调整价格
        orientation_multiplier = {
            '南': 1.2, '朝南': 1.2,
            '东南': 1.15, '西南': 1.1,
            '东': 1.05, '朝东': 1.05,
            '南北': 1.1, '东西': 1.0,
            '西': 0.95, '朝西': 0.95,
            '东北': 0.9, '西北': 0.85,
            '北': 0.8, '朝北': 0.8
        }
        
        orientation = random.choice(orientations)
        price = base_price * city_multiplier[city] * orientation_multiplier.get(orientation, 1.0)
        price = round(price * random.uniform(0.8, 1.2), 2)  # 添加随机波动

        title = f"{district}{style}{room_type} - {feature}"

        house = {
            '_id': str(i),
            'title': title,
            'rental_type': random.choice(rental_types),
            'city': city,
            'district': district,
            'street': street,
            'building': building,
            'price': round(price, 2),
            'area': float(area),
            'room_type': room_type,
            'floor': f"{random.randint(1, 30)}/{random.randint(20, 35)}",
            'orientation': orientation,
            'direction': orientation,  # 添加direction字段用于兼容
            'description': f'{style}，{feature}，{room_type}',
            'crawl_time': datetime.now()
        }
        houses.append(house)

    return houses

def validate_orientation(orientation):
    """验证和清洗朝向数据"""
    if not orientation:
        return '未知'
    
    # 标准化朝向
    orientation_map = {
        '南': '南', '朝南': '南', '正南': '南',
        '北': '北', '朝北': '北', '正北': '北',
        '东': '东', '朝东': '东', '正东': '东',
        '西': '西', '朝西': '西', '正西': '西',
        '东南': '东南', '东南向': '东南',
        '东北': '东北', '东北向': '东北',
        '西南': '西南', '西南向': '西南',
        '西北': '西北', '西北向': '西北',
        '南北': '南北', '南北向': '南北',
        '东西': '东西', '东西向': '东西'
    }
    
    return orientation_map.get(orientation, '未知')

def clean_house_data(house_data):
    """清洗房源数据"""
    if isinstance(house_data, dict):
        # 清洗朝向字段
        if 'orientation' in house_data:
            house_data['orientation'] = validate_orientation(house_data['orientation'])
        if 'direction' in house_data:
            house_data['direction'] = validate_orientation(house_data['direction'])

    return house_data

# 生成10000条房源数据
FALLBACK_HOUSES_10K = [clean_house_data(house) for house in generate_10k_houses()]

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

def get_fallback_stats_10k():
    """获取10K数据的统计信息"""
    return {
        'total_users': len(FALLBACK_USERS),
        'total_houses': len(FALLBACK_HOUSES_10K),
        'cities': list(set(house['city'] for house in FALLBACK_HOUSES_10K)),
        'districts': list(set(house['district'] for house in FALLBACK_HOUSES_10K)),
        'rental_types': list(set(house['rental_type'] for house in FALLBACK_HOUSES_10K)),
        'orientations': list(set(house['orientation'] for house in FALLBACK_HOUSES_10K)),
        'avg_price': sum(house['price'] for house in FALLBACK_HOUSES_10K) / len(FALLBACK_HOUSES_10K),
        'price_range': {
            'min': min(house['price'] for house in FALLBACK_HOUSES_10K),
            'max': max(house['price'] for house in FALLBACK_HOUSES_10K)
        }
    }
