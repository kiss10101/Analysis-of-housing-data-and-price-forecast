#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试前端页面访问
"""

import requests
import sys

def test_page_access():
    """测试页面访问"""
    session = requests.Session()
    
    print("🧪 测试前端页面访问")
    print("=" * 50)
    
    # 测试基本页面访问
    pages_to_test = [
        ('MySQL登录页面', 'http://127.0.0.1:8000/app/login/'),
        ('MongoDB登录页面', 'http://127.0.0.1:8000/mongo/login/'),
        ('根路径重定向', 'http://127.0.0.1:8000/'),
    ]
    
    success_count = 0
    total_count = len(pages_to_test)
    
    for name, url in pages_to_test:
        try:
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: 正常访问 (状态码: {response.status_code})")
                success_count += 1
            elif response.status_code in [301, 302]:
                print(f"✅ {name}: 重定向正常 (状态码: {response.status_code})")
                success_count += 1
            else:
                print(f"❌ {name}: 访问失败 (状态码: {response.status_code})")
        except Exception as e:
            print(f"❌ {name}: 连接失败 - {e}")
    
    print("=" * 50)
    print(f"测试结果: {success_count}/{total_count} 个页面正常")
    
    # 测试MongoDB登录功能
    print("\n🔐 测试MongoDB登录功能")
    print("=" * 50)
    
    try:
        # 获取登录页面
        login_response = session.get('http://127.0.0.1:8000/mongo/login/')
        if login_response.status_code == 200:
            print("✅ 获取登录页面成功")
            
            # 尝试登录
            login_data = {
                'username': 'test4071741',
                'password': '0515'
            }
            
            post_response = session.post('http://127.0.0.1:8000/mongo/login/', data=login_data)
            if post_response.status_code in [200, 302]:
                print("✅ 登录请求成功")
                
                # 测试登录后的页面
                protected_pages = [
                    ('首页', 'http://127.0.0.1:8000/mongo/index/'),
                    ('数据表格', 'http://127.0.0.1:8000/mongo/tableData/'),
                    ('个人信息', 'http://127.0.0.1:8000/mongo/selfInfo/'),
                ]
                
                for page_name, page_url in protected_pages:
                    try:
                        page_response = session.get(page_url, timeout=10)
                        if page_response.status_code == 200:
                            print(f"✅ {page_name}: 访问成功")
                        elif page_response.status_code in [301, 302]:
                            print(f"⚠️ {page_name}: 重定向到登录页面")
                        else:
                            print(f"❌ {page_name}: 访问失败 (状态码: {page_response.status_code})")
                    except Exception as e:
                        print(f"❌ {page_name}: 访问异常 - {e}")
            else:
                print(f"❌ 登录失败 (状态码: {post_response.status_code})")
        else:
            print(f"❌ 获取登录页面失败 (状态码: {login_response.status_code})")
            
    except Exception as e:
        print(f"❌ 登录测试异常: {e}")
    
    print("=" * 50)
    print("测试完成")

if __name__ == '__main__':
    test_page_access()
