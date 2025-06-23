#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试收藏数据页面
"""

import requests
import re

def test_history_page():
    """测试收藏数据页面"""
    session = requests.Session()
    
    print("🧪 测试MongoDB收藏数据页面")
    print("=" * 40)
    
    try:
        # 登录MongoDB版本
        login_page = session.get('http://127.0.0.1:8000/mongo/login/')
        csrf_token = None
        csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', login_page.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
        
        login_data = {'username': 'test4071741', 'password': '0515'}
        if csrf_token:
            login_data['csrfmiddlewaretoken'] = csrf_token
        
        login_response = session.post('http://127.0.0.1:8000/mongo/login/', data=login_data)
        
        if login_response.status_code in [200, 302]:
            print("✅ MongoDB登录成功")
            
            # 测试收藏数据页面
            history_response = session.get('http://127.0.0.1:8000/mongo/historyTableData/')
            if history_response.status_code == 200:
                print("✅ 收藏数据页面访问成功")
                print(f"页面大小: {len(history_response.content)} bytes")
            else:
                print(f"❌ 收藏数据页面访问失败: {history_response.status_code}")
        else:
            print("❌ 登录失败")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == '__main__':
    test_history_page()
