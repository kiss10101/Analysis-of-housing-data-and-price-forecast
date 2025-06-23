#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MongoDB版本登录功能
"""

import requests
import sys

def test_mongo_login():
    """测试MongoDB版本登录"""
    print("🍃 测试MongoDB版本登录功能")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # 创建会话
    session = requests.Session()
    
    try:
        # 1. 获取登录页面
        print("1. 获取登录页面...")
        login_page = session.get(f"{base_url}/mongo/login/")
        if login_page.status_code == 200:
            print("✅ 登录页面访问成功")
        else:
            print(f"❌ 登录页面访问失败: {login_page.status_code}")
            return False
        
        # 2. 尝试登录（降级模式用户）
        print("\n2. 尝试登录（降级模式）...")
        login_data = {
            'name': 'admin',
            'password': 'admin123'
        }
        
        # 获取CSRF token
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        if csrf_input:
            login_data['csrfmiddlewaretoken'] = csrf_input.get('value')
            print(f"✅ 获取CSRF token: {csrf_input.get('value')[:10]}...")
        else:
            print("⚠️  未找到CSRF token")
        
        login_response = session.post(f"{base_url}/mongo/login/", data=login_data)
        
        if login_response.status_code == 200:
            if "index" in login_response.url or login_response.url.endswith("/mongo/index/"):
                print("✅ 登录成功，重定向到首页")
                
                # 3. 测试首页访问
                print("\n3. 测试首页访问...")
                index_response = session.get(f"{base_url}/mongo/index/")
                if index_response.status_code == 200:
                    print("✅ 首页访问成功")
                    
                    # 检查是否包含用户名
                    if 'admin' in index_response.text:
                        print("✅ 用户信息显示正常")
                    else:
                        print("⚠️  用户信息可能有问题")
                        
                    # 4. 测试数据表格页面
                    print("\n4. 测试数据表格页面...")
                    table_response = session.get(f"{base_url}/mongo/tableData/")
                    if table_response.status_code == 200:
                        print("✅ 数据表格页面访问成功")
                        
                        # 检查是否包含房源数据
                        if '房源' in table_response.text or 'house' in table_response.text.lower():
                            print("✅ 房源数据显示正常")
                        else:
                            print("⚠️  房源数据可能有问题")
                    else:
                        print(f"❌ 数据表格页面访问失败: {table_response.status_code}")
                        
                else:
                    print(f"❌ 首页访问失败: {index_response.status_code}")
                    
            else:
                print("❌ 登录失败，未重定向到首页")
                print(f"当前URL: {login_response.url}")
                print(f"响应状态码: {login_response.status_code}")

                # 检查响应内容中的错误信息
                if "信息错误" in login_response.text:
                    print("原因: 用户名或密码错误")
                elif "连接失败" in login_response.text:
                    print("原因: 数据库连接失败")
                elif "演示模式" in login_response.text:
                    print("原因: 演示模式登录失败")
                else:
                    print("原因: 未知错误")
                    # 输出部分响应内容用于调试
                    print("响应内容片段:")
                    print(login_response.text[:500])
                return False
        else:
            print(f"❌ 登录请求失败: {login_response.status_code}")
            return False
            
        print("\n" + "=" * 50)
        print("🎉 MongoDB版本功能测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

if __name__ == '__main__':
    success = test_mongo_login()
    sys.exit(0 if success else 1)
