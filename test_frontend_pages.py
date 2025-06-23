#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端页面访问测试
测试Django服务器和前端页面是否正常工作
"""

import requests
import time
from datetime import datetime

def test_page_access():
    """测试页面访问"""
    base_url = "http://127.0.0.1:8000"
    
    # 测试页面列表
    test_pages = [
        ("/", "主页"),
        ("/app/login/", "MySQL版本登录页"),
        ("/mongo/login/", "MongoDB版本登录页"),
        ("/admin/", "管理后台"),
    ]
    
    print("🌐 前端页面访问测试")
    print("=" * 50)
    print(f"测试时间: {datetime.now()}")
    print(f"服务器地址: {base_url}")
    print()
    
    success_count = 0
    total_count = len(test_pages)
    
    for url, name in test_pages:
        try:
            full_url = base_url + url
            print(f"测试 {name}: {full_url}")
            
            start_time = time.time()
            response = requests.get(full_url, timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                print(f"✅ {name}: 访问成功 ({response_time:.2f}ms)")
                success_count += 1
            elif response.status_code == 302:
                print(f"✅ {name}: 重定向正常 ({response_time:.2f}ms)")
                success_count += 1
            else:
                print(f"❌ {name}: HTTP {response.status_code} ({response_time:.2f}ms)")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: 连接失败 - 服务器未启动")
        except requests.exceptions.Timeout:
            print(f"❌ {name}: 请求超时")
        except Exception as e:
            print(f"❌ {name}: 错误 - {str(e)}")
        
        print()
    
    print("=" * 50)
    print(f"测试结果: {success_count}/{total_count} 页面正常")
    
    if success_count == total_count:
        print("🎉 所有页面访问正常！")
        return True
    else:
        print("⚠️  部分页面访问异常")
        return False

def test_mongodb_pages():
    """专门测试MongoDB版本页面"""
    base_url = "http://127.0.0.1:8000"
    
    # MongoDB版本页面
    mongo_pages = [
        ("/mongo/login/", "MongoDB登录页"),
        ("/mongo/", "MongoDB首页"),
        ("/mongo/tableData/", "MongoDB数据表格"),
        ("/mongo/houseDistribute/", "MongoDB房源分布"),
        ("/mongo/housetyperank/", "MongoDB户型占比"),
        ("/mongo/housewordcloud/", "MongoDB词云汇总"),
    ]
    
    print("\n🍃 MongoDB版本页面专项测试")
    print("=" * 50)
    
    success_count = 0
    total_count = len(mongo_pages)
    
    for url, name in mongo_pages:
        try:
            full_url = base_url + url
            print(f"测试 {name}: {full_url}")
            
            start_time = time.time()
            response = requests.get(full_url, timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code in [200, 302]:
                print(f"✅ {name}: 正常 ({response_time:.2f}ms)")
                success_count += 1
                
                # 检查是否包含MongoDB特色标识
                if response.status_code == 200:
                    content = response.text
                    if "MongoDB" in content or "mongo" in content:
                        print(f"   🍃 包含MongoDB标识")
                    else:
                        print(f"   ⚠️  未检测到MongoDB标识")
            else:
                print(f"❌ {name}: HTTP {response.status_code} ({response_time:.2f}ms)")
                
        except Exception as e:
            print(f"❌ {name}: 错误 - {str(e)}")
        
        print()
    
    print("=" * 50)
    print(f"MongoDB页面测试结果: {success_count}/{total_count} 页面正常")
    
    return success_count == total_count

if __name__ == "__main__":
    print("🏠 房源数据分析系统 - 前端页面测试")
    print("=" * 60)
    
    # 基础页面测试
    basic_ok = test_page_access()
    
    # MongoDB页面测试
    mongo_ok = test_mongodb_pages()
    
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print(f"基础页面: {'✅ 正常' if basic_ok else '❌ 异常'}")
    print(f"MongoDB页面: {'✅ 正常' if mongo_ok else '❌ 异常'}")
    
    if basic_ok and mongo_ok:
        print("\n🎉 前端页面测试全部通过！")
        print("💡 建议: 可以在浏览器中访问以下地址进行手动测试:")
        print("   - MySQL版本: http://127.0.0.1:8000/app/login/")
        print("   - MongoDB版本: http://127.0.0.1:8000/mongo/login/")
    else:
        print("\n⚠️  前端页面存在问题，需要进一步检查")
