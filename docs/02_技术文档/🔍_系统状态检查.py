#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
房源数据分析与智能问答系统 - 系统状态检查脚本
版本: 2025-07-02
功能: 检查所有系统组件的运行状态
"""

import os
import sys
import time
import subprocess
import requests
import pymongo
import pymysql
from datetime import datetime

class SystemStatusChecker:
    def __init__(self):
        self.status = {
            'python': False,
            'dependencies': {},
            'mongodb': False,
            'mysql': False,
            'django': False,
            'rag': False,
            'scrapy': False
        }
        
    def print_header(self):
        """打印标题"""
        print("=" * 80)
        print("🔍 房源数据分析与智能问答系统 - 系统状态检查")
        print("=" * 80)
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
    def check_python_environment(self):
        """检查Python环境"""
        print("🐍 [1/7] 检查Python环境...")
        print("-" * 40)
        
        # Python版本
        python_version = sys.version_info
        print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        if python_version >= (3, 8):
            print("✅ Python版本符合要求 (>= 3.8)")
            self.status['python'] = True
        else:
            print("❌ Python版本过低，建议升级到3.8+")
            
        # 检查依赖包
        dependencies = [
            ('django', 'Django'),
            ('pymongo', 'PyMongo'),
            ('pymysql', 'PyMySQL'),
            ('scrapy', 'Scrapy'),
            ('requests', 'Requests'),
            ('matplotlib', 'Matplotlib'),
            ('pandas', 'Pandas')
        ]
        
        for module_name, display_name in dependencies:
            try:
                module = __import__(module_name)
                version = getattr(module, '__version__', 'Unknown')
                print(f"✅ {display_name}: {version}")
                self.status['dependencies'][module_name] = True
            except ImportError:
                print(f"❌ {display_name}: 未安装")
                self.status['dependencies'][module_name] = False
                
        print()
        
    def check_mongodb_status(self):
        """检查MongoDB状态"""
        print("🍃 [2/7] 检查MongoDB状态...")
        print("-" * 40)
        
        # 检查进程
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq mongod.exe'], 
                                      capture_output=True, text=True)
                process_running = 'mongod.exe' in result.stdout
            else:  # Linux/Mac
                result = subprocess.run(['pgrep', 'mongod'], capture_output=True)
                process_running = result.returncode == 0
                
            if process_running:
                print("✅ MongoDB进程正在运行")
            else:
                print("❌ MongoDB进程未运行")
                
        except Exception as e:
            print(f"⚠️ 无法检查MongoDB进程: {e}")
            process_running = False
            
        # 检查连接
        try:
            client = pymongo.MongoClient('mongodb://localhost:27017/', 
                                       serverSelectionTimeoutMS=3000)
            client.server_info()
            
            # 检查数据库
            db = client['house_data']
            collections = db.list_collection_names()
            
            if 'houses' in collections:
                house_count = db.houses.count_documents({})
                print(f"✅ MongoDB连接正常，房源数据: {house_count}条")
            else:
                print("⚠️ MongoDB连接正常，但缺少房源数据")
                
            if 'users' in collections:
                user_count = db.users.count_documents({})
                print(f"✅ 用户数据: {user_count}条")
            else:
                print("⚠️ 缺少用户数据")
                
            self.status['mongodb'] = True
            client.close()
            
        except Exception as e:
            print(f"❌ MongoDB连接失败: {e}")
            self.status['mongodb'] = False
            
        print()
        
    def check_mysql_status(self):
        """检查MySQL状态"""
        print("🐬 [3/7] 检查MySQL状态...")
        print("-" * 40)
        
        try:
            conn = pymysql.connect(
                host='localhost',
                user='root',
                password='123456',
                database='guangzhou_house',
                charset='utf8mb4'
            )
            
            cursor = conn.cursor()
            
            # 检查表
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            if 'House' in tables:
                cursor.execute("SELECT COUNT(*) FROM House")
                house_count = cursor.fetchone()[0]
                print(f"✅ MySQL连接正常，房源数据: {house_count}条")
            else:
                print("⚠️ MySQL连接正常，但缺少House表")
                
            if 'User' in tables:
                cursor.execute("SELECT COUNT(*) FROM User")
                user_count = cursor.fetchone()[0]
                print(f"✅ 用户数据: {user_count}条")
            else:
                print("⚠️ 缺少User表")
                
            self.status['mysql'] = True
            conn.close()
            
        except Exception as e:
            print(f"❌ MySQL连接失败: {e}")
            self.status['mysql'] = False
            
        print()
        
    def check_django_status(self):
        """检查Django状态"""
        print("🌐 [4/7] 检查Django状态...")
        print("-" * 40)
        
        # 检查项目文件
        if os.path.exists('manage.py'):
            print("✅ Django项目文件存在")
        else:
            print("❌ Django项目文件缺失")
            return
            
        # 检查应用
        apps = ['app', 'app_mongo']
        for app in apps:
            if os.path.exists(app):
                print(f"✅ Django应用 {app} 存在")
            else:
                print(f"❌ Django应用 {app} 缺失")
                
        # 检查模板
        if os.path.exists('templates'):
            print("✅ 模板目录存在")
        else:
            print("❌ 模板目录缺失")
            
        # 检查静态文件
        if os.path.exists('static'):
            print("✅ 静态文件目录存在")
        else:
            print("❌ 静态文件目录缺失")
            
        # 尝试访问Django服务器
        try:
            response = requests.get('http://127.0.0.1:8000/mongo/login/', timeout=5)
            if response.status_code == 200:
                print("✅ Django服务器正在运行")
                self.status['django'] = True
            else:
                print(f"⚠️ Django服务器响应异常: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Django服务器未运行")
        except Exception as e:
            print(f"⚠️ Django服务器检查失败: {e}")
            
        print()
        
    def check_rag_status(self):
        """检查RAG系统状态"""
        print("🤖 [5/7] 检查RAG智能问答系统...")
        print("-" * 40)
        
        # 检查RAG模块目录
        if os.path.exists('rag_module'):
            print("✅ RAG模块目录存在")
            
            # 检查配置文件
            if os.path.exists('rag_module/config.py'):
                print("✅ RAG配置文件存在")
            else:
                print("❌ RAG配置文件缺失")
                
            # 检查API密钥
            if os.path.exists('rag_module/api_keys.json'):
                print("✅ API密钥配置存在")
            else:
                print("⚠️ API密钥配置缺失")
                
            # 检查向量数据库
            if os.path.exists('rag_module/vector_db'):
                vector_files = os.listdir('rag_module/vector_db')
                if vector_files:
                    print(f"✅ 向量数据库存在 ({len(vector_files)}个文件)")
                else:
                    print("⚠️ 向量数据库为空")
            else:
                print("❌ 向量数据库目录缺失")
                
        else:
            print("❌ RAG模块目录缺失")
            
        # 检查RAG页面访问
        try:
            response = requests.get('http://127.0.0.1:8000/mongo/rag/', timeout=5)
            if response.status_code == 200:
                print("✅ RAG页面可访问")
                self.status['rag'] = True
            else:
                print(f"⚠️ RAG页面响应异常: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ RAG页面无法访问 (Django服务器未运行)")
        except Exception as e:
            print(f"⚠️ RAG页面检查失败: {e}")
            
        print()
        
    def check_scrapy_status(self):
        """检查Scrapy爬虫状态"""
        print("🕷️ [6/7] 检查Scrapy爬虫状态...")
        print("-" * 40)
        
        # 检查Scrapy项目目录
        if os.path.exists('scrapy_spider'):
            print("✅ Scrapy项目目录存在")
            
            # 检查配置文件
            if os.path.exists('scrapy_spider/scrapy.cfg'):
                print("✅ Scrapy配置文件存在")
            else:
                print("❌ Scrapy配置文件缺失")
                
            # 检查爬虫文件
            spider_dir = 'scrapy_spider/house_spider/spiders'
            if os.path.exists(spider_dir):
                spiders = [f for f in os.listdir(spider_dir) if f.endswith('.py') and f != '__init__.py']
                if spiders:
                    print(f"✅ 爬虫文件存在: {', '.join(spiders)}")
                    self.status['scrapy'] = True
                else:
                    print("❌ 爬虫文件缺失")
            else:
                print("❌ 爬虫目录缺失")
                
            # 检查输出目录
            if os.path.exists('scrapy_spider/output'):
                print("✅ 输出目录存在")
            else:
                print("⚠️ 输出目录缺失")
                
        else:
            print("❌ Scrapy项目目录缺失")
            
        print()
        
    def check_system_resources(self):
        """检查系统资源"""
        print("💻 [7/7] 检查系统资源...")
        print("-" * 40)
        
        try:
            import psutil
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f"CPU使用率: {cpu_percent}%")
            
            # 内存使用率
            memory = psutil.virtual_memory()
            print(f"内存使用率: {memory.percent}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)")
            
            # 磁盘使用率
            disk = psutil.disk_usage('.')
            print(f"磁盘使用率: {disk.percent}% ({disk.used // 1024 // 1024 // 1024}GB / {disk.total // 1024 // 1024 // 1024}GB)")
            
        except ImportError:
            print("⚠️ psutil未安装，无法检查系统资源")
        except Exception as e:
            print(f"⚠️ 系统资源检查失败: {e}")
            
        print()
        
    def print_summary(self):
        """打印检查总结"""
        print("=" * 80)
        print("📊 系统状态总结")
        print("=" * 80)
        
        total_checks = 0
        passed_checks = 0
        
        # Python环境
        if self.status['python']:
            print("✅ Python环境: 正常")
            passed_checks += 1
        else:
            print("❌ Python环境: 异常")
        total_checks += 1
        
        # 依赖包
        dep_count = len(self.status['dependencies'])
        dep_passed = sum(self.status['dependencies'].values())
        print(f"📦 依赖包: {dep_passed}/{dep_count} 已安装")
        if dep_passed == dep_count:
            passed_checks += 1
        total_checks += 1
        
        # 数据库
        if self.status['mongodb']:
            print("✅ MongoDB: 正常")
            passed_checks += 1
        else:
            print("❌ MongoDB: 异常")
        total_checks += 1
        
        if self.status['mysql']:
            print("✅ MySQL: 正常")
            passed_checks += 1
        else:
            print("❌ MySQL: 异常")
        total_checks += 1
        
        # Web服务
        if self.status['django']:
            print("✅ Django Web服务器: 正常")
            passed_checks += 1
        else:
            print("❌ Django Web服务器: 异常")
        total_checks += 1
        
        # RAG系统
        if self.status['rag']:
            print("✅ RAG智能问答: 正常")
            passed_checks += 1
        else:
            print("❌ RAG智能问答: 异常")
        total_checks += 1
        
        # 爬虫系统
        if self.status['scrapy']:
            print("✅ Scrapy爬虫: 正常")
            passed_checks += 1
        else:
            print("❌ Scrapy爬虫: 异常")
        total_checks += 1
        
        print()
        print(f"🎯 总体状态: {passed_checks}/{total_checks} 项检查通过")
        
        if passed_checks == total_checks:
            print("🎉 系统状态良好，所有组件正常运行！")
        elif passed_checks >= total_checks * 0.8:
            print("⚠️ 系统基本正常，部分组件需要注意")
        else:
            print("❌ 系统存在较多问题，建议检查配置")
            
        print()
        
    def run(self):
        """运行检查"""
        self.print_header()
        self.check_python_environment()
        self.check_mongodb_status()
        self.check_mysql_status()
        self.check_django_status()
        self.check_rag_status()
        self.check_scrapy_status()
        self.check_system_resources()
        self.print_summary()

if __name__ == '__main__':
    checker = SystemStatusChecker()
    checker.run()
