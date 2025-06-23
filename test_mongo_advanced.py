#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB版本高级功能测试
"""

import requests
from bs4 import BeautifulSoup
import sys

def test_advanced_mongo_features():
    """测试MongoDB版本高级功能"""
    print("🍃 MongoDB版本高级功能测试")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    session = requests.Session()
    
    try:
        # 登录
        login_page = session.get(f"{base_url}/mongo/login/")
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        login_data = {
            'name': 'admin',
            'password': 'admin123'
        }
        if csrf_input:
            login_data['csrfmiddlewaretoken'] = csrf_input.get('value')
        
        session.post(f"{base_url}/mongo/login/", data=login_data)
        
        # 测试高级可视化页面
        advanced_pages = [
            ("/mongo/housewordcloud/", "词云汇总"),
            ("/mongo/housetyperank/", "房型级别"),
            ("/mongo/servicemoney/", "价钱影响"),
            ("/mongo/heatmap-analysis/", "热力图分析"),
            ("/mongo/predict-all-prices/", "房价预测")
        ]
        
        print("🎨 高级可视化功能测试:")
        for url, name in advanced_pages:
            try:
                response = session.get(f"{base_url}{url}")
                if response.status_code == 200:
                    print(f"✅ {name}: 正常")
                else:
                    print(f"❌ {name}: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ {name}: 错误 - {e}")
        
        # 测试数据API
        print("\n📊 数据API测试:")
        try:
            api_response = session.get(f"{base_url}/mongo/api/tableData/?draw=1&start=0&length=10")
            if api_response.status_code == 200:
                print("✅ 数据表格API: 正常")
            else:
                print(f"❌ 数据表格API: HTTP {api_response.status_code}")
        except Exception as e:
            print(f"❌ 数据表格API: 错误 - {e}")
        
        # 测试收藏功能
        print("\n⭐ 收藏功能测试:")
        try:
            history_response = session.get(f"{base_url}/mongo/historyTableData/")
            if history_response.status_code == 200:
                print("✅ 收藏历史页面: 正常")
            else:
                print(f"❌ 收藏历史页面: HTTP {history_response.status_code}")
        except Exception as e:
            print(f"❌ 收藏历史页面: 错误 - {e}")
        
        # 测试注册功能
        print("\n👤 用户注册测试:")
        try:
            register_page = session.get(f"{base_url}/mongo/register/")
            soup = BeautifulSoup(register_page.text, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
            
            register_data = {
                'name': f'testuser_{int(time.time())}',
                'password': 'test123',
                'phone': '13800138999',
                'email': 'test@example.com'
            }
            if csrf_input:
                register_data['csrfmiddlewaretoken'] = csrf_input.get('value')
            
            register_response = session.post(f"{base_url}/mongo/register/", data=register_data)
            if register_response.status_code == 200:
                if "注册成功" in register_response.text:
                    print("✅ 用户注册: 成功")
                else:
                    print("⚠️  用户注册: 可能有问题")
            else:
                print(f"❌ 用户注册: HTTP {register_response.status_code}")
        except Exception as e:
            print(f"❌ 用户注册: 错误 - {e}")
        
        print("\n" + "=" * 60)
        print("🎉 MongoDB版本高级功能测试完成！")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

if __name__ == '__main__':
    import time
    success = test_advanced_mongo_features()
    sys.exit(0 if success else 1)
