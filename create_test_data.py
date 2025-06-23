#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试数据 - 绕过认证问题
使用PyMongo直接操作
"""

import pymongo
from datetime import datetime
import json

def create_test_data():
    """创建测试数据"""
    print("🍃 创建MongoDB测试数据")
    print("=" * 50)
    
    try:
        # 连接MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client.house_data
        
        print("✅ 连接到MongoDB成功")
        
        # 创建测试用户
        users_collection = db.users
        test_users = [
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
            }
        ]
        
        for user in test_users:
            try:
                # 检查用户是否已存在
                existing = users_collection.find_one({'username': user['username']})
                if not existing:
                    result = users_collection.insert_one(user)
                    print(f"✅ 创建用户: {user['username']}")
                else:
                    print(f"ℹ️  用户已存在: {user['username']}")
            except Exception as e:
                print(f"❌ 创建用户失败 {user['username']}: {e}")
        
        # 创建测试房源数据
        houses_collection = db.houses
        test_houses = [
            {
                'title': '测试房源1 - 天河区精装修',
                'rental_type': '整租',
                'location': {
                    'city': '广州',
                    'district': '天河区',
                    'street': '体育西路',
                    'building': '测试大厦'
                },
                'price': {
                    'monthly_rent': 3000.0,
                    'deposit': 6000.0
                },
                'features': {
                    'area': 80.0,
                    'room_type': '2室1厅',
                    'floor': '10/20',
                    'orientation': '南北'
                },
                'images': [],
                'description': '精装修，交通便利',
                'crawl_time': datetime.now(),
                'data_quality_score': 85
            },
            {
                'title': '测试房源2 - 越秀区地铁房',
                'rental_type': '合租',
                'location': {
                    'city': '广州',
                    'district': '越秀区',
                    'street': '中山路',
                    'building': '地铁大厦'
                },
                'price': {
                    'monthly_rent': 1500.0,
                    'deposit': 3000.0
                },
                'features': {
                    'area': 20.0,
                    'room_type': '1室0厅',
                    'floor': '5/15',
                    'orientation': '南'
                },
                'images': [],
                'description': '地铁口，单间出租',
                'crawl_time': datetime.now(),
                'data_quality_score': 75
            }
        ]
        
        for house in test_houses:
            try:
                # 检查房源是否已存在
                existing = houses_collection.find_one({'title': house['title']})
                if not existing:
                    result = houses_collection.insert_one(house)
                    print(f"✅ 创建房源: {house['title']}")
                else:
                    print(f"ℹ️  房源已存在: {house['title']}")
            except Exception as e:
                print(f"❌ 创建房源失败: {e}")
        
        # 统计数据
        user_count = users_collection.count_documents({})
        house_count = houses_collection.count_documents({})
        
        print(f"\n📊 数据统计:")
        print(f"用户数量: {user_count}")
        print(f"房源数量: {house_count}")
        
        client.close()
        print("\n✅ 测试数据创建完成")
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        print("\n可能的原因:")
        print("1. MongoDB认证问题")
        print("2. 数据库权限不足")
        print("3. 网络连接问题")

if __name__ == '__main__':
    create_test_data()
