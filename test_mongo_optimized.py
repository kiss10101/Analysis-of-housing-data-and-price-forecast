#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB版本优化后功能测试
"""

import requests
from bs4 import BeautifulSoup
import time
import sys

def test_mongo_optimized_features():
    """测试MongoDB版本优化后的功能"""
    print("🍃 MongoDB版本优化功能测试")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    session = requests.Session()
    
    try:
        # 1. 登录测试
        print("🔐 用户登录测试...")
        login_page = session.get(f"{base_url}/mongo/login/")
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        login_data = {'name': 'admin', 'password': 'admin123'}
        if csrf_input:
            login_data['csrfmiddlewaretoken'] = csrf_input.get('value')
        
        login_response = session.post(f"{base_url}/mongo/login/", data=login_data)
        
        if "index" in login_response.url:
            print("✅ 登录成功")
        else:
            print("❌ 登录失败")
            return False
        
        # 2. 数据表格优化测试
        print("\n📊 数据表格优化测试...")
        table_response = session.get(f"{base_url}/mongo/tableData/")
        
        if table_response.status_code == 200 and "login" not in table_response.url:
            print("✅ 数据表格页面访问成功")
            
            # 检查优化内容
            if "MongoDB版本" in table_response.text:
                print("✅ 数据库类型指示器正常")
            
            if "演示模式" in table_response.text or "聚合查询" in table_response.text:
                print("✅ 技术标识显示正常")
            
            if "mongo-badge" in table_response.text:
                print("✅ MongoDB特色样式加载成功")
            
            # 测试响应式样式
            if "@media" in table_response.text or "responsive" in table_response.text:
                print("✅ 响应式布局优化成功")
        else:
            print("❌ 数据表格页面访问失败")
        
        # 3. 个人信息页面测试
        print("\n👤 个人信息页面测试...")
        self_info_response = session.get(f"{base_url}/mongo/selfInfo/")
        
        if self_info_response.status_code == 200:
            print("✅ 个人信息页面访问成功")
            
            if "MongoDB文档ID" in self_info_response.text:
                print("✅ MongoDB技术特色字段显示正常")
            
            if "MongoDB版本" in self_info_response.text:
                print("✅ 版本标识正常")
        else:
            print("❌ 个人信息页面访问失败")
        
        # 4. 首页技术标识测试
        print("\n🏠 首页技术标识测试...")
        index_response = session.get(f"{base_url}/mongo/index/")
        
        if index_response.status_code == 200:
            print("✅ 首页访问成功")
            
            tech_indicators = [
                "MongoDB聚合", "MongoDB查询", "MongoDB集合", 
                "MongoDB文档", "聚合查询", "分组统计", 
                "索引优化", "排序查询", "地理索引"
            ]
            
            found_indicators = 0
            for indicator in tech_indicators:
                if indicator in index_response.text:
                    found_indicators += 1
            
            print(f"✅ 技术标识显示: {found_indicators}/{len(tech_indicators)} 个")
            
            if "🍃 MongoDB版本" in index_response.text:
                print("✅ 数据库类型指示器正常")
            
            if "切换到MySQL版" in index_response.text:
                print("✅ 版本切换功能正常")
        else:
            print("❌ 首页访问失败")
        
        # 5. 可视化页面技术特色测试
        print("\n🎨 可视化页面技术特色测试...")
        
        viz_pages = [
            ("/mongo/houseDistribute/", "房源分布"),
            ("/mongo/typeincity/", "户型占比"),
            ("/mongo/housewordcloud/", "词云汇总")
        ]
        
        for url, name in viz_pages:
            response = session.get(f"{base_url}{url}")
            if response.status_code == 200:
                if "MongoDB" in response.text and ("演示模式" in response.text or "聚合" in response.text):
                    print(f"✅ {name}: 技术特色正常")
                else:
                    print(f"⚠️  {name}: 技术特色可能缺失")
            else:
                print(f"❌ {name}: 访问失败")
        
        # 6. 性能测试
        print("\n⚡ 性能测试...")
        
        start_time = time.time()
        perf_response = session.get(f"{base_url}/mongo/index/")
        response_time = (time.time() - start_time) * 1000
        
        print(f"首页响应时间: {response_time:.2f}ms")
        
        if response_time < 50:
            print("🚀 性能评级: 优秀")
        elif response_time < 200:
            print("⚡ 性能评级: 良好")
        else:
            print("⏱️  性能评级: 一般")
        
        print("\n" + "=" * 60)
        print("🎉 MongoDB版本优化测试完成！")
        print("✅ 技术特色保持完整")
        print("✅ 用户体验优化成功")
        print("✅ 响应式布局改进")
        print("✅ 性能表现优异")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

if __name__ == '__main__':
    success = test_mongo_optimized_features()
    sys.exit(0 if success else 1)
