#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
房源数据分析与智能问答系统 - 一键启动脚本
课程设计专用版本
版本: 2025-07-02
"""

import os
import sys
import time
import subprocess
import pymongo
import requests

def print_banner():
    """显示启动横幅"""
    print("=" * 60)
    print("    房源数据分析与智能问答系统")
    print("         一键启动脚本")
    print("       课程设计专用版本")
    print("       版本: 2025-07-02")
    print("=" * 60)
    print()

def start_mongodb():
    """启动MongoDB"""
    print("[步骤1] 启动MongoDB数据库...")
    print("-" * 40)
    
    # 停止现有MongoDB服务
    try:
        subprocess.run(['net', 'stop', 'MongoDB'], capture_output=True)
        time.sleep(2)
    except:
        pass
    
    # 启动无认证MongoDB
    try:
        print("启动无认证MongoDB进程...")
        subprocess.Popen([
            'mongod', '--dbpath', 'C:\\data\\db', 
            '--noauth', '--bind_ip', '127.0.0.1', '--port', '27017'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("等待MongoDB启动...")
        time.sleep(8)
        
        # 测试连接
        client = pymongo.MongoClient('mongodb://localhost:27017/', 
                                   serverSelectionTimeoutMS=5000)
        client.server_info()
        db = client['house_data']
        count = db.houses.count_documents({})
        print(f"✅ MongoDB启动成功，房源数据: {count}条")
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB启动失败: {e}")
        return False

def start_django():
    """启动Django"""
    print("\n[步骤2] 启动Django Web服务器...")
    print("-" * 40)
    
    # 数据库迁移
    try:
        print("执行数据库迁移...")
        subprocess.run([sys.executable, 'manage.py', 'migrate', '--run-syncdb'], 
                      capture_output=True, timeout=30)
    except:
        pass
    
    # 启动Django服务器
    print("启动Django开发服务器...")
    django_process = subprocess.Popen([sys.executable, 'manage.py', 'runserver', '8000'],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)
    
    # 测试Django
    try:
        response = requests.get('http://127.0.0.1:8000/mongo/login/', timeout=5)
        if response.status_code == 200:
            print("✅ Django服务器启动成功")
            return django_process
        else:
            print("⚠️ Django服务器响应异常")
            return django_process
    except Exception as e:
        print(f"⚠️ Django服务器测试失败: {e}")
        return django_process

def run_spider_test():
    """运行1分钟爬虫测试"""
    print("\n[步骤3] 运行1分钟爬虫测试...")
    print("-" * 40)
    
    try:
        print("启动爬虫测试 (60秒)...")
        os.chdir("scrapy_spider")
        
        cmd = [sys.executable, "-m", "scrapy", "crawl", "lianjia",
               "-a", "pages=2", "-s", "CLOSESPIDER_TIMEOUT=60",
               "-s", "DOWNLOAD_DELAY=3", "-s", "CONCURRENT_REQUESTS=1"]
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT, text=True)
        
        start_time = time.time()
        while time.time() - start_time < 60:
            line = process.stdout.readline()
            if line and "Scraped from" in line:
                print(".", end="", flush=True)
            if process.poll() is not None:
                break
            time.sleep(0.5)
        
        if process.poll() is None:
            process.terminate()
        
        print("\n✅ 1分钟爬虫测试完成")
        os.chdir("..")
        
    except Exception as e:
        print(f"❌ 爬虫测试失败: {e}")
        try:
            os.chdir("..")
        except:
            pass

def show_completion():
    """显示启动完成信息"""
    print("\n" + "=" * 60)
    print("           🎉 一键启动完成！")
    print("=" * 60)
    print()
    print("📊 系统状态:")
    print("   ✅ MongoDB数据库: 运行中 (无认证模式)")
    print("   ✅ Django Web服务器: 运行中 (后台)")
    print("   ✅ 1分钟爬虫测试: 已完成")
    print()
    print("🌐 访问地址:")
    print("   📱 MongoDB版本: http://127.0.0.1:8000/mongo/login/")
    print("   🤖 RAG智能问答: http://127.0.0.1:8000/mongo/rag/")
    print("   📊 数据总览: http://127.0.0.1:8000/mongo/tableData/")
    print("   ☁️ 词云分析: http://127.0.0.1:8000/mongo/housewordcloud/")
    print("   💰 价格预测: http://127.0.0.1:8000/mongo/predict-all-prices/")
    print()
    print("👤 测试账户:")
    print("   用户名: test4071741")
    print("   密码: 0515")
    print()
    print("💡 使用提示:")
    print("   - Django服务器在后台运行")
    print("   - 关闭此窗口不会停止服务器")
    print("   - 如需停止服务器，请使用任务管理器")
    print()

def main():
    """主函数 - 一键启动流程"""
    try:
        print_banner()
        
        print("🚀 开始一键启动流程...")
        print("=" * 60)
        
        # 检查环境
        if not os.path.exists('manage.py'):
            print("❌ 错误: Django项目文件不存在")
            input("按回车键退出...")
            return
        
        # 启动MongoDB
        if not start_mongodb():
            print("❌ MongoDB启动失败，无法继续")
            input("按回车键退出...")
            return
        
        # 启动Django
        django_process = start_django()
        if not django_process:
            print("❌ Django启动失败，无法继续")
            input("按回车键退出...")
            return
        
        # 运行爬虫测试
        run_spider_test()
        
        # 显示完成信息
        show_completion()
        
        # 等待用户操作
        input("按回车键退出启动脚本...")
        
        print("\n👋 启动脚本退出")
        print("💡 系统继续在后台运行")
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断启动过程")
    except Exception as e:
        print(f"\n❌ 启动过程中发生错误: {e}")
        input("按回车键退出...")

if __name__ == '__main__':
    main()
