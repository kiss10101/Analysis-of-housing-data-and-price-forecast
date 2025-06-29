#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python可视化视图
集成Matplotlib/Seaborn静态图表和Plotly交互式图表
"""

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from pymongo import MongoClient
from .chart_generator import ChartGenerator
from .fallback_data import FALLBACK_HOUSES
import json
import logging

logger = logging.getLogger(__name__)

def get_mongodb_data():
    """获取MongoDB数据"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['house_data']
        
        # 获取房源数据
        houses_data = list(db.houses.find())
        client.close()
        
        return houses_data
    except Exception as e:
        logger.error(f"MongoDB连接失败: {e}")
        return None

@login_required
def python_dashboard(request):
    """Python可视化仪表板主页"""
    try:
        # 获取用户信息
        username = request.session.get('username', 'Guest')
        useravatar = request.session.get('useravatar', '/static/picture/avatar.jpg')
        
        # 获取数据
        houses_data = get_mongodb_data()
        
        if houses_data:
            # 使用真实数据
            total_houses = len(houses_data)
            data_source = "MongoDB"
            
            # 基础统计
            price_stats = calculate_price_stats(houses_data)
            city_stats = calculate_city_stats(houses_data)
            
        else:
            # 使用降级数据
            houses_data = FALLBACK_HOUSES
            total_houses = len(houses_data)
            data_source = "降级模式"
            
            # 基础统计
            price_stats = calculate_price_stats_fallback(houses_data)
            city_stats = calculate_city_stats_fallback(houses_data)
        
        context = {
            'username': username,
            'useravatar': useravatar,
            'total_houses': total_houses,
            'data_source': data_source,
            'price_stats': price_stats,
            'city_stats': city_stats,
            'page_title': 'Python可视化仪表板'
        }
        
        return render(request, 'mongo/python_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Python仪表板视图错误: {e}")
        return render(request, 'mongo/error.html', {'error': str(e)})

@login_required
def static_charts_page(request):
    """静态图表页面"""
    try:
        # 获取用户信息
        username = request.session.get('username', 'Guest')
        useravatar = request.session.get('useravatar', '/static/picture/avatar.jpg')
        
        # 获取数据
        houses_data = get_mongodb_data()
        
        if houses_data:
            # 生成静态图表
            generator = ChartGenerator(houses_data)
            
            # 生成各种静态图表
            price_histogram = generator.generate_price_histogram()
            area_price_scatter = generator.generate_area_price_scatter()
            price_trend_line = generator.generate_price_trend_line()
            city_price_boxplot = generator.generate_city_price_boxplot()
            
            data_source = "MongoDB"
        else:
            # 使用降级数据
            generator = ChartGenerator(FALLBACK_HOUSES)
            
            price_histogram = generator.generate_price_histogram()
            area_price_scatter = generator.generate_area_price_scatter()
            price_trend_line = generator.generate_price_trend_line()
            city_price_boxplot = generator.generate_city_price_boxplot()
            
            data_source = "降级模式"
        
        context = {
            'username': username,
            'useravatar': useravatar,
            'price_histogram': price_histogram,
            'area_price_scatter': area_price_scatter,
            'price_trend_line': price_trend_line,
            'city_price_boxplot': city_price_boxplot,
            'data_source': data_source,
            'page_title': 'Python静态图表分析'
        }
        
        return render(request, 'mongo/static_charts.html', context)
        
    except Exception as e:
        logger.error(f"静态图表页面错误: {e}")
        return render(request, 'mongo/error.html', {'error': str(e)})

@login_required
def interactive_charts_page(request):
    """交互式图表页面"""
    try:
        # 获取用户信息
        username = request.session.get('username', 'Guest')
        useravatar = request.session.get('useravatar', '/static/picture/avatar.jpg')
        
        # 获取数据
        houses_data = get_mongodb_data()
        
        if houses_data:
            # 生成交互式图表
            generator = ChartGenerator(houses_data)
            
            # 生成各种交互式图表
            interactive_heatmap = generator.generate_interactive_heatmap()
            interactive_scatter_3d = generator.generate_interactive_scatter_3d()
            
            data_source = "MongoDB"
        else:
            # 使用降级数据
            generator = ChartGenerator(FALLBACK_HOUSES)
            
            interactive_heatmap = generator.generate_interactive_heatmap()
            interactive_scatter_3d = generator.generate_interactive_scatter_3d()
            
            data_source = "降级模式"
        
        context = {
            'username': username,
            'useravatar': useravatar,
            'interactive_heatmap': interactive_heatmap,
            'interactive_scatter_3d': interactive_scatter_3d,
            'data_source': data_source,
            'page_title': 'Python交互式图表分析'
        }
        
        return render(request, 'mongo/interactive_charts.html', context)
        
    except Exception as e:
        logger.error(f"交互式图表页面错误: {e}")
        return render(request, 'mongo/error.html', {'error': str(e)})

@csrf_exempt
def chart_api(request):
    """图表API接口"""
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            chart_type = data.get('chart_type')
            chart_format = data.get('format', 'base64')  # base64 或 html
            
            # 获取数据
            houses_data = get_mongodb_data()
            if not houses_data:
                houses_data = FALLBACK_HOUSES
            
            # 创建图表生成器
            generator = ChartGenerator(houses_data)
            
            # 根据类型生成图表
            if chart_type == 'price_histogram':
                result = generator.generate_price_histogram()
            elif chart_type == 'area_price_scatter':
                result = generator.generate_area_price_scatter()
            elif chart_type == 'city_price_boxplot':
                result = generator.generate_city_price_boxplot()
            elif chart_type == 'interactive_heatmap':
                result = generator.generate_interactive_heatmap()
            elif chart_type == 'interactive_scatter_3d':
                result = generator.generate_interactive_scatter_3d()
            else:
                return JsonResponse({'error': '不支持的图表类型'}, status=400)
            
            return JsonResponse({
                'success': True,
                'chart_data': result,
                'chart_type': chart_type,
                'format': chart_format
            })
        
        else:
            return JsonResponse({'error': '仅支持POST请求'}, status=405)
            
    except Exception as e:
        logger.error(f"图表API错误: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def calculate_price_stats(houses_data):
    """计算价格统计信息"""
    prices = []
    
    for house in houses_data:
        if isinstance(house.get('price'), dict):
            price = house['price'].get('monthly_rent', 0)
        else:
            price = house.get('price', 0)
        
        if price > 0:
            prices.append(price)
    
    if prices:
        return {
            'count': len(prices),
            'min': min(prices),
            'max': max(prices),
            'avg': sum(prices) / len(prices),
            'median': sorted(prices)[len(prices)//2]
        }
    else:
        return {'count': 0, 'min': 0, 'max': 0, 'avg': 0, 'median': 0}

def calculate_city_stats(houses_data):
    """计算城市统计信息"""
    city_counts = {}
    
    for house in houses_data:
        if isinstance(house.get('location'), dict):
            city = house['location'].get('city', '未知')
        else:
            city = house.get('city', '未知')
        
        city_counts[city] = city_counts.get(city, 0) + 1
    
    # 按数量排序
    sorted_cities = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'total_cities': len(city_counts),
        'top_cities': sorted_cities[:5],
        'city_distribution': dict(sorted_cities)
    }

def calculate_price_stats_fallback(houses_data):
    """计算降级数据的价格统计"""
    prices = [house['price'] for house in houses_data if house.get('price', 0) > 0]
    
    if prices:
        return {
            'count': len(prices),
            'min': min(prices),
            'max': max(prices),
            'avg': sum(prices) / len(prices),
            'median': sorted(prices)[len(prices)//2]
        }
    else:
        return {'count': 0, 'min': 0, 'max': 0, 'avg': 0, 'median': 0}

def calculate_city_stats_fallback(houses_data):
    """计算降级数据的城市统计"""
    city_counts = {}
    
    for house in houses_data:
        city = house.get('city', '未知')
        city_counts[city] = city_counts.get(city, 0) + 1
    
    # 按数量排序
    sorted_cities = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'total_cities': len(city_counts),
        'top_cities': sorted_cities[:5],
        'city_distribution': dict(sorted_cities)
    }

def python_housetyperank(request):
    """房型级别分析 - Python可视化版本"""
    try:
        # 获取用户信息
        username = request.session.get('mongo_username', {}).get('username', 'Guest')
        useravatar = request.session.get('mongo_username', {}).get('avatar', '/static/picture/avatar.jpg')

        # 获取数据
        houses_data = get_mongodb_data()

        if houses_data:
            # 使用真实MongoDB数据
            data_source = "MongoDB"

            # 生成房型分析图表
            chart_generator = ChartGenerator()

            # 1. 房型分布统计
            type_stats = {}
            for house in houses_data:
                rental_type = house.get('rental_type', '整租')
                if rental_type not in type_stats:
                    type_stats[rental_type] = {'count': 0, 'prices': []}
                type_stats[rental_type]['count'] += 1
                price = house.get('price', {})
                if isinstance(price, dict):
                    monthly_rent = price.get('monthly_rent', 0)
                else:
                    monthly_rent = price
                if monthly_rent:
                    type_stats[rental_type]['prices'].append(monthly_rent)

            # 获取前3种最常见的房型
            sorted_types = sorted(type_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:3]
            top_three_types = [item[0] for item in sorted_types]

            # 2. 生成图表
            charts = {}
            for i, house_type in enumerate(top_three_types):
                if type_stats[house_type]['prices']:
                    # 生成价格分布图
                    chart_html = chart_generator.generate_price_distribution_chart(
                        type_stats[house_type]['prices'],
                        f"{house_type}房源价格分布"
                    )
                    charts[f'chart_{i+1}'] = chart_html

        else:
            # 使用降级数据
            data_source = "Fallback Data"
            charts = {}
            top_three_types = ['整租', '合租', '单间']

            chart_generator = ChartGenerator()
            for i, house_type in enumerate(top_three_types):
                # 生成模拟图表
                chart_html = chart_generator.generate_sample_chart(f"{house_type}房源价格分布")
                charts[f'chart_{i+1}'] = chart_html

        context = {
            'username': username,
            'useravatar': useravatar,
            'charts': charts,
            'top_three_types': top_three_types,
            'data_source': data_source,
            'page_title': '房型级别分析 - Python可视化'
        }

        return render(request, 'mongo/python_housetyperank.html', context)

    except Exception as e:
        logger.error(f"房型级别分析页面错误: {e}")
        return render(request, 'mongo/python_housetyperank.html', {
            'error': str(e),
            'username': 'Guest',
            'useravatar': '/static/picture/avatar.jpg'
        })

def python_servicemoney(request):
    """价钱影响分析 - Python可视化版本"""
    try:
        # 获取用户信息
        username = request.session.get('mongo_username', {}).get('username', 'Guest')
        useravatar = request.session.get('mongo_username', {}).get('avatar', '/static/picture/avatar.jpg')

        # 获取数据
        houses_data = get_mongodb_data()

        if houses_data:
            # 使用真实MongoDB数据
            data_source = "MongoDB"

            # 生成价格影响分析图表
            chart_generator = ChartGenerator()

            # 1. 面积对价格的影响
            area_chart = chart_generator.generate_area_price_chart(houses_data)

            # 2. 房型对价格的影响
            type_chart = chart_generator.generate_type_price_chart(houses_data)

            # 3. 朝向对价格的影响
            direction_chart = chart_generator.generate_direction_price_chart(houses_data)

            # 4. 城市对价格的影响
            city_chart = chart_generator.generate_city_price_chart(houses_data)

            charts = {
                'area_chart': area_chart,
                'type_chart': type_chart,
                'direction_chart': direction_chart,
                'city_chart': city_chart
            }

        else:
            # 使用降级数据
            data_source = "Fallback Data"
            chart_generator = ChartGenerator()

            charts = {
                'area_chart': chart_generator.generate_sample_chart("面积对价格影响"),
                'type_chart': chart_generator.generate_sample_chart("房型对价格影响"),
                'direction_chart': chart_generator.generate_sample_chart("朝向对价格影响"),
                'city_chart': chart_generator.generate_sample_chart("城市对价格影响")
            }

        context = {
            'username': username,
            'useravatar': useravatar,
            'charts': charts,
            'data_source': data_source,
            'page_title': '价钱影响分析 - Python可视化'
        }

        return render(request, 'mongo/python_servicemoney.html', context)

    except Exception as e:
        logger.error(f"价钱影响分析页面错误: {e}")
        return render(request, 'mongo/python_servicemoney.html', {
            'error': str(e),
            'username': 'Guest',
            'useravatar': '/static/picture/avatar.jpg'
        })
