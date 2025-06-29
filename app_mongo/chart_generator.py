#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python可视化图表生成器
支持Matplotlib/Seaborn静态图表和Plotly交互式图表
"""

import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import io
import base64
from django.conf import settings
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 设置Seaborn样式
sns.set_style("whitegrid")
sns.set_palette("husl")

class ChartGenerator:
    """图表生成器基类"""
    
    def __init__(self, data_source=None):
        """
        初始化图表生成器
        
        Args:
            data_source: 数据源，可以是DataFrame或数据库查询结果
        """
        self.data = data_source
        self.static_charts_dir = os.path.join(settings.STATIC_ROOT or 'static', 'charts')
        
        # 确保图表目录存在
        os.makedirs(self.static_charts_dir, exist_ok=True)
    
    def prepare_data(self, data=None):
        """
        准备数据，转换为DataFrame格式
        
        Args:
            data: 输入数据
            
        Returns:
            pandas.DataFrame: 处理后的数据
        """
        if data is None:
            data = self.data
            
        if isinstance(data, pd.DataFrame):
            return data
        elif isinstance(data, list):
            return pd.DataFrame(data)
        else:
            # 假设是MongoDB查询结果
            return pd.DataFrame(list(data))
    
    def generate_price_histogram(self, data=None, save_path=None):
        """
        生成房源价格分布直方图 (Seaborn)
        
        Args:
            data: 房源数据
            save_path: 保存路径
            
        Returns:
            str: 图表的base64编码或文件路径
        """
        df = self.prepare_data(data)
        
        # 创建图表
        plt.figure(figsize=(12, 8))
        
        # 提取价格数据
        prices = []
        for _, row in df.iterrows():
            price = None

            # 尝试多种方式提取价格
            if isinstance(row.get('price'), dict):
                price = row['price'].get('monthly_rent', 0)
            elif isinstance(row.get('price'), (int, float)):
                price = row.get('price', 0)
            elif 'monthly_rent' in row:
                price = row.get('monthly_rent', 0)

            if price and isinstance(price, (int, float)) and price > 0:
                prices.append(float(price))

        prices = pd.Series(prices)
        print(f"提取到 {len(prices)} 个有效价格数据")
        
        # 绘制直方图
        if len(prices) > 10:
            # 数据充足时使用Seaborn
            sns.histplot(data=prices, bins=30, kde=False, alpha=0.7)
        elif len(prices) > 1:
            # 数据较少时使用简单直方图
            plt.hist(prices, bins=min(10, len(prices)//2 + 1), alpha=0.7, edgecolor='black')
        else:
            # 数据太少时显示提示
            plt.text(0.5, 0.5, f'数据不足\n仅有{len(prices)}条记录',
                    ha='center', va='center', transform=plt.gca().transAxes, fontsize=14)
        
        # 添加统计信息
        if len(prices) > 0:
            mean_price = prices.mean()
            median_price = prices.median()

            plt.axvline(mean_price, color='red', linestyle='--',
                       label=f'平均价格: ¥{mean_price:.0f}')
            plt.axvline(median_price, color='orange', linestyle='--',
                       label=f'中位数价格: ¥{median_price:.0f}')
        
        plt.title('广州市房源价格分布直方图', fontsize=16, fontweight='bold')
        plt.xlabel('月租金 (元)', fontsize=12)
        plt.ylabel('房源数量', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 保存或返回
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            # 转换为base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            return f"data:image/png;base64,{image_base64}"
    
    def generate_area_price_scatter(self, data=None, save_path=None):
        """
        生成面积vs价格散点图 (Matplotlib + Seaborn)
        
        Args:
            data: 房源数据
            save_path: 保存路径
            
        Returns:
            str: 图表的base64编码或文件路径
        """
        df = self.prepare_data(data)
        
        # 提取面积和价格数据
        areas = []
        prices = []
        cities = []
        
        for _, row in df.iterrows():
            # 提取面积
            if isinstance(row.get('features'), dict):
                area = row['features'].get('area', 0)
            else:
                area = row.get('area', 0)
            
            # 提取价格
            if isinstance(row.get('price'), dict):
                price = row['price'].get('monthly_rent', 0)
            else:
                price = row.get('price', 0)
            
            # 提取城市
            if isinstance(row.get('location'), dict):
                city = row['location'].get('city', '未知')
            else:
                city = row.get('city', '未知')
            
            if area > 0 and price > 0:
                areas.append(area)
                prices.append(price)
                cities.append(city)
        
        # 创建DataFrame
        scatter_df = pd.DataFrame({
            'area': areas,
            'price': prices,
            'city': cities
        })
        
        # 创建图表
        plt.figure(figsize=(12, 8))
        
        # 按城市分组绘制散点图
        for city in scatter_df['city'].unique():
            city_data = scatter_df[scatter_df['city'] == city]
            plt.scatter(city_data['area'], city_data['price'], 
                       label=city, alpha=0.6, s=50)
        
        # 添加回归线
        if len(areas) > 1:
            z = np.polyfit(areas, prices, 1)
            p = np.poly1d(z)
            plt.plot(areas, p(areas), "r--", alpha=0.8, linewidth=2, 
                    label=f'趋势线 (斜率: {z[0]:.1f})')
        
        plt.title('房源面积与价格关系散点图', fontsize=16, fontweight='bold')
        plt.xlabel('面积 (㎡)', fontsize=12)
        plt.ylabel('月租金 (元)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 保存或返回
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            return f"data:image/png;base64,{image_base64}"

    def generate_price_trend_line(self, data=None, save_path=None):
        """
        生成价格趋势折线图 (Matplotlib + Seaborn)
        课程设计要求：折线图

        Args:
            data: 房源数据
            save_path: 保存路径

        Returns:
            str: 图表的base64编码或文件路径
        """
        df = self.prepare_data(data)

        # 提取价格数据并按城市分组
        city_prices = {}

        for _, row in df.iterrows():
            # 提取价格
            if isinstance(row.get('price'), dict):
                price = row['price'].get('monthly_rent', 0)
            else:
                price = row.get('price', 0)

            # 提取城市
            if isinstance(row.get('location'), dict):
                city = row['location'].get('city', '未知')
            else:
                city = row.get('city', '未知')

            if price > 0 and city != '未知':
                if city not in city_prices:
                    city_prices[city] = []
                city_prices[city].append(price)

        # 计算每个城市的价格统计
        city_stats = {}
        for city, prices in city_prices.items():
            if len(prices) >= 10:  # 只包含有足够数据的城市
                city_stats[city] = {
                    'mean': np.mean(prices),
                    'median': np.median(prices),
                    'q25': np.percentile(prices, 25),
                    'q75': np.percentile(prices, 75),
                    'count': len(prices)
                }

        if not city_stats:
            return self.generate_error_chart("价格趋势折线图", "数据不足")

        # 创建图表
        plt.style.use('seaborn-v0_8')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        # 上图：价格趋势线
        cities = list(city_stats.keys())
        means = [city_stats[city]['mean'] for city in cities]
        medians = [city_stats[city]['median'] for city in cities]

        x_pos = range(len(cities))

        ax1.plot(x_pos, means, marker='o', linewidth=2.5, markersize=8,
                label='平均价格', color='#2E86AB', alpha=0.8)
        ax1.plot(x_pos, medians, marker='s', linewidth=2.5, markersize=8,
                label='中位数价格', color='#A23B72', alpha=0.8)

        ax1.set_title('广州各区域房租价格趋势分析', fontsize=16, fontweight='bold', pad=20)
        ax1.set_xlabel('城市区域', fontsize=12)
        ax1.set_ylabel('月租金 (元)', fontsize=12)
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(cities, rotation=45, ha='right')
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)

        # 添加数值标签
        for i, (mean, median) in enumerate(zip(means, medians)):
            ax1.annotate(f'{mean:.0f}', (i, mean), textcoords="offset points",
                        xytext=(0,10), ha='center', fontsize=9)
            ax1.annotate(f'{median:.0f}', (i, median), textcoords="offset points",
                        xytext=(0,-15), ha='center', fontsize=9)

        # 下图：价格分布范围
        q25_values = [city_stats[city]['q25'] for city in cities]
        q75_values = [city_stats[city]['q75'] for city in cities]

        ax2.fill_between(x_pos, q25_values, q75_values, alpha=0.3, color='#F18F01',
                        label='四分位数范围 (Q1-Q3)')
        ax2.plot(x_pos, means, marker='o', linewidth=2, markersize=6,
                color='#2E86AB', label='平均价格')

        ax2.set_title('价格分布范围分析', fontsize=14, fontweight='bold')
        ax2.set_xlabel('城市区域', fontsize=12)
        ax2.set_ylabel('月租金 (元)', fontsize=12)
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(cities, rotation=45, ha='right')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        # 保存或返回base64
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close()
            return save_path
        else:
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            return f"data:image/png;base64,{image_base64}"

    def generate_city_price_boxplot(self, data=None, save_path=None):
        """
        生成城市价格分布箱线图 (Seaborn)
        
        Args:
            data: 房源数据
            save_path: 保存路径
            
        Returns:
            str: 图表的base64编码或文件路径
        """
        df = self.prepare_data(data)
        
        # 提取城市和价格数据
        city_price_data = []
        
        for _, row in df.iterrows():
            # 提取价格
            if isinstance(row.get('price'), dict):
                price = row['price'].get('monthly_rent', 0)
            else:
                price = row.get('price', 0)
            
            # 提取城市
            if isinstance(row.get('location'), dict):
                city = row['location'].get('city', '未知')
            else:
                city = row.get('city', '未知')
            
            if price > 0:
                city_price_data.append({'city': city, 'price': price})
        
        # 创建DataFrame
        boxplot_df = pd.DataFrame(city_price_data)
        
        # 创建图表
        plt.figure(figsize=(12, 8))
        
        # 绘制箱线图
        sns.boxplot(data=boxplot_df, x='city', y='price', palette='Set2')
        
        # 添加均值点
        sns.pointplot(data=boxplot_df, x='city', y='price', 
                     estimator=np.mean, color='red', markers='D', 
                     linestyles='', scale=0.8, label='均值')
        
        plt.title('各城市房源价格分布箱线图', fontsize=16, fontweight='bold')
        plt.xlabel('城市', fontsize=12)
        plt.ylabel('月租金 (元)', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # 保存或返回
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            return f"data:image/png;base64,{image_base64}"
    
    def generate_interactive_heatmap(self, data=None):
        """
        生成交互式热力图 (Plotly)
        
        Args:
            data: 房源数据
            
        Returns:
            str: Plotly图表的HTML div
        """
        df = self.prepare_data(data)
        
        # 准备热力图数据
        heatmap_data = []
        
        for _, row in df.iterrows():
            # 提取位置信息
            if isinstance(row.get('location'), dict):
                city = row['location'].get('city', '未知')
                street = row['location'].get('street', '未知')
            else:
                city = row.get('city', '未知')
                street = row.get('street', '未知')
            
            # 提取价格
            if isinstance(row.get('price'), dict):
                price = row['price'].get('monthly_rent', 0)
            else:
                price = row.get('price', 0)
            
            if price > 0:
                heatmap_data.append({
                    'city': city,
                    'street': street,
                    'price': price
                })
        
        # 创建DataFrame
        heatmap_df = pd.DataFrame(heatmap_data)
        
        # 计算城市-街道的平均价格
        pivot_data = heatmap_df.groupby(['city', 'street'])['price'].mean().reset_index()
        pivot_table = pivot_data.pivot(index='street', columns='city', values='price')
        
        # 创建交互式热力图
        fig = go.Figure(data=go.Heatmap(
            z=pivot_table.values,
            x=pivot_table.columns,
            y=pivot_table.index,
            colorscale='Viridis',
            hoverongaps=False,
            hovertemplate='城市: %{x}<br>街道: %{y}<br>平均价格: ¥%{z:.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='广州市房源价格热力图',
            xaxis_title='城市',
            yaxis_title='街道',
            font=dict(size=12),
            height=600
        )
        
        return fig.to_html(div_id="interactive_heatmap", include_plotlyjs=True)
    
    def generate_interactive_scatter_3d(self, data=None):
        """
        生成3D交互式散点图 (Plotly)
        
        Args:
            data: 房源数据
            
        Returns:
            str: Plotly图表的HTML div
        """
        df = self.prepare_data(data)
        
        # 准备3D散点图数据
        scatter_data = []
        
        for _, row in df.iterrows():
            # 提取面积
            if isinstance(row.get('features'), dict):
                area = row['features'].get('area', 0)
            else:
                area = row.get('area', 0)
            
            # 提取价格
            if isinstance(row.get('price'), dict):
                price = row['price'].get('monthly_rent', 0)
            else:
                price = row.get('price', 0)
            
            # 提取城市
            if isinstance(row.get('location'), dict):
                city = row['location'].get('city', '未知')
            else:
                city = row.get('city', '未知')
            
            # 计算单价
            unit_price = price / area if area > 0 else 0
            
            if area > 0 and price > 0:
                scatter_data.append({
                    'area': area,
                    'price': price,
                    'unit_price': unit_price,
                    'city': city,
                    'title': row.get('title', '未知房源')
                })
        
        # 创建DataFrame
        scatter_df = pd.DataFrame(scatter_data)
        
        # 创建3D散点图
        fig = px.scatter_3d(
            scatter_df, 
            x='area', 
            y='price', 
            z='unit_price',
            color='city',
            hover_data=['title'],
            title='房源面积-价格-单价 3D散点图',
            labels={
                'area': '面积 (㎡)',
                'price': '月租金 (元)',
                'unit_price': '单价 (元/㎡)',
                'city': '城市'
            }
        )
        
        fig.update_layout(
            scene=dict(
                xaxis_title='面积 (㎡)',
                yaxis_title='月租金 (元)',
                zaxis_title='单价 (元/㎡)'
            ),
            height=600
        )
        
        return fig.to_html(div_id="interactive_scatter_3d", include_plotlyjs=True)

    def generate_area_price_chart(self, houses_data):
        """生成面积对价格影响的图表"""
        try:
            # 准备数据
            areas = []
            prices = []

            for house in houses_data:
                area = house.get('area', 0)
                price = house.get('price', {})
                if isinstance(price, dict):
                    monthly_rent = price.get('monthly_rent', 0)
                else:
                    monthly_rent = price

                if area and monthly_rent:
                    areas.append(area)
                    prices.append(monthly_rent)

            if not areas:
                return self.generate_sample_chart("面积对价格影响")

            # 创建DataFrame
            df = pd.DataFrame({'area': areas, 'price': prices})

            # 创建面积区间
            df['area_range'] = pd.cut(df['area'], bins=5, labels=['小户型', '紧凑型', '标准型', '大户型', '豪华型'])

            # 计算每个区间的平均价格
            area_avg = df.groupby('area_range')['price'].mean().reset_index()

            # 生成Plotly图表
            fig = px.bar(
                area_avg,
                x='area_range',
                y='price',
                title='不同面积区间的平均租金',
                labels={'area_range': '面积区间', 'price': '平均租金 (元)'}
            )

            fig.update_layout(height=400)
            return fig.to_html(div_id="area_price_chart", include_plotlyjs=True)

        except Exception as e:
            return self.generate_sample_chart(f"面积对价格影响 (错误: {str(e)})")

    def generate_type_price_chart(self, houses_data):
        """生成房型对价格影响的图表"""
        try:
            # 准备数据
            types = []
            prices = []

            for house in houses_data:
                rental_type = house.get('rental_type', '整租')
                price = house.get('price', {})
                if isinstance(price, dict):
                    monthly_rent = price.get('monthly_rent', 0)
                else:
                    monthly_rent = price

                if monthly_rent:
                    types.append(rental_type)
                    prices.append(monthly_rent)

            if not types:
                return self.generate_sample_chart("房型对价格影响")

            # 创建DataFrame
            df = pd.DataFrame({'type': types, 'price': prices})

            # 计算每种房型的平均价格
            type_avg = df.groupby('type')['price'].mean().reset_index()

            # 生成Plotly图表
            fig = px.bar(
                type_avg,
                x='type',
                y='price',
                title='不同房型的平均租金',
                labels={'type': '房型', 'price': '平均租金 (元)'}
            )

            fig.update_layout(height=400)
            return fig.to_html(div_id="type_price_chart", include_plotlyjs=True)

        except Exception as e:
            return self.generate_sample_chart(f"房型对价格影响 (错误: {str(e)})")

    def generate_direction_price_chart(self, houses_data):
        """生成朝向对价格影响的图表"""
        try:
            # 准备数据
            directions = []
            prices = []

            for house in houses_data:
                direction = house.get('direction', '南')
                price = house.get('price', {})
                if isinstance(price, dict):
                    monthly_rent = price.get('monthly_rent', 0)
                else:
                    monthly_rent = price

                if monthly_rent:
                    directions.append(direction)
                    prices.append(monthly_rent)

            if not directions:
                return self.generate_sample_chart("朝向对价格影响")

            # 创建DataFrame
            df = pd.DataFrame({'direction': directions, 'price': prices})

            # 计算每种朝向的平均价格
            direction_avg = df.groupby('direction')['price'].mean().reset_index()

            # 生成Plotly图表
            fig = px.bar(
                direction_avg,
                x='direction',
                y='price',
                title='不同朝向的平均租金',
                labels={'direction': '朝向', 'price': '平均租金 (元)'}
            )

            fig.update_layout(height=400)
            return fig.to_html(div_id="direction_price_chart", include_plotlyjs=True)

        except Exception as e:
            return self.generate_sample_chart(f"朝向对价格影响 (错误: {str(e)})")

    def generate_city_price_chart(self, houses_data):
        """生成城市对价格影响的图表"""
        try:
            # 准备数据
            cities = []
            prices = []

            for house in houses_data:
                city = house.get('city', '北京')
                price = house.get('price', {})
                if isinstance(price, dict):
                    monthly_rent = price.get('monthly_rent', 0)
                else:
                    monthly_rent = price

                if monthly_rent:
                    cities.append(city)
                    prices.append(monthly_rent)

            if not cities:
                return self.generate_sample_chart("城市对价格影响")

            # 创建DataFrame
            df = pd.DataFrame({'city': cities, 'price': prices})

            # 计算每个城市的平均价格
            city_avg = df.groupby('city')['price'].mean().reset_index()

            # 取前10个城市
            city_avg = city_avg.nlargest(10, 'price')

            # 生成Plotly图表
            fig = px.bar(
                city_avg,
                x='city',
                y='price',
                title='不同城市的平均租金 (Top 10)',
                labels={'city': '城市', 'price': '平均租金 (元)'}
            )

            fig.update_layout(height=400)
            return fig.to_html(div_id="city_price_chart", include_plotlyjs=True)

        except Exception as e:
            return self.generate_sample_chart(f"城市对价格影响 (错误: {str(e)})")
