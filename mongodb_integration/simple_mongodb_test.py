#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的MongoDB连接测试
不需要认证的基础测试
"""

import pymongo
from datetime import datetime

def test_basic_connection():
    """测试基础连接"""
    print("MongoDB基础连接测试")
    print("=" * 50)
    
    try:
        # 尝试连接MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        
        # 测试连接
        client.admin.command('ping')
        print("✅ MongoDB服务连接成功")
        
        # 获取服务器信息
        server_info = client.server_info()
        print(f"✅ MongoDB版本: {server_info['version']}")
        
        # 尝试访问house_data数据库
        db = client['house_data']
        
        # 测试集合操作
        collection = db['houses']
        
        # 插入测试文档
        test_doc = {
            'title': '测试房源',
            'type': '整租',
            'city': '天河区',
            'price': 3000,
            'created_at': datetime.now(),
            'test': True
        }
        
        result = collection.insert_one(test_doc)
        print(f"✅ 测试文档插入成功，ID: {result.inserted_id}")
        
        # 查询测试文档
        found_doc = collection.find_one({'_id': result.inserted_id})
        if found_doc:
            print(f"✅ 测试文档查询成功: {found_doc['title']}")
        
        # 统计文档数量
        count = collection.count_documents({})
        print(f"✅ 集合中文档总数: {count}")
        
        # 清理测试文档
        collection.delete_one({'_id': result.inserted_id})
        print("✅ 测试文档清理完成")
        
        client.close()
        return True
        
    except pymongo.errors.ServerSelectionTimeoutError:
        print("❌ MongoDB服务连接超时")
        print("请确认MongoDB服务正在运行")
        return False
    except pymongo.errors.OperationFailure as e:
        print(f"❌ MongoDB操作失败: {e}")
        print("可能需要认证或权限设置")
        return False
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False

def test_with_auth():
    """测试带认证的连接"""
    print("\n" + "=" * 50)
    print("MongoDB认证连接测试")
    print("=" * 50)
    
    # 如果您设置了用户认证，请修改这里的连接字符串
    auth_uri = "mongodb://house_user:house_password@localhost:27017/house_data"
    
    try:
        client = pymongo.MongoClient(auth_uri, serverSelectionTimeoutMS=5000)
        
        # 测试连接
        client.admin.command('ping')
        print("✅ 认证连接成功")
        
        db = client['house_data']
        collection = db['houses']
        
        # 测试操作
        count = collection.count_documents({})
        print(f"✅ 认证访问成功，文档数: {count}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"ℹ️  认证连接测试跳过: {e}")
        return False

def main():
    """主函数"""
    print("房源数据分析系统 - MongoDB连接测试")
    print(f"测试时间: {datetime.now()}")
    print()
    
    # 基础连接测试
    basic_ok = test_basic_connection()
    
    # 认证连接测试（可选）
    auth_ok = test_with_auth()
    
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    
    if basic_ok:
        print("🎉 MongoDB基础功能测试通过!")
        print("✅ 可以开始MongoDB集成开发")
        
        print("\n建议的手动配置步骤:")
        print("1. 在MongoDB Compass中确认数据库 'house_data' 已创建")
        print("2. 确认集合 'houses' 已创建")
        print("3. 可以开始数据模型设计")
        
    elif auth_ok:
        print("🎉 MongoDB认证连接测试通过!")
        print("✅ 使用认证模式进行开发")
        
    else:
        print("❌ MongoDB连接测试失败")
        print("\n故障排除建议:")
        print("1. 确认MongoDB服务正在运行")
        print("2. 检查端口27017是否可访问")
        print("3. 在MongoDB Compass中手动创建数据库")

if __name__ == '__main__':
    main()
