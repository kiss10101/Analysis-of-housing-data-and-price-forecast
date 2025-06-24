#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成500条房源数据用于MongoDB版本图表展示
控制硬件开销，提供充足的数据用于可视化
"""

import random
from datetime import datetime

def generate_500_houses():
    """生成500条模拟房源数据"""
    
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
                '富力城', '中海花园', '华润城', '龙湖天街', '时代广场', '星河湾', '雅居乐', '金地花园',
                '招商花园', '融创城', '绿城花园', '世茂广场', '华发城', '佳兆业', '奥园城', '合景泰富']
    
    rental_types = ['整租', '合租', '单间']
    room_types = ['1室0厅', '1室1厅', '2室1厅', '2室2厅', '3室1厅', '3室2厅', '4室2厅', '4室3厅']
    orientations = ['南', '北', '东', '西', '东南', '西南', '东北', '西北', '南北', '东西']
    
    # 房源标题模板
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

def update_fallback_data():
    """更新fallback_data.py文件"""
    houses = generate_500_houses()
    
    # 生成Python代码
    code_lines = [
        "# 模拟房源数据 - 500条数据用于图表展示",
        "FALLBACK_HOUSES = ["
    ]
    
    for house in houses:
        code_lines.append("    {")
        for key, value in house.items():
            if key == 'crawl_time':
                code_lines.append(f"        '{key}': datetime.now(),")
            elif isinstance(value, str):
                code_lines.append(f"        '{key}': '{value}',")
            else:
                code_lines.append(f"        '{key}': {value},")
        code_lines.append("    },")
    
    code_lines.append("]")
    
    return '\n'.join(code_lines)

if __name__ == '__main__':
    print("生成500条房源数据...")
    houses = generate_500_houses()
    print(f"生成完成，共{len(houses)}条数据")
    
    # 统计信息
    districts = {}
    rental_types = {}
    for house in houses:
        district = house['district']
        rental_type = house['rental_type']
        districts[district] = districts.get(district, 0) + 1
        rental_types[rental_type] = rental_types.get(rental_type, 0) + 1
    
    print("\n区域分布:")
    for district, count in sorted(districts.items()):
        print(f"  {district}: {count}条")
    
    print("\n租赁类型分布:")
    for rental_type, count in sorted(rental_types.items()):
        print(f"  {rental_type}: {count}条")
    
    print(f"\n价格范围: {min(h['price'] for h in houses):.2f} - {max(h['price'] for h in houses):.2f}元/月")
    print(f"面积范围: {min(h['area'] for h in houses):.0f} - {max(h['area'] for h in houses):.0f}㎡")
