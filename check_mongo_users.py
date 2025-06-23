#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查和创建MongoDB用户数据
"""

import pymongo

def check_and_create_users():
    """检查和创建MongoDB用户"""
    try:
        print('🔍 检查MongoDB用户数据...')
        
        # 连接MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['house_data']
        users_collection = db['users']
        
        # 查看所有用户
        users = list(users_collection.find({}))
        print(f'用户总数: {len(users)}')
        
        if users:
            print('\n现有用户:')
            for user in users:
                username = user.get('username', 'N/A')
                password = user.get('password', 'N/A')
                print(f'- 用户名: {username}, 密码: {password}')
        
        # 检查是否有admin用户
        admin_user = users_collection.find_one({'username': 'admin'})
        if admin_user:
            print('\n✅ 找到admin用户')
            print(f'密码: {admin_user.get("password")}')
        else:
            print('\n❌ 未找到admin用户，正在创建...')
            
            # 创建admin用户
            admin_data = {
                'username': 'admin',
                'password': 'admin123',
                'email': 'admin@example.com',
                'phone': '13800138000',
                'avatar': 'user/avatar/default.png'
            }
            result = users_collection.insert_one(admin_data)
            print(f'✅ admin用户创建成功，ID: {result.inserted_id}')
        
        # 检查test用户
        test_user = users_collection.find_one({'username': 'test'})
        if not test_user:
            print('\n创建test用户...')
            test_data = {
                'username': 'test',
                'password': '123456',
                'email': 'test@example.com',
                'phone': '13800138001',
                'avatar': 'user/avatar/default.png'
            }
            result = users_collection.insert_one(test_data)
            print(f'✅ test用户创建成功，ID: {result.inserted_id}')
        
        # 检查demo用户
        demo_user = users_collection.find_one({'username': 'demo'})
        if not demo_user:
            print('\n创建demo用户...')
            demo_data = {
                'username': 'demo',
                'password': 'demo123',
                'email': 'demo@example.com',
                'phone': '13800138002',
                'avatar': 'user/avatar/default.png'
            }
            result = users_collection.insert_one(demo_data)
            print(f'✅ demo用户创建成功，ID: {result.inserted_id}')
        
        # 最终用户统计
        final_count = users_collection.count_documents({})
        print(f'\n📊 最终用户总数: {final_count}')
        
        return True
        
    except Exception as e:
        print(f'❌ MongoDB操作失败: {e}')
        print('可能需要启动MongoDB或检查连接')
        return False

def test_mongo_connection():
    """测试MongoDB连接"""
    try:
        print('🔗 测试MongoDB连接...')
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        
        # 测试连接
        client.admin.command('ping')
        print('✅ MongoDB连接成功')
        
        # 列出数据库
        db_names = client.list_database_names()
        print(f'数据库列表: {db_names}')
        
        # 检查house_data数据库
        if 'house_data' in db_names:
            print('✅ house_data数据库存在')
            
            db = client['house_data']
            collections = db.list_collection_names()
            print(f'集合列表: {collections}')
        else:
            print('⚠️  house_data数据库不存在，将自动创建')
        
        return True
        
    except Exception as e:
        print(f'❌ MongoDB连接失败: {e}')
        return False

if __name__ == "__main__":
    print("🍃 MongoDB用户数据检查和创建")
    print("=" * 50)
    
    # 测试连接
    if test_mongo_connection():
        # 检查和创建用户
        check_and_create_users()
    else:
        print("请确保MongoDB服务正在运行")
