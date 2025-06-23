#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的tableData页面
"""

import requests
import re

def test_tabledata_fix():
    """测试修复后的tableData页面"""
    base_url = 'http://127.0.0.1:8000'
    session = requests.Session()
    
    print('🧪 测试修复后的tableData页面...')
    
    try:
        # 1. 登录
        login_url = base_url + '/mongo/login/'
        response = session.get(login_url)
        
        csrf_pattern = r'name="csrfmiddlewaretoken" value="([^"]+)"'
        csrf_match = re.search(csrf_pattern, response.text)
        
        login_data = {
            'name': 'admin',
            'password': 'admin123'
        }
        
        if csrf_match:
            login_data['csrfmiddlewaretoken'] = csrf_match.group(1)
        
        response = session.post(login_url, data=login_data)
        print(f'登录状态: {response.status_code}')
        
        if response.status_code == 302:
            # 2. 测试tableData页面
            table_url = base_url + '/mongo/tableData/'
            response = session.get(table_url)
            print(f'tableData页面: {response.status_code}')
            
            if response.status_code == 200:
                print('✅ tableData页面访问成功')
                
                # 检查页面内容
                if 'MongoDB' in response.text:
                    print('✅ 页面包含MongoDB标识')
                
                if '房源类型' in response.text:
                    print('✅ 页面包含房源类型列')
                    
                if 'rental_type' in response.text:
                    print('✅ 页面使用正确的字段名')
                    
                return True
            else:
                print(f'❌ tableData页面访问失败: {response.status_code}')
                print('错误内容:', response.text[:500])
                return False
        else:
            print('❌ 登录失败')
            return False
            
    except Exception as e:
        print(f'❌ 测试过程中出错: {e}')
        return False

def test_favicon():
    """测试favicon.ico"""
    base_url = 'http://127.0.0.1:8000'
    
    print('\n🎨 测试favicon.ico...')
    
    try:
        favicon_url = base_url + '/favicon.ico'
        response = requests.get(favicon_url)
        print(f'favicon.ico: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ favicon.ico访问成功')
            return True
        elif response.status_code == 302:
            print('✅ favicon.ico重定向正常')
            return True
        else:
            print(f'❌ favicon.ico访问失败: {response.status_code}')
            return False
            
    except Exception as e:
        print(f'❌ favicon.ico测试出错: {e}')
        return False

if __name__ == "__main__":
    print("🔧 MongoDB版本tableData页面修复测试")
    print("=" * 50)
    
    # 测试tableData页面
    tabledata_ok = test_tabledata_fix()
    
    # 测试favicon
    favicon_ok = test_favicon()
    
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    print(f"tableData页面: {'✅ 正常' if tabledata_ok else '❌ 异常'}")
    print(f"favicon.ico: {'✅ 正常' if favicon_ok else '❌ 异常'}")
    
    if tabledata_ok and favicon_ok:
        print("\n🎉 所有修复测试通过！")
        print("💡 浏览器控制台错误应该已经完全消除")
    else:
        print("\n⚠️  部分功能仍有问题，需要进一步检查")
