#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整的前端页面测试
"""

import requests
import re
import sys

def test_complete_frontend():
    """完整测试前端功能"""
    session = requests.Session()
    
    print("🎯 房源数据分析系统 - 完整前端测试")
    print("=" * 60)
    
    # 测试基本页面访问
    print("\n📄 基础页面访问测试")
    print("-" * 40)
    
    basic_pages = [
        ('MySQL登录页面', 'http://127.0.0.1:8000/app/login/'),
        ('MongoDB登录页面', 'http://127.0.0.1:8000/mongo/login/'),
        ('根路径', 'http://127.0.0.1:8000/'),
    ]
    
    for name, url in basic_pages:
        try:
            response = session.get(url, timeout=10)
            if response.status_code in [200, 301, 302]:
                print(f"✅ {name}: 正常 (状态码: {response.status_code})")
            else:
                print(f"❌ {name}: 失败 (状态码: {response.status_code})")
        except Exception as e:
            print(f"❌ {name}: 异常 - {e}")
    
    # 测试MongoDB版本登录和功能
    print("\n🍃 MongoDB版本功能测试")
    print("-" * 40)
    
    try:
        # 获取登录页面和CSRF令牌
        login_page = session.get('http://127.0.0.1:8000/mongo/login/')
        if login_page.status_code == 200:
            print("✅ 获取MongoDB登录页面成功")
            
            # 提取CSRF令牌
            csrf_token = None
            csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', login_page.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print("✅ 提取CSRF令牌成功")
            else:
                print("⚠️ 未找到CSRF令牌，尝试无令牌登录")
            
            # 准备登录数据
            login_data = {
                'username': 'test4071741',
                'password': '0515'
            }
            if csrf_token:
                login_data['csrfmiddlewaretoken'] = csrf_token
            
            # 尝试登录
            login_response = session.post('http://127.0.0.1:8000/mongo/login/', data=login_data)
            
            if login_response.status_code in [200, 302]:
                print("✅ MongoDB登录成功")
                
                # 测试登录后的页面
                protected_pages = [
                    ('首页', 'http://127.0.0.1:8000/mongo/index/'),
                    ('个人信息', 'http://127.0.0.1:8000/mongo/selfInfo/'),
                    ('房源分布', 'http://127.0.0.1:8000/mongo/houseDistribute/'),
                    ('户型占比', 'http://127.0.0.1:8000/mongo/housetyperank/'),
                    ('词云汇总', 'http://127.0.0.1:8000/mongo/housewordcloud/'),
                    ('房型排名', 'http://127.0.0.1:8000/mongo/typeincity/'),
                    ('价钱影响', 'http://127.0.0.1:8000/mongo/servicemoney/'),
                    ('热力图分析', 'http://127.0.0.1:8000/mongo/heatmap_analysis/'),
                    ('房价预测', 'http://127.0.0.1:8000/mongo/pricePredict/'),
                    ('数据表格', 'http://127.0.0.1:8000/mongo/tableData/'),
                ]
                
                success_count = 0
                for page_name, page_url in protected_pages:
                    try:
                        page_response = session.get(page_url, timeout=15)
                        if page_response.status_code == 200:
                            print(f"✅ {page_name}: 访问成功")
                            success_count += 1
                        elif page_response.status_code in [301, 302]:
                            print(f"⚠️ {page_name}: 重定向")
                        else:
                            print(f"❌ {page_name}: 失败 (状态码: {page_response.status_code})")
                    except Exception as e:
                        print(f"❌ {page_name}: 异常 - {e}")
                
                print(f"\n📊 MongoDB版本测试结果: {success_count}/{len(protected_pages)} 个页面正常")
                
            else:
                print(f"❌ MongoDB登录失败 (状态码: {login_response.status_code})")
                
        else:
            print(f"❌ 获取MongoDB登录页面失败 (状态码: {login_page.status_code})")
            
    except Exception as e:
        print(f"❌ MongoDB版本测试异常: {e}")
    
    # 测试MySQL版本
    print("\n🗄️ MySQL版本功能测试")
    print("-" * 40)
    
    try:
        # 重新创建session以避免冲突
        mysql_session = requests.Session()
        
        # 获取MySQL登录页面
        mysql_login_page = mysql_session.get('http://127.0.0.1:8000/app/login/')
        if mysql_login_page.status_code == 200:
            print("✅ 获取MySQL登录页面成功")
            
            # 提取CSRF令牌
            csrf_token = None
            csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', mysql_login_page.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
            
            # 准备登录数据
            mysql_login_data = {
                'name': 'test4071741',
                'password': '0515'
            }
            if csrf_token:
                mysql_login_data['csrfmiddlewaretoken'] = csrf_token
            
            # 尝试登录
            mysql_login_response = mysql_session.post('http://127.0.0.1:8000/app/login/', data=mysql_login_data)
            
            if mysql_login_response.status_code in [200, 302]:
                print("✅ MySQL登录成功")
                
                # 测试几个关键页面
                mysql_pages = [
                    ('首页', 'http://127.0.0.1:8000/app/index/'),
                    ('数据表格', 'http://127.0.0.1:8000/app/tableData/'),
                    ('个人信息', 'http://127.0.0.1:8000/app/selfInfo/'),
                ]
                
                mysql_success = 0
                for page_name, page_url in mysql_pages:
                    try:
                        page_response = mysql_session.get(page_url, timeout=10)
                        if page_response.status_code == 200:
                            print(f"✅ {page_name}: 访问成功")
                            mysql_success += 1
                        else:
                            print(f"❌ {page_name}: 失败 (状态码: {page_response.status_code})")
                    except Exception as e:
                        print(f"❌ {page_name}: 异常 - {e}")
                
                print(f"\n📊 MySQL版本测试结果: {mysql_success}/{len(mysql_pages)} 个页面正常")
                
            else:
                print(f"❌ MySQL登录失败 (状态码: {mysql_login_response.status_code})")
        else:
            print(f"❌ 获取MySQL登录页面失败")
            
    except Exception as e:
        print(f"❌ MySQL版本测试异常: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 前端测试完成！")

if __name__ == '__main__':
    test_complete_frontend()
