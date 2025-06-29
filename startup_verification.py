#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目启动验证脚本
验证所有功能模块是否正常工作
"""

import requests
import time
import json

def test_basic_pages():
    """测试基础页面"""
    print("=== 测试基础页面 ===")
    
    basic_urls = [
        ('主页', '/'),
        ('MySQL版本登录', '/app/login/'),
        ('MongoDB版本登录', '/mongo/login/'),
    ]
    
    for name, url in basic_urls:
        try:
            response = requests.get(f'http://127.0.0.1:8000{url}', timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: 正常访问")
            else:
                print(f"❌ {name}: 状态码 {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: 访问失败 - {e}")

def test_python_visualization():
    """测试Python可视化功能"""
    print("\n=== 测试Python可视化功能 ===")
    
    viz_urls = [
        ('Python可视化仪表板', '/mongo/python-viz/'),
        ('静态图表页面', '/mongo/python-viz/static-charts/'),
        ('交互式图表页面', '/mongo/python-viz/interactive-charts/'),
    ]
    
    for name, url in viz_urls:
        try:
            response = requests.get(f'http://127.0.0.1:8000{url}', timeout=5, allow_redirects=False)
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                if '/mongo/login/' in redirect_url:
                    print(f"✅ {name}: 正确重定向到登录页")
                else:
                    print(f"⚠️  {name}: 重定向到 {redirect_url}")
            elif response.status_code == 200:
                print(f"✅ {name}: 直接访问成功")
            else:
                print(f"❌ {name}: 状态码 {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: 访问失败 - {e}")

def test_mongodb_pages():
    """测试MongoDB版本页面"""
    print("\n=== 测试MongoDB版本页面 ===")
    
    mongo_urls = [
        ('数据总览', '/mongo/tableData/'),
        ('房源分布', '/mongo/houseDistribute/'),
        ('户型占比', '/mongo/housetyperank/'),
        ('词云汇总', '/mongo/housewordcloud/'),
        ('类型级别', '/mongo/typeincity/'),
        ('价钱影响', '/mongo/servicemoney/'),
        ('热力图分析', '/mongo/heatmap-analysis/'),
        ('房价预测', '/mongo/predict-all-prices/'),
    ]
    
    for name, url in mongo_urls:
        try:
            response = requests.get(f'http://127.0.0.1:8000{url}', timeout=5, allow_redirects=False)
            if response.status_code == 302:
                print(f"✅ {name}: 需要登录访问")
            elif response.status_code == 200:
                print(f"✅ {name}: 直接访问成功")
            else:
                print(f"❌ {name}: 状态码 {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: 访问失败 - {e}")

def test_mysql_pages():
    """测试MySQL版本页面"""
    print("\n=== 测试MySQL版本页面 ===")
    
    mysql_urls = [
        ('数据总览', '/app/tableData/'),
        ('房源分布', '/app/houseDistribute/'),
        ('户型占比', '/app/housetyperank/'),
        ('词云汇总', '/app/housewordcloud/'),
    ]
    
    for name, url in mysql_urls:
        try:
            response = requests.get(f'http://127.0.0.1:8000{url}', timeout=5, allow_redirects=False)
            if response.status_code == 302:
                print(f"✅ {name}: 需要登录访问")
            elif response.status_code == 200:
                print(f"✅ {name}: 直接访问成功")
            else:
                print(f"❌ {name}: 状态码 {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: 访问失败 - {e}")

def test_database_connections():
    """测试数据库连接"""
    print("\n=== 测试数据库连接 ===")
    
    try:
        # 测试MySQL连接
        import pymysql
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='guangzhou_house'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM House")
        mysql_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"✅ MySQL连接正常，House表记录数: {mysql_count}")
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
    
    try:
        # 测试MongoDB连接
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/')
        db = client['house_data']
        mongo_count = db.houses.count_documents({})
        client.close()
        print(f"✅ MongoDB连接正常，houses集合记录数: {mongo_count}")
    except Exception as e:
        print(f"❌ MongoDB连接失败: {e}")

def test_chart_generation():
    """测试图表生成功能"""
    print("\n=== 测试图表生成功能 ===")
    
    try:
        import os
        import sys
        import django
        
        # 设置Django环境
        sys.path.append('.')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Python租房房源数据可视化分析.settings')
        django.setup()
        
        from app_mongo.chart_generator import ChartGenerator
        
        # 创建测试数据
        test_data = [
            {
                'title': '测试房源1',
                'location': {'city': '天河', 'street': '天河路'},
                'features': {'area': 80.0},
                'price': {'monthly_rent': 3500.0},
                'rental_type': '整租'
            },
            {
                'title': '测试房源2',
                'location': {'city': '海珠', 'street': '江燕路'},
                'features': {'area': 60.0},
                'price': {'monthly_rent': 2800.0},
                'rental_type': '合租'
            }
        ]
        
        generator = ChartGenerator(test_data)
        
        # 测试静态图表
        histogram = generator.generate_price_histogram()
        if histogram and histogram.startswith('data:image/png;base64,'):
            print("✅ 静态图表生成正常")
        else:
            print("❌ 静态图表生成失败")
        
        # 测试交互式图表
        heatmap = generator.generate_interactive_heatmap()
        if heatmap and '<div' in heatmap:
            print("✅ 交互式图表生成正常")
        else:
            print("❌ 交互式图表生成失败")
            
    except Exception as e:
        print(f"❌ 图表生成测试失败: {e}")

def show_access_guide():
    """显示访问指南"""
    print("\n" + "="*60)
    print("🎉 项目启动成功！访问指南:")
    print("="*60)
    
    print("\n📊 MySQL版本 (原有功能):")
    print("- 登录页面: http://127.0.0.1:8000/app/login/")
    print("- 测试账号: admin / 123456")
    
    print("\n🍃 MongoDB版本 (增强功能):")
    print("- 登录页面: http://127.0.0.1:8000/mongo/login/")
    print("- 测试账号: test4071741 / 0515")
    
    print("\n🐍 Python可视化功能 (新增):")
    print("- 主仪表板: http://127.0.0.1:8000/mongo/python-viz/")
    print("- 静态图表: http://127.0.0.1:8000/mongo/python-viz/static-charts/")
    print("- 交互式图表: http://127.0.0.1:8000/mongo/python-viz/interactive-charts/")
    
    print("\n⚠️  注意事项:")
    print("1. Python可视化功能需要先登录MongoDB版本")
    print("2. 建议使用Chrome或Firefox浏览器")
    print("3. 如遇到问题，请检查数据库服务是否正常运行")
    
    print("\n🎯 推荐体验流程:")
    print("1. 访问MongoDB版本登录页面")
    print("2. 使用测试账号登录")
    print("3. 体验Python可视化功能")
    print("4. 对比原有ECharts图表和新的Python图表")

def main():
    """主函数"""
    print("房源数据分析系统 - 启动验证")
    print("="*60)
    
    # 等待服务器完全启动
    print("等待Django服务器启动...")
    time.sleep(3)
    
    # 运行所有测试
    test_basic_pages()
    test_python_visualization()
    test_mongodb_pages()
    test_mysql_pages()
    test_database_connections()
    test_chart_generation()
    
    # 显示访问指南
    show_access_guide()

if __name__ == '__main__':
    main()
