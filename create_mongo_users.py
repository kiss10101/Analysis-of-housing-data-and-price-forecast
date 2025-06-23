#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建MongoDB用户数据
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Python租房房源数据可视化分析.settings')
django.setup()

from app_mongo.models import MongoUser
from datetime import datetime

def create_test_users():
    """创建测试用户"""
    print("🍃 创建MongoDB测试用户")
    print("=" * 50)
    
    test_users = [
        {
            'username': 'admin',
            'password': 'admin123',
            'phone': '13800138000',
            'email': 'admin@test.com',
            'avatar': ''
        },
        {
            'username': 'test',
            'password': '123456',
            'phone': '13800138001',
            'email': 'test@test.com',
            'avatar': ''
        },
        {
            'username': 'demo',
            'password': 'demo123',
            'phone': '13800138002',
            'email': 'demo@test.com',
            'avatar': ''
        }
    ]
    
    created_count = 0
    
    for user_data in test_users:
        try:
            # 检查用户是否已存在
            existing_user = MongoUser.objects(username=user_data['username']).first()
            if existing_user:
                print(f"ℹ️  用户已存在: {user_data['username']}")
            else:
                # 创建新用户
                new_user = MongoUser(
                    username=user_data['username'],
                    password=user_data['password'],
                    phone=user_data['phone'],
                    email=user_data['email'],
                    avatar=user_data['avatar'],
                    time=datetime.now()
                )
                new_user.save()
                print(f"✅ 创建用户成功: {user_data['username']}")
                created_count += 1
                
        except Exception as e:
            print(f"❌ 创建用户失败 {user_data['username']}: {e}")
    
    # 统计用户数量
    total_users = MongoUser.objects.count()
    print(f"\n📊 用户统计:")
    print(f"新创建用户: {created_count}")
    print(f"总用户数量: {total_users}")
    
    # 测试登录
    print(f"\n🔐 测试登录:")
    for user_data in test_users:
        try:
            user = MongoUser.objects(username=user_data['username'], password=user_data['password']).first()
            if user:
                print(f"✅ {user_data['username']} 登录测试成功")
            else:
                print(f"❌ {user_data['username']} 登录测试失败")
        except Exception as e:
            print(f"❌ {user_data['username']} 登录测试错误: {e}")
    
    print("\n✅ 用户创建完成")

if __name__ == '__main__':
    create_test_users()
