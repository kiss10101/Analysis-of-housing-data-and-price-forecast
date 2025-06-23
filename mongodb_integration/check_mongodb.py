#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB环境检查工具
验证MongoDB连接和基础配置
"""

import sys
import pymongo
from datetime import datetime

def check_mongodb_connection():
    """检查MongoDB连接"""
    print("=" * 60)
    print("MongoDB环境检查")
    print("=" * 60)
    
    try:
        # 连接MongoDB (默认本地连接)
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        
        # 检查服务器状态
        server_info = client.server_info()
        print(f"✅ MongoDB连接成功")
        print(f"✅ MongoDB版本: {server_info['version']}")
        print(f"✅ 服务器时间: {datetime.now()}")
        
        # 列出现有数据库
        db_list = client.list_database_names()
        print(f"✅ 现有数据库: {db_list}")
        
        # 测试数据库操作
        test_db = client['test_connection']
        test_collection = test_db['test_collection']
        
        # 插入测试文档
        test_doc = {
            'test': True,
            'timestamp': datetime.now(),
            'message': 'MongoDB连接测试'
        }
        
        result = test_collection.insert_one(test_doc)
        print(f"✅ 测试写入成功，文档ID: {result.inserted_id}")
        
        # 查询测试文档
        found_doc = test_collection.find_one({'_id': result.inserted_id})
        if found_doc:
            print(f"✅ 测试查询成功: {found_doc['message']}")
        
        # 清理测试数据
        test_collection.delete_one({'_id': result.inserted_id})
        print("✅ 测试数据清理完成")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB连接失败: {e}")
        return False

def check_python_packages():
    """检查Python包"""
    print("\n" + "=" * 60)
    print("Python包检查")
    print("=" * 60)
    
    packages = [
        ('pymongo', 'MongoDB Python驱动'),
        ('mongoengine', 'MongoDB ODM (可选)'),
        ('bson', 'BSON支持')
    ]
    
    results = []
    
    for package_name, description in packages:
        try:
            module = __import__(package_name)
            version = getattr(module, '__version__', 'Unknown')
            print(f"✅ {package_name} ({description}): {version}")
            results.append(True)
        except ImportError:
            print(f"❌ {package_name} ({description}): 未安装")
            results.append(False)
    
    return all(results)

def install_missing_packages():
    """安装缺失的包"""
    print("\n" + "=" * 60)
    print("安装缺失的Python包")
    print("=" * 60)
    
    try:
        import mongoengine
        print("✅ mongoengine已安装")
    except ImportError:
        print("⚠️  mongoengine未安装，正在安装...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'mongoengine'])
            print("✅ mongoengine安装成功")
        except Exception as e:
            print(f"❌ mongoengine安装失败: {e}")
            return False
    
    return True

def main():
    """主函数"""
    print("房源数据分析系统 - MongoDB环境检查")
    print(f"检查时间: {datetime.now()}")
    
    # 检查Python包
    packages_ok = check_python_packages()
    
    if not packages_ok:
        print("\n正在安装缺失的包...")
        install_missing_packages()
    
    # 检查MongoDB连接
    mongodb_ok = check_mongodb_connection()
    
    print("\n" + "=" * 60)
    print("检查结果汇总")
    print("=" * 60)
    
    if mongodb_ok:
        print("🎉 MongoDB环境检查通过!")
        print("✅ 可以开始MongoDB集成开发")
        
        print("\n下一步手动配置建议:")
        print("1. 在MongoDB Compass中创建数据库: house_data")
        print("2. 创建集合: houses")
        print("3. 可选：设置用户权限")
        
    else:
        print("❌ MongoDB环境检查失败")
        print("请检查MongoDB服务是否正常运行")

if __name__ == '__main__':
    main()
