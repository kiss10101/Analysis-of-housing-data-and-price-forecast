#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查MongoDB运行状态
"""

import socket
import subprocess
import time

def check_port_27017():
    """检查27017端口是否开放"""
    print("检查MongoDB端口状态")
    print("=" * 40)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('127.0.0.1', 27017))
        sock.close()
        
        if result == 0:
            print("✅ 端口27017已开放，MongoDB可能正在运行")
            return True
        else:
            print("❌ 端口27017未开放，MongoDB未运行")
            return False
    except Exception as e:
        print(f"❌ 端口检查失败: {e}")
        return False

def check_mongodb_process():
    """检查MongoDB进程"""
    print("\n检查MongoDB进程")
    print("=" * 40)
    
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq mongod.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'mongod.exe' in result.stdout:
            print("✅ 找到MongoDB进程:")
            lines = result.stdout.split('\n')
            for line in lines:
                if 'mongod.exe' in line:
                    print(f"  {line.strip()}")
            return True
        else:
            print("❌ 未找到MongoDB进程")
            return False
    except Exception as e:
        print(f"❌ 进程检查失败: {e}")
        return False

def simple_connection_test():
    """简单连接测试"""
    print("\n简单连接测试")
    print("=" * 40)
    
    try:
        import pymongo
        
        # 尝试连接，超时时间很短
        client = pymongo.MongoClient('mongodb://127.0.0.1:27017/', 
                                   serverSelectionTimeoutMS=2000,
                                   connectTimeoutMS=2000)
        
        # 测试ping
        client.admin.command('ping')
        print("✅ MongoDB连接成功!")
        
        # 测试数据库操作
        db = client['test']
        collection = db['test_collection']
        
        # 简单的插入测试
        test_doc = {'test': True, 'timestamp': time.time()}
        result = collection.insert_one(test_doc)
        print(f"✅ 数据写入成功: {result.inserted_id}")
        
        # 清理测试数据
        collection.delete_one({'_id': result.inserted_id})
        print("✅ 测试数据清理完成")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False

def provide_startup_help():
    """提供启动帮助"""
    print("\n" + "=" * 50)
    print("MongoDB启动帮助")
    print("=" * 50)
    
    print("如果MongoDB未运行，请尝试以下方法:")
    print()
    
    print("方法1: 双击运行启动脚本")
    print("  文件: mongodb_integration/quick_start_mongodb.bat")
    print("  注意: 保持窗口打开")
    print()
    
    print("方法2: 手动命令行启动")
    print("  1. 打开命令提示符")
    print("  2. 执行以下命令:")
    print('     cd /d "F:\\Non-relational database technology\\mongodb-windows-x86_64-8.0.5\\bin"')
    print('     mongod.exe --dbpath "F:\\Non-relational database technology\\mongodb-windows-x86_64-8.0.5\\data" --bind_ip 127.0.0.1')
    print()
    
    print("方法3: 检查数据目录")
    print("  确保数据目录存在:")
    print("  F:\\Non-relational database technology\\mongodb-windows-x86_64-8.0.5\\data")
    print()
    
    print("启动成功的标志:")
    print("  - 看到 'waiting for connections on port 27017'")
    print("  - 端口27017被占用")
    print("  - 可以连接到 mongodb://127.0.0.1:27017")

def main():
    """主函数"""
    print("MongoDB状态检查工具")
    print("=" * 50)
    
    # 检查端口
    port_open = check_port_27017()
    
    # 检查进程
    process_running = check_mongodb_process()
    
    # 连接测试
    connection_ok = False
    if port_open:
        connection_ok = simple_connection_test()
    
    print("\n" + "=" * 50)
    print("检查结果总结")
    print("=" * 50)
    
    if connection_ok:
        print("🎉 MongoDB运行正常!")
        print("✅ 端口开放")
        print("✅ 进程运行")
        print("✅ 连接成功")
        print("\n可以开始MongoDB集成开发!")
    elif port_open and process_running:
        print("⚠️  MongoDB运行但连接有问题")
        print("可能是认证或配置问题")
    elif process_running:
        print("⚠️  MongoDB进程运行但端口未开放")
        print("可能是启动参数问题")
    else:
        print("❌ MongoDB未运行")
        provide_startup_help()

if __name__ == '__main__':
    main()
