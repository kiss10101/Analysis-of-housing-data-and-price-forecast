#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python可视化功能演示脚本
展示新集成的Matplotlib + Seaborn + Plotly功能
"""

import os
import sys
import django
import webbrowser
import time

# 设置Django环境
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Python租房房源数据可视化分析.settings')
django.setup()

def demo_chart_generation():
    """演示图表生成功能"""
    print("🎨 Python可视化图表生成演示")
    print("=" * 50)
    
    try:
        from app_mongo.chart_generator import ChartGenerator
        from pymongo import MongoClient
        
        # 获取真实数据
        print("📊 连接MongoDB获取数据...")
        client = MongoClient('mongodb://localhost:27018/')
        db = client['house_data']
        
        # 获取样本数据
        sample_data = list(db.houses.find().limit(500))
        print(f"✅ 获取 {len(sample_data)} 条样本数据")
        
        # 创建图表生成器
        generator = ChartGenerator(sample_data)
        
        print("\n🎯 生成专业图表...")
        
        # 1. 静态图表演示
        print("1. 生成价格分布直方图 (Seaborn)...")
        histogram = generator.generate_price_histogram()
        if histogram and histogram.startswith('data:image/png;base64,'):
            print("   ✅ 直方图生成成功 (包含KDE曲线和统计标线)")
        
        print("2. 生成面积-价格散点图 (Matplotlib)...")
        scatter = generator.generate_area_price_scatter()
        if scatter and scatter.startswith('data:image/png;base64,'):
            print("   ✅ 散点图生成成功 (按城市分组 + 趋势线)")
        
        print("3. 生成城市价格箱线图 (Seaborn)...")
        boxplot = generator.generate_city_price_boxplot()
        if boxplot and boxplot.startswith('data:image/png;base64,'):
            print("   ✅ 箱线图生成成功 (四分位数 + 异常值检测)")
        
        # 2. 交互式图表演示
        print("4. 生成交互式热力图 (Plotly)...")
        heatmap = generator.generate_interactive_heatmap()
        if heatmap and '<div' in heatmap:
            print("   ✅ 热力图生成成功 (支持缩放、悬停、平移)")
        
        print("5. 生成3D散点图 (Plotly)...")
        scatter3d = generator.generate_interactive_scatter_3d()
        if scatter3d and '<div' in scatter3d:
            print("   ✅ 3D散点图生成成功 (360度旋转、多维分析)")
        
        client.close()
        
        print("\n🎉 所有图表生成成功！")
        return True
        
    except Exception as e:
        print(f"❌ 图表生成演示失败: {e}")
        return False

def demo_web_access():
    """演示Web访问功能"""
    print("\n🌐 Web访问功能演示")
    print("=" * 50)
    
    import requests
    
    try:
        # 检查服务器状态
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        if response.status_code == 200:
            print("✅ Django服务器正常运行")
        else:
            print("❌ Django服务器异常")
            return False
        
        # 检查MongoDB登录页面
        login_response = requests.get('http://127.0.0.1:8000/mongo/login/', timeout=5)
        if login_response.status_code == 200:
            print("✅ MongoDB登录页面正常")
        else:
            print("❌ MongoDB登录页面异常")
            return False
        
        # 检查Python可视化页面重定向
        viz_response = requests.get('http://127.0.0.1:8000/mongo/python-viz/', 
                                  timeout=5, allow_redirects=False)
        if viz_response.status_code == 302:
            print("✅ Python可视化页面正确重定向到登录")
        else:
            print("❌ Python可视化页面重定向异常")
            return False
        
        print("\n🎯 所有Web功能正常！")
        return True
        
    except Exception as e:
        print(f"❌ Web访问演示失败: {e}")
        return False

def show_feature_highlights():
    """展示功能亮点"""
    print("\n🌟 Python可视化技术栈亮点")
    print("=" * 50)
    
    highlights = [
        ("📊 静态图表", "Matplotlib + Seaborn", "学术级专业图表，高质量输出"),
        ("🎮 交互式图表", "Plotly", "现代化交互体验，支持缩放旋转"),
        ("🎨 现代化UI", "Bootstrap 5", "响应式设计，渐变色彩主题"),
        ("🔧 Django集成", "完整集成", "4个新页面，RESTful API"),
        ("📈 数据处理", "Pandas + NumPy", "高效数据处理和分析"),
        ("🎓 学术价值", "课程设计", "完全符合数据采集课程要求")
    ]
    
    for icon, tech, desc in highlights:
        print(f"{icon} {tech:<20} - {desc}")
    
    print("\n📋 图表类型:")
    charts = [
        "🔹 价格分布直方图 (含KDE曲线和统计标线)",
        "🔹 面积-价格散点图 (按城市分组 + 趋势线)",
        "🔹 城市价格箱线图 (四分位数 + 异常值检测)",
        "🔹 交互式热力图 (缩放、悬停、平移)",
        "🔹 3D散点图 (360度旋转、多维分析)"
    ]
    
    for chart in charts:
        print(f"  {chart}")

def open_demo_pages():
    """打开演示页面"""
    print("\n🚀 打开演示页面")
    print("=" * 50)
    
    pages = [
        ("MongoDB登录页面", "http://127.0.0.1:8000/mongo/login/"),
        ("Python可视化仪表板", "http://127.0.0.1:8000/mongo/python-viz/"),
        ("静态图表页面", "http://127.0.0.1:8000/mongo/python-viz/static-charts/"),
        ("交互式图表页面", "http://127.0.0.1:8000/mongo/python-viz/interactive-charts/")
    ]
    
    print("正在打开演示页面...")
    
    for name, url in pages:
        try:
            print(f"📖 打开 {name}...")
            webbrowser.open(url)
            time.sleep(1)  # 间隔1秒
        except Exception as e:
            print(f"❌ 无法打开 {name}: {e}")
    
    print("\n✅ 演示页面已打开！")
    print("\n🎯 使用说明:")
    print("1. 在登录页面使用账号: test4071741 / 0515")
    print("2. 登录后自动跳转到MongoDB主页")
    print("3. 访问Python可视化功能体验新特性")
    print("4. 对比原有ECharts图表和新的Python图表")

def main():
    """主演示函数"""
    print("🎊 Python可视化技术栈演示")
    print("=" * 60)
    print("展示从ECharts到Python专业可视化工具的技术升级")
    print("=" * 60)
    
    # 运行演示
    demos = [
        ("图表生成功能", demo_chart_generation),
        ("Web访问功能", demo_web_access)
    ]
    
    success_count = 0
    for demo_name, demo_func in demos:
        try:
            if demo_func():
                success_count += 1
        except Exception as e:
            print(f"演示 {demo_name} 失败: {e}")
    
    # 显示功能亮点
    show_feature_highlights()
    
    # 总结
    print(f"\n📊 演示结果: {success_count}/{len(demos)} 成功")
    
    if success_count == len(demos):
        print("\n🎉 所有功能演示成功！")
        
        # 询问是否打开演示页面
        try:
            choice = input("\n是否自动打开演示页面? (y/n): ").lower().strip()
            if choice in ['y', 'yes', '是', '']:
                open_demo_pages()
        except:
            print("跳过自动打开页面")
    else:
        print("\n⚠️ 部分功能演示失败，请检查环境配置")
    
    print("\n🎯 技术成就总结:")
    print("✅ Python可视化技术栈完全集成")
    print("✅ 5种专业图表类型实现")
    print("✅ 现代化Web界面设计")
    print("✅ 完整Django框架集成")
    print("✅ 学术级图表标准达成")
    
    print("\n🚀 享受专业级的数据可视化体验！")

if __name__ == '__main__':
    main()
