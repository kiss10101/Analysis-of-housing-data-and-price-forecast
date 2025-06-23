#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建MongoDB用户和数据库
解决认证问题
"""

import pymongo
from pymongo.errors import OperationFailure

def create_mongodb_user():
    """创建MongoDB用户"""
    print("🍃 MongoDB用户创建工具")
    print("=" * 50)
    
    try:
        # 尝试连接到admin数据库
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        admin_db = client.admin
        
        print("✅ 连接到MongoDB成功")
        
        # 尝试创建管理员用户
        try:
            admin_db.command("createUser", "admin", 
                           pwd="admin123", 
                           roles=["root"])
            print("✅ 创建管理员用户成功")
        except OperationFailure as e:
            if "already exists" in str(e):
                print("ℹ️  管理员用户已存在")
            else:
                print(f"❌ 创建管理员用户失败: {e}")
        
        # 创建应用数据库用户
        house_db = client.house_data
        try:
            house_db.command("createUser", "house_user",
                           pwd="house_password",
                           roles=["readWrite"])
            print("✅ 创建应用用户成功")
        except OperationFailure as e:
            if "already exists" in str(e):
                print("ℹ️  应用用户已存在")
            else:
                print(f"❌ 创建应用用户失败: {e}")
        
        # 测试连接
        print("\n测试连接...")
        
        # 测试管理员连接
        try:
            admin_client = pymongo.MongoClient('mongodb://admin:admin123@localhost:27017/house_data?authSource=admin')
            admin_client.server_info()
            print("✅ 管理员认证连接成功")
        except Exception as e:
            print(f"❌ 管理员认证失败: {e}")
        
        # 测试应用用户连接
        try:
            app_client = pymongo.MongoClient('mongodb://house_user:house_password@localhost:27017/house_data')
            app_client.server_info()
            print("✅ 应用用户认证连接成功")
        except Exception as e:
            print(f"❌ 应用用户认证失败: {e}")
            
        client.close()
        
    except Exception as e:
        print(f"❌ 连接MongoDB失败: {e}")
        print("\n可能的解决方案:")
        print("1. 确保MongoDB服务正在运行")
        print("2. 尝试无认证模式启动MongoDB")
        print("3. 检查MongoDB配置文件")

if __name__ == '__main__':
    create_mongodb_user()
