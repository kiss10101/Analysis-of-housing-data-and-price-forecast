#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试所有页面的完整性
"""

import requests
import re
import sys

def test_all_pages():
    """测试所有页面"""
    print("🎯 房源数据分析系统 - 全页面测试")
    print("=" * 60)
    
    # MySQL版本完整测试
    print("\n🗄️ MySQL版本完整测试")
    print("-" * 40)
    
    mysql_session = requests.Session()
    
    # 登录MySQL版本
    try:
        login_page = mysql_session.get('http://127.0.0.1:8000/app/login/')
        csrf_token = None
        csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', login_page.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
        
        login_data = {'name': 'test4071741', 'password': '0515'}
        if csrf_token:
            login_data['csrfmiddlewaretoken'] = csrf_token
        
        login_response = mysql_session.post('http://127.0.0.1:8000/app/login/', data=login_data)
        
        if login_response.status_code in [200, 302]:
            print("✅ MySQL登录成功")
            
            # 测试所有MySQL页面
            mysql_pages = [
                ('首页', 'http://127.0.0.1:8000/app/index/'),
                ('数据表格', 'http://127.0.0.1:8000/app/tableData/'),
                ('收藏数据', 'http://127.0.0.1:8000/app/historyTableData/'),
                ('个人信息', 'http://127.0.0.1:8000/app/selfInfo/'),
                ('房源分布', 'http://127.0.0.1:8000/app/houseDistribute/'),
                ('户型占比', 'http://127.0.0.1:8000/app/housetyperank/'),
                ('词云汇总', 'http://127.0.0.1:8000/app/housewordcloud/'),
                ('房型排名', 'http://127.0.0.1:8000/app/typeincity/'),
                ('价钱影响', 'http://127.0.0.1:8000/app/servicemoney/'),
                ('热力图分析', 'http://127.0.0.1:8000/app/heatmap_analysis/'),
                ('房价预测', 'http://127.0.0.1:8000/app/pricePredict/'),
            ]
            
            mysql_success = 0
            for page_name, page_url in mysql_pages:
                try:
                    response = mysql_session.get(page_url, timeout=15)
                    if response.status_code == 200:
                        print(f"✅ {page_name}: 正常")
                        mysql_success += 1
                    elif response.status_code in [301, 302]:
                        print(f"⚠️ {page_name}: 重定向")
                    else:
                        print(f"❌ {page_name}: 失败 (状态码: {response.status_code})")
                except Exception as e:
                    print(f"❌ {page_name}: 异常 - {e}")
            
            print(f"\n📊 MySQL版本结果: {mysql_success}/{len(mysql_pages)} 个页面正常")
        else:
            print("❌ MySQL登录失败")
    except Exception as e:
        print(f"❌ MySQL测试异常: {e}")
    
    # MongoDB版本完整测试
    print("\n🍃 MongoDB版本完整测试")
    print("-" * 40)
    
    mongo_session = requests.Session()
    
    try:
        login_page = mongo_session.get('http://127.0.0.1:8000/mongo/login/')
        csrf_token = None
        csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', login_page.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
        
        login_data = {'username': 'test4071741', 'password': '0515'}
        if csrf_token:
            login_data['csrfmiddlewaretoken'] = csrf_token
        
        login_response = mongo_session.post('http://127.0.0.1:8000/mongo/login/', data=login_data)
        
        if login_response.status_code in [200, 302]:
            print("✅ MongoDB登录成功")
            
            # 测试所有MongoDB页面
            mongo_pages = [
                ('首页', 'http://127.0.0.1:8000/mongo/index/'),
                ('数据表格', 'http://127.0.0.1:8000/mongo/tableData/'),
                ('收藏数据', 'http://127.0.0.1:8000/mongo/historyTableData/'),
                ('个人信息', 'http://127.0.0.1:8000/mongo/selfInfo/'),
                ('房源分布', 'http://127.0.0.1:8000/mongo/houseDistribute/'),
                ('户型占比', 'http://127.0.0.1:8000/mongo/housetyperank/'),
                ('词云汇总', 'http://127.0.0.1:8000/mongo/housewordcloud/'),
                ('房型排名', 'http://127.0.0.1:8000/mongo/typeincity/'),
                ('价钱影响', 'http://127.0.0.1:8000/mongo/servicemoney/'),
                ('热力图分析', 'http://127.0.0.1:8000/mongo/heatmap_analysis/'),
                ('房价预测', 'http://127.0.0.1:8000/mongo/pricePredict/'),
            ]
            
            mongo_success = 0
            for page_name, page_url in mongo_pages:
                try:
                    response = mongo_session.get(page_url, timeout=15)
                    if response.status_code == 200:
                        print(f"✅ {page_name}: 正常")
                        mongo_success += 1
                    elif response.status_code in [301, 302]:
                        print(f"⚠️ {page_name}: 重定向")
                    else:
                        print(f"❌ {page_name}: 失败 (状态码: {response.status_code})")
                except Exception as e:
                    print(f"❌ {page_name}: 异常 - {e}")
            
            print(f"\n📊 MongoDB版本结果: {mongo_success}/{len(mongo_pages)} 个页面正常")
        else:
            print("❌ MongoDB登录失败")
    except Exception as e:
        print(f"❌ MongoDB测试异常: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 全页面测试完成！")

if __name__ == '__main__':
    test_all_pages()
