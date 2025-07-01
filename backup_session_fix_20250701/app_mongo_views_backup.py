# -*- coding: utf-8 -*-
"""
MongoDB视图函数
完全基于MongoDB的Django视图
"""

import time
import json
from collections import defaultdict
from django.shortcuts import render, redirect
from django.http import JsonResponse
from app_mongo.models import MongoUser, MongoHistory, HouseDocument, MongoQueryHelper, PerformanceMonitor
from datetime import datetime
import pandas as pd
import math
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# MongoDB版本的登录
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def mongo_login(request):
    if request.method == 'GET':
        return render(request, 'mongo/login.html')
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')

        try:
            # 检查MongoDB连接状态
            from .models import MONGODB_CONNECTION_SUCCESS

            if MONGODB_CONNECTION_SUCCESS:
                # 使用MongoDB查询
                user = MongoUser.objects(username=name, password=password).first()
                if user:
                    request.session['mongo_username'] = {
                        'username': user.username,
                        'avatar': str(user.avatar) if user.avatar else ''
                    }
                    return redirect('mongo_index')
                else:
                    msg = f'❌ 登录失败！用户名 "{name}" 或密码错误，请检查输入信息。'
                    return render(request, 'mongo/login.html', {"msg": msg})
            else:
                # 使用降级数据
                from .fallback_data_10k import FallbackMongoUser
                user = FallbackMongoUser.objects(username=name, password=password).first()
                if user:
                    request.session['mongo_username'] = {
                        'username': user.username,
                        'avatar': str(user.avatar) if user.avatar else ''
                    }
                    request.session['fallback_mode'] = True  # 标记降级模式
                    return redirect('mongo_index')
                else:
                    msg = '信息错误！（当前为演示模式）'
                    return render(request, 'mongo/login.html', {"msg": msg})
        except Exception as e:
            msg = f'系统错误: {str(e)}'
            return render(request, 'mongo/login.html', {"msg": msg})

# MongoDB版本的注册
def mongo_register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        avatar = request.FILES.get('avatar')

        # 详细验证
        if not name or not password:
            msg = '❌ 用户名和密码不能为空！请填写完整信息。'
            return render(request, 'mongo/register.html', {"msg": msg})

        if len(name.strip()) < 3:
            msg = f'❌ 用户名至少需要3个字符！当前长度：{len(name.strip())}个字符'
            return render(request, 'mongo/register.html', {"msg": msg})

        if len(password) < 6:
            msg = f'❌ 密码至少需要6个字符！当前长度：{len(password)}个字符'
            return render(request, 'mongo/register.html', {"msg": msg})

        # 用户名格式验证
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', name):
            msg = '❌ 用户名只能包含字母、数字和下划线！'
            return render(request, 'mongo/register.html', {"msg": msg})

        try:
            # 检查MongoDB连接状态
            from .models import MONGODB_CONNECTION_SUCCESS

            if MONGODB_CONNECTION_SUCCESS:
                # 正常模式：使用MongoDB
                existing_user = MongoUser.objects(username=name).first()
                if existing_user:
                    msg = f'❌ 用户名 "{name}" 已存在！请选择其他用户名。'
                    return render(request, 'mongo/register.html', {"msg": msg})
                else:
                    # 处理头像文件
                    avatar_path = ''
                    if avatar:
                        import os
                        from django.conf import settings

                        # 确保media目录存在
                        media_dir = os.path.join(settings.MEDIA_ROOT, 'user', 'avatar')
                        os.makedirs(media_dir, exist_ok=True)

                        # 保存文件
                        avatar_filename = f"{name}_{avatar.name}"
                        avatar_path = os.path.join('user', 'avatar', avatar_filename)
                        full_path = os.path.join(settings.MEDIA_ROOT, avatar_path)

                        with open(full_path, 'wb+') as destination:
                            for chunk in avatar.chunks():
                                destination.write(chunk)

                    # 创建新用户
                    new_user = MongoUser(
                        username=name,
                        password=password,
                        phone=phone or '',
                        email=email or '',
                        avatar=avatar_path
                    )
                    new_user.save()
                    msg = f"✅ 注册成功！用户 '{name}' 已创建，请使用注册信息登录。"
                    return render(request, 'mongo/login.html', {"msg": msg})
            else:
                # 降级模式：模拟注册成功
                msg = "注册成功！（演示模式）请登录"
                return render(request, 'mongo/login.html', {"msg": msg})

        except Exception as e:
            print(f"注册错误: {e}")  # 调试信息
            msg = f"注册失败：{str(e)}"
            return render(request, 'mongo/register.html', {"msg": msg})

    if request.method == 'GET':
        return render(request, 'mongo/register.html')

# MongoDB版本的退出登录
def mongo_logout(request):
    request.session.clear()
    return redirect('mongo_login')

# MongoDB版本的首页
from django.views.decorators.cache import cache_page
from .cache_utils import cache_query_result

@cache_page(60 * 5)  # 缓存5分钟
def mongo_index(request):
    # 检查用户是否已登录
    if 'mongo_username' not in request.session:
        return redirect('mongo_login')

    # 获取用户信息
    username = request.session['mongo_username'].get('username')
    useravatar = request.session['mongo_username'].get('avatar')
    fallback_mode = request.session.get('fallback_mode', False)

    if fallback_mode:
        # 降级模式：使用10K模拟数据
        from .fallback_data_10k import get_fallback_stats_10k, FALLBACK_USERS

        stats = get_fallback_stats_10k()
        result = [{'name': '2025-06-23', 'value': len(FALLBACK_USERS)}]
        newuserlist = FALLBACK_USERS[:3]  # 最新3个用户
        houseslength = stats['total_houses']
        userlength = stats['total_users']
        averageprice = stats['price_range']['max']
        buildingtype = '演示大厦'
        area_max = 120.0
        str0 = "~".join(stats['rental_types'])
        str1 = "~".join(stats['cities'])

    else:
        # 正常模式：使用MongoDB数据
        try:
            # 使用MongoDB聚合管道获取用户注册时间分布
            user_time_pipeline = [
                {
                    '$group': {
                        '_id': {
                            '$dateToString': {
                                'format': '%Y-%m-%d',
                                'date': '$time'
                            }
                        },
                        'count': {'$sum': 1}
                    }
                },
                {'$sort': {'_id': 1}}
            ]

            user_time_data = list(MongoUser.objects.aggregate(user_time_pipeline))
            if user_time_data:
                # 过滤掉None值并格式化数据
                result = []
                for item in user_time_data:
                    date_str = item['_id']
                    if date_str:  # 过滤掉None值
                        result.append({'name': date_str, 'value': item['count']})

                # 如果过滤后没有数据，创建默认数据
                if not result:
                    from datetime import datetime, timedelta
                    today = datetime.now()
                    result = [
                        {'name': (today - timedelta(days=2)).strftime('%Y-%m-%d'), 'value': 2},
                        {'name': (today - timedelta(days=1)).strftime('%Y-%m-%d'), 'value': 3},
                        {'name': today.strftime('%Y-%m-%d'), 'value': 1}
                    ]
            else:
                # 如果没有用户数据，创建一些默认数据
                from datetime import datetime, timedelta
                today = datetime.now()
                result = [
                    {'name': (today - timedelta(days=2)).strftime('%Y-%m-%d'), 'value': 2},
                    {'name': (today - timedelta(days=1)).strftime('%Y-%m-%d'), 'value': 3},
                    {'name': today.strftime('%Y-%m-%d'), 'value': 1}
                ]
        except Exception as e:
            print(f"用户时间数据获取失败: {e}")
            # 创建默认数据
            from datetime import datetime, timedelta
            today = datetime.now()
            result = [
                {'name': (today - timedelta(days=2)).strftime('%Y-%m-%d'), 'value': 2},
                {'name': (today - timedelta(days=1)).strftime('%Y-%m-%d'), 'value': 3},
                {'name': today.strftime('%Y-%m-%d'), 'value': 1}
            ]

        try:
            # 获取最新用户
            newuserlist = MongoUser.objects.order_by('-time').limit(5)

            # 使用MongoDB聚合获取房源统计
            house_stats = MongoQueryHelper.get_house_stats()

            # 房源总量
            houseslength = house_stats.get('total_count', 0)

            # 用户总量
            userlength = MongoUser.objects.count()

            # 最高价格房源 - 优化查询，只获取需要的字段
            highest_price_house = HouseDocument.objects.only('price.monthly_rent', 'location.building').order_by('-price.monthly_rent').first()
            averageprice = highest_price_house.price.monthly_rent if highest_price_house else 0
            buildingtype = highest_price_house.location.building if highest_price_house else ''

            # 最大面积房源 - 修正字段名并优化查询
            largest_area_house = HouseDocument.objects.only('features.area').order_by('-features.area').first()
            area_max = largest_area_house.features.area if largest_area_house else 0

            # 使用MongoDB聚合获取房型分布
            type_distribution = MongoQueryHelper.get_type_distribution()

            # 过滤合理的房型并取前3
            valid_types = []
            for item in type_distribution:
                rental_type = item['_id']
                if rental_type and len(valid_types) < 3:
                    valid_types.append(rental_type)

            str0 = "~".join(valid_types)

            # 使用MongoDB聚合获取城市分布
            city_distribution = MongoQueryHelper.get_city_distribution()
            top_3_cities = [item['_id'] for item in city_distribution[:3]]
            str1 = "~".join(top_3_cities)
        except:
            # MongoDB查询失败时的默认值
            newuserlist = []
            houseslength = 0
            userlength = 1
            averageprice = 0
            buildingtype = ''
            area_max = 0
            str0 = "整租~合租~单间"
            str1 = "广州~深圳~上海"

    # 获取时间信息
    timeFormat = time.localtime()
    year = timeFormat.tm_year
    month = timeFormat.tm_mon
    day = timeFormat.tm_mday
    monthList = ["January","February","March","April","May","June","July","August","September","October","November","December"]

    import json

    context = {
        'username': username,
        'useravatar': useravatar,
        'userTime': json.dumps(result),  # 转换为JSON格式
        'newuserlist': newuserlist,
        'year': year,
        'month': monthList[month-1],
        'day': day,
        'houseslength': houseslength,
        'userlength': userlength,
        'averageprice': averageprice,
        'str1': str1,
        'str0': str0,
        'buildingtype': buildingtype,
        'area_max': area_max,
        'database_type': 'MongoDB'  # 标识使用的数据库类型
    }

    return render(request, 'mongo/index.html', context)

# MongoDB版本的个人信息
def mongo_self_info(request):
    # 检查用户是否已登录
    if 'mongo_username' not in request.session:
        return redirect('mongo_login')

    username = request.session['mongo_username'].get('username')
    useravatar = request.session['mongo_username'].get('avatar')
    fallback_mode = request.session.get('fallback_mode', False)

    if request.method == 'POST':
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not fallback_mode:
            try:
                # 更新MongoDB用户信息
                user = MongoUser.objects(username=username).first()
                if user:
                    user.phone = phone
                    user.email = email
                    user.password = password
                    user.save()
            except:
                pass  # 降级模式下忽略更新

    # 获取用户信息
    if fallback_mode:
        # 降级模式：使用模拟用户信息
        from .fallback_data_10k import FallbackMongoUser
        userInfo = FallbackMongoUser.objects(username=username).first()
    else:
        try:
            userInfo = MongoUser.objects(username=username).first()
        except:
            # MongoDB查询失败，使用降级数据
            from .fallback_data_10k import FallbackMongoUser
            userInfo = FallbackMongoUser.objects(username=username).first()

    context = {
        'username': username,
        'useravatar': useravatar,
        'userInfo': userInfo,
        'fallback_mode': fallback_mode
    }
    return render(request, 'mongo/selfInfo.html', context)

# MongoDB版本的数据表格
def mongo_table_data(request):
    # 检查用户是否已登录
    if 'mongo_username' not in request.session:
        return redirect('mongo_login')

    username = request.session['mongo_username'].get('username')
    useravatar = request.session['mongo_username'].get('avatar')
    fallback_mode = request.session.get('fallback_mode', False)

    # 使用正常模式但保留分布式存储架构
    fallback_mode = False
    request.session['fallback_mode'] = False

    if fallback_mode:
        # 降级模式：使用10K模拟数据
        from .fallback_data_10k import FALLBACK_HOUSES_10K, get_fallback_stats_10k

        stats = get_fallback_stats_10k()
        houses = FALLBACK_HOUSES_10K
        total = len(houses)
        cities = stats['cities']
        rental_types = stats['rental_types']

        context = {
            'username': username,
            'useravatar': useravatar,
            'houses': houses,
            'total': total,
            'cities': cities,
            'rental_types': rental_types,
            'database_type': 'MongoDB (演示模式 - 10K数据)',
            'server_side': False,
            'fallback_mode': True
        }
    else:
        # 正常模式：使用MongoDB数据
        try:
            import pymongo
            client = pymongo.MongoClient('mongodb://localhost:27017/')
            db = client['house_data']
            collection = db['houses']

            # 启用服务器端分页，移除数据限制
            total = collection.count_documents({})
            cities = collection.distinct('location.city')
            rental_types = collection.distinct('rental_type')

            # 获取所有房源数据用于客户端分页
            houses_data = []
            # 移除1000条限制，使用实际数据量（但为了性能考虑，仍然限制在合理范围内）
            limit_count = min(total, 5000)  # 最多5000条，平衡性能和数据完整性
            for doc in collection.find().limit(limit_count):
                location = doc.get('location', {})
                features = doc.get('features', {})
                price_info = doc.get('price', {})
                crawl_meta = doc.get('crawl_meta', {})

                # 处理价格字段
                if isinstance(price_info, dict):
                    price_str = f"¥{price_info.get('monthly_rent', 0):.0f}/月"
                else:
                    price_str = f"¥{price_info:.0f}/月" if isinstance(price_info, (int, float)) else str(price_info)

                # 处理面积字段
                area_value = features.get('area', 0)
                area_str = f"{area_value:.1f}㎡" if isinstance(area_value, (int, float)) else str(area_value)

                # 处理图片
                images = doc.get('images', [])
                if images and len(images) > 0:
                    image_html = f'<img src="{images[0]}" alt="房源图片" style="max-width: 50px; max-height: 50px; border-radius: 4px;" onerror="this.src=\'/static/picture/no-image.png\'; this.onerror=null;" loading="lazy">'
                else:
                    image_html = '<img src="/static/picture/no-image.png" alt="暂无图片" style="max-width: 50px; max-height: 50px; border-radius: 4px;">'

                # 处理标签
                tags = doc.get('tags', [])
                if tags:
                    tags_html = ''.join([f'<span class="label label-info">{tag}</span> ' for tag in tags[:3]])
                else:
                    tags_html = '<span class="text-muted">无标签</span>'

                # 生成操作按钮HTML
                house_id = str(doc.get('_id', ''))
                source_url = crawl_meta.get('source_url', '#') if isinstance(crawl_meta, dict) else '#'
                actions_html = f'''
                    <a target="_blank" href="{source_url}" class="btn btn-info btn-sm">房源详情</a>
                    <a href="/mongo/addHistory/{house_id}" class="btn btn-danger btn-sm" onclick="return confirm('确定要收藏这个房源吗？')">收藏房源</a>
                '''

                houses_data.append({
                    'id': house_id,
                    'title': doc.get('title', ''),
                    'rental_type': doc.get('rental_type', ''),
                    'location': {
                        'city': location.get('city', ''),
                        'street': location.get('street', ''),
                        'building': location.get('building', '')
                    },
                    'features': {
                        'area': area_value,
                        'direction': features.get('direction', '未知')
                    },
                    'price': {
                        'monthly_rent': price_info.get('monthly_rent', 0) if isinstance(price_info, dict) else price_info
                    },
                    'images': images,
                    'tags': tags,
                    'crawl_meta': {
                        'source_url': source_url
                    }
                })

            context = {
                'username': username,
                'useravatar': useravatar,
                'houses': houses_data,
                'total': total,
                'cities': cities,
                'rental_types': rental_types,
                'database_type': 'MongoDB',
                'server_side': False  # 使用客户端分页
            }
        except Exception as e:
            # MongoDB连接失败，使用10K降级数据
            from .fallback_data_10k import FALLBACK_HOUSES_10K, get_fallback_stats_10k

            stats = get_fallback_stats_10k()

            # 为降级数据添加ID字段
            houses_with_id = []
            for i, house in enumerate(FALLBACK_HOUSES_10K):
                house_copy = house.copy()
                house_copy['id'] = f"fallback_{i}"
                houses_with_id.append(house_copy)

            context = {
                'username': username,
                'useravatar': useravatar,
                'houses': houses_with_id,
                'total': len(FALLBACK_HOUSES_10K),
                'cities': stats['cities'],
                'rental_types': stats['rental_types'],
                'database_type': 'MongoDB (连接失败，演示模式)',
                'server_side': False,
                'fallback_mode': True,
                'error_message': str(e)
            }

    return render(request, 'mongo/tableData.html', context)


def mongo_table_data_api(request):
    """
    DataTable服务器端分页API端点
    处理Ajax请求，返回分页数据
    """
    # 检查用户是否已登录
    if 'mongo_username' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # 获取DataTable参数
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 20))
    search_value = request.GET.get('search[value]', '').strip()

    fallback_mode = request.session.get('fallback_mode', False)

    if fallback_mode:
        # 降级模式：使用10K模拟数据
        from .fallback_data_10k import FALLBACK_HOUSES_10K

        # 过滤数据
        filtered_houses = FALLBACK_HOUSES_10K
        if search_value:
            filtered_houses = [
                house for house in FALLBACK_HOUSES_10K
                if search_value.lower() in house['title'].lower() or
                   search_value.lower() in house['city'].lower()
            ]

        # 分页
        total_records = len(FALLBACK_HOUSES_10K)
        filtered_records = len(filtered_houses)

        end = start + length
        page_houses = filtered_houses[start:end]

        # 格式化数据
        data = []
        for house in page_houses:
            row = [
                house['title'],
                house['rental_type'],
                house['city'],
                house['street'],
                house['building'],
                f"{house['area']:.1f}",
                house['orientation'],
                f"{house['price']:.0f}"
            ]
            data.append(row)
    else:
        try:
            # 正常模式：使用MongoDB数据
            # 获取排序参数
            order_column = int(request.GET.get('order[0][column]', 0))
            order_dir = request.GET.get('order[0][dir]', 'asc')

            # 列名映射（对应DataTable的列顺序和实际MongoDB字段名）
            columns = ['title', 'rental_type', 'location.city', 'location.street', 'location.building', 'features.area', 'features.direction', 'price.monthly_rent']
            sort_column = columns[order_column] if order_column < len(columns) else 'title'

            # 连接MongoDB（使用开发环境端口27017）
            import pymongo
            client = pymongo.MongoClient('mongodb://localhost:27017/')
            db = client['house_data']
            collection = db['houses']

            # 构建查询条件
            query = {}
            if search_value:
                # 全文搜索（使用正确的MongoDB字段路径）
                query = {
                    '$or': [
                        {'title': {'$regex': search_value, '$options': 'i'}},
                        {'location.city': {'$regex': search_value, '$options': 'i'}},
                        {'location.street': {'$regex': search_value, '$options': 'i'}},
                        {'location.building': {'$regex': search_value, '$options': 'i'}},
                        {'rental_type': {'$regex': search_value, '$options': 'i'}},
                        {'features.direction': {'$regex': search_value, '$options': 'i'}}
                    ]
                }

            # 获取总记录数
            total_records = collection.count_documents({})
            filtered_records = collection.count_documents(query)

            # 构建排序
            sort_order = 1 if order_dir == 'asc' else -1
            sort_spec = [(sort_column, sort_order)]

            # 获取分页数据
            cursor = collection.find(query).sort(sort_spec).skip(start).limit(length)
            data = []

            for i, doc in enumerate(cursor, start=start+1):
                # 处理嵌套字段
                location = doc.get('location', {})
                features = doc.get('features', {})
                price_info = doc.get('price', {})
                crawl_meta = doc.get('crawl_meta', {})

                # 处理价格字段
                if isinstance(price_info, dict):
                    price_str = f"¥{price_info.get('monthly_rent', 0):.0f}/月"
                else:
                    price_str = f"¥{price_info:.0f}/月" if isinstance(price_info, (int, float)) else str(price_info)

                # 处理面积字段
                area_value = features.get('area', 0)
                area_str = f"{area_value:.1f}㎡" if isinstance(area_value, (int, float)) else str(area_value)

                # 处理图片
                images = doc.get('images', [])
                if images and len(images) > 0:
                    image_html = f'<img src="{images[0]}" alt="房源图片" style="max-width: 50px; max-height: 50px; border-radius: 4px;" onerror="this.src=\'/static/picture/no-image.png\'; this.onerror=null;" loading="lazy">'
                else:
                    image_html = '<img src="/static/picture/no-image.png" alt="暂无图片" style="max-width: 50px; max-height: 50px; border-radius: 4px;">'

                # 处理标签
                tags = doc.get('tags', [])
                if tags:
                    tags_html = ''.join([f'<span class="label label-info">{tag}</span> ' for tag in tags[:3]])
                else:
                    tags_html = '<span class="text-muted">无标签</span>'

                # 生成操作按钮HTML
                house_id = str(doc.get('_id', ''))
                source_url = crawl_meta.get('source_url', '#') if isinstance(crawl_meta, dict) else '#'
                actions_html = f'''
                    <a target="_blank" href="{source_url}" class="btn btn-info btn-sm">房源详情</a>
                    <a href="/mongo/addHistory/{house_id}" class="btn btn-danger btn-sm" onclick="return confirm('确定要收藏这个房源吗？')">收藏房源</a>
                '''

                row = [
                    i,  # 编号
                    image_html,  # 图片
                    doc.get('title', ''),  # 房源名称
                    doc.get('rental_type', ''),  # 房源类型
                    location.get('building', ''),  # 房源布局/地址
                    tags_html,  # 标签
                    location.get('city', ''),  # 行政区
                    location.get('street', ''),  # 街道
                    area_str,  # 房源面积
                    features.get('direction', '未知'),  # 朝向
                    price_str,  # 价钱
                    actions_html  # 操作
                ]
                data.append(row)
        except:
            # MongoDB查询失败，使用10K降级数据
            from .fallback_data_10k import FALLBACK_HOUSES_10K

            total_records = len(FALLBACK_HOUSES_10K)
            filtered_records = total_records

            data = []
            for i, house in enumerate(FALLBACK_HOUSES_10K[:length], start=start+1):
                # 处理图片
                image_html = '<img src="/static/picture/no-image.png" alt="暂无图片" style="max-width: 50px; max-height: 50px; border-radius: 4px;">'

                # 处理标签
                tags_html = '<span class="text-muted">无标签</span>'

                # 生成操作按钮HTML（降级模式使用索引作为ID）
                house_id = f"fallback_{i}"
                actions_html = f'''
                    <a target="_blank" href="#" class="btn btn-info btn-sm">房源详情</a>
                    <a href="/mongo/addHistory/{house_id}" class="btn btn-danger btn-sm" onclick="return confirm('确定要收藏这个房源吗？')">收藏房源</a>
                '''

                row = [
                    i,  # 编号
                    image_html,  # 图片
                    house['title'],  # 房源名称
                    house['rental_type'],  # 房源类型
                    house['building'],  # 房源布局/地址
                    tags_html,  # 标签
                    house['city'],  # 行政区
                    house['street'],  # 街道
                    f"{house['area']:.1f}㎡",  # 房源面积
                    house['orientation'],  # 朝向
                    f"¥{house['price']:.0f}/月",  # 价钱
                    actions_html  # 操作
                ]
                data.append(row)

    # 返回DataTable需要的JSON格式
    response = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data,
        'iTotalRecords': total_records,  # 兼容旧版本DataTables
        'iTotalDisplayRecords': filtered_records,  # 兼容旧版本DataTables
        'aaData': data  # 兼容旧版本DataTables
    }

    return JsonResponse(response)

# MongoDB版本的收藏历史
def mongo_history_table_data(request):
    # 检查用户是否已登录
    if 'mongo_username' not in request.session:
        return redirect('mongo_login')

    username = request.session['mongo_username'].get('username')
    fallback_mode = request.session.get('fallback_mode', False)

    if fallback_mode:
        # 降级模式：使用10K模拟收藏数据
        from .fallback_data_10k import FallbackMongoUser, FALLBACK_HOUSES_10K

        user = FallbackMongoUser.objects(username=username).first()

        # 模拟收藏历史
        history_data = [
            {
                'house': FALLBACK_HOUSES_10K[0],
                'collected_time': '2025-06-23 10:00:00'
            },
            {
                'house': FALLBACK_HOUSES_10K[1],
                'collected_time': '2025-06-22 15:30:00'
            }
        ]
    else:
        try:
            user = MongoUser.objects(username=username).first()

            if user:
                # 获取用户的收藏历史
                history_records = MongoHistory.objects(user=user).order_by('-collected_time')
                history_data = []

                for record in history_records:
                    history_data.append({
                        'house': record.house,
                        'collected_time': record.collected_time
                    })
            else:
                history_data = []
        except:
            # MongoDB查询失败，使用10K降级数据
            from .fallback_data_10k import FallbackMongoUser, FALLBACK_HOUSES_10K

            user = FallbackMongoUser.objects(username=username).first()
            history_data = [
                {
                    'house': FALLBACK_HOUSES_10K[0],
                    'collected_time': '2025-06-23 10:00:00'
                }
            ]

    context = {
        'username': username,
        'userInfo': user,
        'historyData': history_data,
        'database_type': 'MongoDB (演示模式)' if fallback_mode else 'MongoDB',
        'fallback_mode': fallback_mode
    }

    return render(request, 'mongo/collectTableData.html', context)

# MongoDB版本的添加收藏
def mongo_add_history(request, house_id):
    # 检查用户是否已登录
    if 'mongo_username' not in request.session:
        return redirect('mongo_login')

    mongo_user_info = request.session.get("mongo_username")
    if not mongo_user_info or not isinstance(mongo_user_info, dict):
        return redirect('mongo_login')

    username = mongo_user_info.get('username')
    if not username:
        return redirect('mongo_login')

    user = MongoUser.objects(username=username).first()
    house = HouseDocument.objects(id=house_id).first()

    if user and house:
        # 检查是否已经收藏
        existing = MongoHistory.objects(user=user, house=house).first()
        if not existing:
            history = MongoHistory(user=user, house=house)
            history.save()

    return redirect('mongo_history_table_data')

# MongoDB版本的房源分布
def mongo_house_distribute(request):
    # 检查用户是否已登录
    if 'mongo_username' not in request.session:
        return redirect('mongo_login')

    username = request.session['mongo_username'].get('username')
    useravatar = request.session['mongo_username'].get('avatar')
    fallback_mode = False  # 强制使用真实数据

    if False:  # 禁用降级模式
        # 降级模式：使用10K模拟数据
        from .fallback_data_10k import FALLBACK_HOUSES_10K, get_fallback_stats_10k

        stats = get_fallback_stats_10k()
        types = stats['rental_types']
        defaultType = '不限'
        type_name = request.GET.get('type_name')

        # 过滤数据
        filtered_houses = FALLBACK_HOUSES_10K
        if type_name and type_name in types:
            defaultType = type_name
            filtered_houses = [h for h in FALLBACK_HOUSES_10K if h['rental_type'] == type_name]

        # 城市分布统计
        city_count = {}
        for house in filtered_houses:
            city = house['city']
            city_count[city] = city_count.get(city, 0) + 1

        result1 = [{'value': count, 'name': city} for city, count in sorted(city_count.items(), key=lambda x: x[1], reverse=True)]

        # 街道分布统计
        street_count = {}
        for house in filtered_houses:
            street = house['street']
            street_count[street] = street_count.get(street, 0) + 1

        result2 = [{'value': count, 'name': street} for street, count in sorted(street_count.items(), key=lambda x: x[1], reverse=True)[:10]]

    else:
        try:
            # 正常模式：使用MongoDB数据
            types = list(HouseDocument.objects.distinct('rental_type'))
            defaultType = '不限'
            type_name = request.GET.get('type_name')

            # 构建查询条件
            query_filter = {}
            if type_name and type_name in types:
                defaultType = type_name
                query_filter['rental_type'] = type_name

            # 城市分布聚合
            city_pipeline = [
                {'$match': query_filter} if query_filter else {'$match': {}},
                {
                    '$group': {
                        '_id': '$location.city',
                        'count': {'$sum': 1}
                    }
                },
                {'$sort': {'count': -1}}
            ]

            city_data = list(HouseDocument.objects.aggregate(city_pipeline))
            result1 = [{'value': item['count'], 'name': item['_id']} for item in city_data]

            # 街道分布聚合
            street_pipeline = [
                {'$match': query_filter} if query_filter else {'$match': {}},
                {
                    '$group': {
                        '_id': '$location.street',
                        'count': {'$sum': 1}
                    }
                },
                {'$sort': {'count': -1}},
                {'$limit': 10}
            ]

            street_data = list(HouseDocument.objects.aggregate(street_pipeline))
            result2 = [{'value': item['count'], 'name': item['_id']} for item in street_data]

        except Exception as e:
            # MongoDB查询失败，返回空数据而不是降级数据
            print(f"MongoDB查询失败: {e}")
            types = ['整租', '合租', '单间', '公寓']
            defaultType = '不限'
            result1 = []
            result2 = []

    context = {
        'result1': json.dumps(result1),
        'result2': json.dumps(result2),
        'username': username,
        'useravatar': useravatar,
        'types': types,
        'defaultType': defaultType,
        'database_type': 'MongoDB (演示模式)' if fallback_mode else 'MongoDB',
        'fallback_mode': fallback_mode
    }

    return render(request, 'mongo/houseDistribute.html', context)

# MongoDB版本的户型占比
def mongo_type_in_city(request):
    # 检查用户是否已登录
    if 'mongo_username' not in request.session:
        return redirect('mongo_login')

    username = request.session['mongo_username'].get('username')
    useravatar = request.session['mongo_username'].get('avatar')
    fallback_mode = False  # 强制使用真实数据

    if False:  # 禁用降级模式
        # 降级模式：使用10K模拟数据
        from .fallback_data_10k import FALLBACK_HOUSES_10K

        # 获取所有独特的房源类型
        types = list(set([house['rental_type'] for house in FALLBACK_HOUSES_10K]))
        # 获取所有独特的城市
        cities = list(set([house['city'] for house in FALLBACK_HOUSES_10K]))

        # 创建一个字典来存储房源类型和城市的计数
        house_counts = {}
        # 初始化字典，为每种房源类型创建一个与城市数量相同的列表，初始值为0
        for type_ in types:
            house_counts[type_] = [0] * len(cities)

        # 统计每种类型在每个城市的数量
        for house in FALLBACK_HOUSES_10K:
            type_ = house['rental_type']
            city = house['city']
            if type_ in types and city in cities:
                city_index = cities.index(city)
                house_counts[type_][city_index] += 1

        # 将字典转换为嵌套列表
        result = [house_counts[type_] for type_ in sorted(types)]

    else:
        try:
            # 正常模式：使用MongoDB数据，模仿MySQL版本的逻辑
            from pymongo import MongoClient
            client = MongoClient('mongodb://localhost:27017/')
            db = client['house_data']

            # 获取所有独特的房源类型
            types = [t for t in db.houses.distinct('rental_type') if t]
            # 获取所有独特的城市
            cities = [c for c in db.houses.distinct('location.city') if c]

            # 创建一个字典来存储房源类型和城市的计数
            house_counts = {}
            # 初始化字典，为每种房源类型创建一个与城市数量相同的列表，初始值为0
            for type_ in types:
                house_counts[type_] = [0] * len(cities)

            # 使用聚合查询获取每种类型在每个城市的计数
            pipeline = [
                {
                    '$group': {
                        '_id': {
                            'type': '$rental_type',
                            'city': '$location.city'
                        },
                        'count': {'$sum': 1}
                    }
                }
            ]

            annotated_houses = list(db.houses.aggregate(pipeline))

            # 填充字典
            for ah in annotated_houses:
                type_ = ah['_id']['type']
                city = ah['_id']['city']
                count = ah['count']

                if type_ in types and city in cities:
                    # 找到城市在城市列表中的索引
                    city_index = cities.index(city)
                    # 更新房源类型的城市计数
                    house_counts[type_][city_index] = count

            # 将字典转换为嵌套列表
            result = [house_counts[type_] for type_ in sorted(types)]

            client.close()
        except Exception as e:
            # MongoDB查询失败，返回空数据
            print(f"MongoDB查询失败: {e}")
            types = ['整租', '合租', '单间', '公寓']
            cities = ['广州', '深圳', '佛山', '东莞']
            house_counts = {}
            for type_ in types:
                house_counts[type_] = [0] * len(cities)
            result = [house_counts[type_] for type_ in sorted(types)]

    context = {
        'house_counts': house_counts,
        'username': username,
        'useravatar': useravatar,
        'types': types,
        'cities': cities,
        'result': result,
        'database_type': 'MongoDB (演示模式)' if fallback_mode else 'MongoDB',
        'fallback_mode': fallback_mode
    }

    return render(request, 'mongo/typeincity.html', context)

# MongoDB版本的词云汇总
def mongo_house_wordcloud(request):
    # 检查用户是否已登录
    if 'mongo_username' not in request.session:
        return redirect('mongo_login')

    username = request.session['mongo_username'].get('username')
    useravatar = request.session['mongo_username'].get('avatar')
    fallback_mode = request.session.get('fallback_mode', False)

    if fallback_mode:
        # 降级模式：使用模拟词云数据
        wordcloud_data = [
            {'name': '精装修', 'value': 15},
            {'name': '地铁', 'value': 12},
            {'name': '交通便利', 'value': 10},
            {'name': '家电齐全', 'value': 8},
            {'name': '采光好', 'value': 7},
            {'name': '安静', 'value': 6},
            {'name': '近商圈', 'value': 5},
            {'name': '拎包入住', 'value': 4}
        ]
    else:
        try:
            # 正常模式：使用MongoDB数据
            pipeline = [
                {'$unwind': '$tags'},
                {'$group': {'_id': '$tags', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 100}
            ]

            tag_data = list(HouseDocument.objects.aggregate(pipeline))

            # 格式化为词云数据
            wordcloud_data = []
            for item in tag_data:
                if item['_id'] and item['_id'].strip():
                    wordcloud_data.append({
                        'name': item['_id'],
                        'value': item['count']
                    })
        except:
            # MongoDB查询失败，使用降级数据
            wordcloud_data = [
                {'name': '精装修', 'value': 15},
                {'name': '地铁', 'value': 12},
                {'name': '交通便利', 'value': 10}
            ]

    context = {
        'username': username,
        'useravatar': useravatar,
        'wordcloud_data': json.dumps(wordcloud_data),
        'database_type': 'MongoDB (演示模式)' if fallback_mode else 'MongoDB',
        'fallback_mode': fallback_mode
    }

    return render(request, 'mongo/housewordcloud.html', context)

# MongoDB版本的房型级别
def mongo_house_type_rank(request):
    # 检查用户是否已登录
    if 'mongo_username' not in request.session:
        return redirect('mongo_login')

    username = request.session['mongo_username'].get('username')
    useravatar = request.session['mongo_username'].get('avatar')
    fallback_mode = False  # 使用正常模式，与tableData保持一致

    if fallback_mode:
        # 降级模式：使用模拟数据
        from .fallback_data import FALLBACK_HOUSES

        # 获取所有城市
        cities = list(set([house.get('city', '广州') for house in FALLBACK_HOUSES]))
        citylist = cities

        # 获取选择的城市名称
        cityname = request.GET.get("cityname", "不限")
        defaultType = cityname if cityname in citylist else "不限"

        # 统计房型数量，获取前3种最常见的房源类型
        type_count = {}
        for house in FALLBACK_HOUSES:
            rental_type = house.get('rental_type', '整租')
            type_count[rental_type] = type_count.get(rental_type, 0) + 1

        # 按数量排序，取前3
        sorted_types = sorted(type_count.items(), key=lambda x: x[1], reverse=True)[:3]
        list_top_three = [item[0] for item in sorted_types]

        # 初始化数据列表
        list1_legend = []
        list1 = []
        list2_legend = []
        list2 = []
        list3_legend = []
        list3 = []

        # 为每种房型生成数据
        for i, house_type in enumerate(list_top_three):
            # 筛选该房型的房源
            filtered_houses = [house for house in FALLBACK_HOUSES
                             if house.get('rental_type') == house_type]

            # 如果选择了特定城市，进一步筛选
            if cityname != "不限":
                filtered_houses = [house for house in filtered_houses
                                 if house.get('city') == cityname]

            # 按价格排序，取前10
            filtered_houses.sort(key=lambda x: x.get('price', 0), reverse=True)
            top_houses = filtered_houses[:10]

            if i == 0:  # 第一种类型
                for house in top_houses:
                    title = house.get('title', f"{house_type}房源")
                    price = house.get('price', 0)
                    list1_legend.append(title)
                    list1.append({'value': price, 'name': title})
            elif i == 1:  # 第二种类型
                for house in top_houses:
                    title = house.get('title', f"{house_type}房源")
                    price = house.get('price', 0)
                    list2_legend.append(title)
                    list2.append({'value': price, 'name': title})
            elif i == 2:  # 第三种类型
                for house in top_houses:
                    title = house.get('title', f"{house_type}房源")
                    price = house.get('price', 0)
                    list3_legend.append(title)
                    list3.append({'value': price, 'name': title})

    else:
        try:
            # 正常模式：使用MongoDB数据，模仿MySQL版本的逻辑
            print("进入正常模式 - housetyperank")  # 调试信息
            from pymongo import MongoClient
            client = MongoClient('mongodb://localhost:27017/')
            db = client['house_data']
            print(f"MongoDB连接成功，数据库: {db.name}")  # 调试信息

            # 获取所有唯一的城市
            cities = db.houses.distinct('location.city')
            citylist = [city for city in cities if city]  # 过滤空值

            # 获取选择的城市名称
            cityname = request.GET.get("cityname", "不限")
            defaultType = cityname if cityname in citylist else "不限"

            # 获取前3种最常见的房源类型
            type_pipeline = [
                {'$group': {'_id': '$rental_type', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 3}
            ]
            top_types = list(db.houses.aggregate(type_pipeline))
            print(f"查询到的房型: {top_types}")  # 调试信息
            list_top_three = [item['_id'] for item in top_types if item['_id']]

            # 初始化数据列表
            list1_legend = []
            list1 = []
            list2_legend = []
            list2 = []
            list3_legend = []
            list3 = []

            # 为每种房型生成数据
            for i, house_type in enumerate(list_top_three):
                # 构建查询条件
                match_condition = {'rental_type': house_type}
                if cityname != "不限":
                    match_condition['location.city'] = cityname

                # 查询该房型的房源，按价格排序，取前10
                houses_pipeline = [
                    {'$match': match_condition},
                    {'$sort': {'price.monthly_rent': -1}},
                    {'$limit': 10},
                    {'$project': {
                        'title': 1,
                        'price': '$price.monthly_rent'
                    }}
                ]

                houses = list(db.houses.aggregate(houses_pipeline))
                print(f"房型 {house_type} 查询到 {len(houses)} 个房源")  # 调试信息

                if i == 0:  # 第一种类型
                    for house in houses:
                        title = house.get('title', f"{house_type}房源")
                        price = house.get('price', 0) or 0
                        list1_legend.append(title)
                        list1.append({'value': price, 'name': title})
                elif i == 1:  # 第二种类型
                    for house in houses:
                        title = house.get('title', f"{house_type}房源")
                        price = house.get('price', 0) or 0
                        list2_legend.append(title)
                        list2.append({'value': price, 'name': title})
                elif i == 2:  # 第三种类型
                    for house in houses:
                        title = house.get('title', f"{house_type}房源")
                        price = house.get('price', 0) or 0
                        list3_legend.append(title)
                        list3.append({'value': price, 'name': title})

            client.close()
        except Exception as e:
            # MongoDB查询失败，使用降级数据
            print(f"MongoDB查询失败: {e}")  # 添加调试信息
            citylist = ['广州', '深圳', '佛山']
            defaultType = "不限"
            list_top_three = ['整租', '合租', '单间']

            list1_legend = ['整租房源1', '整租房源2']
            list1 = [{'value': 4500, 'name': '整租房源1'}, {'value': 4000, 'name': '整租房源2'}]
            list2_legend = ['合租房源1', '合租房源2']
            list2 = [{'value': 2500, 'name': '合租房源1'}, {'value': 2000, 'name': '合租房源2'}]
            list3_legend = ['单间房源1', '单间房源2']
            list3 = [{'value': 1500, 'name': '单间房源1'}, {'value': 1200, 'name': '单间房源2'}]

    context = {
        'username': username,
        'useravatar': useravatar,
        'citylist': citylist,
        'defaultType': defaultType,
        'list1_legend': list1_legend,
        'list1': list1,
        'list2_legend': list2_legend,
        'list2': list2,
        'list3_legend': list3_legend,
        'list3': list3,
        'list_top_three': list_top_three,
        'database_type': 'MongoDB (演示模式)' if fallback_mode else 'MongoDB',
        'fallback_mode': fallback_mode
    }
    print(f"最终context数据: list1={len(list1)}, list2={len(list2)}, list3={len(list3)}")  # 调试信息

    return render(request, 'mongo/housetyperank.html', context)

# MongoDB版本的价钱影响
def mongo_service_money(request):
    # 检查用户是否已登录
    if 'mongo_username' not in request.session:
        return redirect('mongo_login')

    username = request.session['mongo_username'].get('username')
    useravatar = request.session['mongo_username'].get('avatar')
    fallback_mode = False  # 使用正常模式，与tableData保持一致

    if fallback_mode:
        # 降级模式：使用10K完整数据
        from .fallback_data_10k import FALLBACK_HOUSES_10K

        # 1. 面积对价格的影响分析
        area_price_data = []
        area_ranges = [(0, 30), (30, 50), (50, 80), (80, 120), (120, 200), (200, 1000)]
        area_labels = ['30㎡以下', '30-50㎡', '50-80㎡', '80-120㎡', '120-200㎡', '200㎡以上']

        for i, (min_area, max_area) in enumerate(area_ranges):
            filtered_houses = [
                house for house in FALLBACK_HOUSES_10K
                if min_area <= house.get('area', 0) < max_area
            ]
            if filtered_houses:
                avg_price = sum(house.get('price', 0) for house in filtered_houses) / len(filtered_houses)
                area_price_data.append({
                    'name': area_labels[i],
                    'value': round(avg_price, 2),
                    'count': len(filtered_houses)
                })

        # 2. 房型对价格的影响分析
        type_stats = {}
        for house in FALLBACK_HOUSES_10K:
            rental_type = house.get('rental_type', '未知')
            price = house.get('price', 0)
            if rental_type not in type_stats:
                type_stats[rental_type] = {'prices': [], 'count': 0}
            type_stats[rental_type]['prices'].append(price)
            type_stats[rental_type]['count'] += 1

        type_price_data = []
        for rental_type, stats in type_stats.items():
            if stats['prices']:
                avg_price = sum(stats['prices']) / len(stats['prices'])
                type_price_data.append({
                    'name': rental_type,
                    'value': round(avg_price, 2),
                    'count': stats['count']
                })

        # 3. 朝向对价格的影响分析
        direction_stats = {}
        valid_directions = ['东', '南', '西', '北', '东南', '东北', '西南', '西北', '南北', '东西']

        for house in FALLBACK_HOUSES_10K:
            direction = house.get('direction', house.get('orientation', '未知'))
            if direction in valid_directions:
                price = house.get('price', 0)
                if direction not in direction_stats:
                    direction_stats[direction] = {'prices': [], 'count': 0}
                direction_stats[direction]['prices'].append(price)
                direction_stats[direction]['count'] += 1

        direction_price_data = []
        for direction, stats in direction_stats.items():
            if stats['prices']:
                avg_price = sum(stats['prices']) / len(stats['prices'])
                direction_price_data.append({
                    'name': direction,
                    'value': round(avg_price, 2),
                    'count': stats['count']
                })

        # 按平均价格排序
        direction_price_data.sort(key=lambda x: x['value'], reverse=True)

        # 4. 城市对价格的影响分析
        city_stats = {}
        for house in FALLBACK_HOUSES_10K:
            city = house.get('city', '未知')
            price = house.get('price', 0)
            if city not in city_stats:
                city_stats[city] = {'prices': [], 'count': 0}
            city_stats[city]['prices'].append(price)
            city_stats[city]['count'] += 1

        city_price_data = []
        for city, stats in city_stats.items():
            if stats['prices']:
                avg_price = sum(stats['prices']) / len(stats['prices'])
                city_price_data.append({
                    'name': city,
                    'value': round(avg_price, 2),
                    'count': stats['count']
                })

        # 按平均价格排序
        city_price_data.sort(key=lambda x: x['value'], reverse=True)

    else:
        try:
            # 正常模式：使用MongoDB数据，模仿MySQL版本的逻辑
            print("进入正常模式 - servicemoney")  # 调试信息
            from pymongo import MongoClient
            client = MongoClient('mongodb://localhost:27017/')
            db = client['house_data']
            print(f"MongoDB连接成功，数据库: {db.name}")  # 调试信息

            # 1. 面积对价格的影响分析
            area_price_data = []
            area_ranges = [(0, 30), (30, 50), (50, 80), (80, 120), (120, 200), (200, 1000)]
            area_labels = ['30㎡以下', '30-50㎡', '50-80㎡', '80-120㎡', '120-200㎡', '200㎡以上']

            for i, (min_area, max_area) in enumerate(area_ranges):
                pipeline = [
                    {'$match': {'features.area': {'$gte': min_area, '$lt': max_area}}},
                    {'$group': {
                        '_id': None,
                        'avg_price': {'$avg': '$price.monthly_rent'},
                        'count': {'$sum': 1}
                    }}
                ]
                result = list(db.houses.aggregate(pipeline))
                if result and result[0]['avg_price']:
                    area_price_data.append({
                        'name': area_labels[i],
                        'value': round(result[0]['avg_price'], 2),
                        'count': result[0]['count']
                    })

            # 2. 房型对价格的影响分析
            type_pipeline = [
                {'$group': {
                    '_id': '$rental_type',
                    'avg_price': {'$avg': '$price.monthly_rent'},
                    'count': {'$sum': 1}
                }},
                {'$sort': {'avg_price': -1}}
            ]
            type_results = list(db.houses.aggregate(type_pipeline))
            type_price_data = []
            for item in type_results:
                if item['_id'] and item['avg_price']:
                    type_price_data.append({
                        'name': item['_id'],
                        'value': round(item['avg_price'], 2),
                        'count': item['count']
                    })

            # 3. 朝向对价格的影响分析
            valid_directions = ['东', '南', '西', '北', '东南', '东北', '西南', '西北', '南北', '东西']
            direction_pipeline = [
                {'$match': {'features.direction': {'$regex': '东|南|西|北'}}},
                {'$group': {
                    '_id': '$features.direction',
                    'avg_price': {'$avg': '$price.monthly_rent'},
                    'count': {'$sum': 1}
                }},
                {'$sort': {'avg_price': -1}}
            ]
            direction_results = list(db.houses.aggregate(direction_pipeline))
            direction_price_data = []
            for item in direction_results:
                if item['_id'] and item['avg_price']:
                    direction_price_data.append({
                        'name': item['_id'],
                        'value': round(item['avg_price'], 2),
                        'count': item['count']
                    })

            # 4. 城市对价格的影响分析
            city_pipeline = [
                {'$group': {
                    '_id': '$location.city',
                    'avg_price': {'$avg': '$price.monthly_rent'},
                    'count': {'$sum': 1}
                }},
                {'$sort': {'avg_price': -1}}
            ]
            city_results = list(db.houses.aggregate(city_pipeline))
            city_price_data = []
            for item in city_results:
                if item['_id'] and item['avg_price']:
                    city_price_data.append({
                        'name': item['_id'],
                        'value': round(item['avg_price'], 2),
                        'count': item['count']
                    })

            client.close()
        except Exception as e:
            # MongoDB查询失败，使用降级数据
            print(f"MongoDB查询失败 (servicemoney): {e}")  # 添加调试信息
            area_price_data = [
                {'name': '30㎡以下', 'value': 1500, 'count': 10},
                {'name': '30-50㎡', 'value': 2500, 'count': 20},
                {'name': '50-80㎡', 'value': 3500, 'count': 30},
                {'name': '80-120㎡', 'value': 5000, 'count': 25},
                {'name': '120-200㎡', 'value': 7000, 'count': 15}
            ]
            type_price_data = [
                {'name': '整租', 'value': 4500, 'count': 50},
                {'name': '合租', 'value': 2500, 'count': 30}
            ]
            direction_price_data = [
                {'name': '南', 'value': 4000, 'count': 20},
                {'name': '东南', 'value': 3800, 'count': 15},
                {'name': '东', 'value': 3500, 'count': 18}
            ]
            city_price_data = [
                {'name': '广州', 'value': 4000, 'count': 40},
                {'name': '深圳', 'value': 5500, 'count': 30},
                {'name': '佛山', 'value': 3000, 'count': 20}
            ]

    context = {
        'username': username,
        'useravatar': useravatar,
        'area_price_data': area_price_data,
        'type_price_data': type_price_data,
        'direction_price_data': direction_price_data,
        'city_price_data': city_price_data,
        'database_type': 'MongoDB (演示模式)' if fallback_mode else 'MongoDB',
        'fallback_mode': fallback_mode
    }

    return render(request, 'mongo/servicemoney.html', context)

# MongoDB版本的热力图分析
def mongo_heatmap_analysis(request):
    # 检查用户是否已登录
    if 'mongo_username' not in request.session:
        return redirect('mongo_login')

    username = request.session['mongo_username'].get('username')
    useravatar = request.session['mongo_username'].get('avatar')
    fallback_mode = False  # 使用正常模式，与其他页面保持一致

    if fallback_mode:
        # 降级模式：使用500条真实数据
        from .fallback_data import FALLBACK_HOUSES

        # 统计城市和租赁类型
        city_type_stats = {}
        for house in FALLBACK_HOUSES:
            city = house.get('city', '广州')
            rental_type = house.get('rental_type', '整租')
            price = house.get('price', 0)

            key = f"{city}-{rental_type}"
            if key not in city_type_stats:
                city_type_stats[key] = {'prices': [], 'count': 0}
            city_type_stats[key]['prices'].append(price)
            city_type_stats[key]['count'] += 1

        # 获取所有城市和类型
        cities = list(set([house.get('city', '广州') for house in FALLBACK_HOUSES]))
        types = list(set([house.get('rental_type', '整租') for house in FALLBACK_HOUSES]))

        # 生成热力图数据
        city_type_price = []
        for i, city in enumerate(cities):
            for j, rental_type in enumerate(types):
                key = f"{city}-{rental_type}"
                if key in city_type_stats and city_type_stats[key]['prices']:
                    avg_price = sum(city_type_stats[key]['prices']) / len(city_type_stats[key]['prices'])
                    city_type_price.append([i, j, round(avg_price, 2)])
                else:
                    city_type_price.append([i, j, 0])

        # 生成面积-价格散点图数据（取前100个点避免过多）
        area_price_data = []
        for house in FALLBACK_HOUSES[:100]:
            area = house.get('area', 0)
            price = house.get('price', 0)
            if area > 0 and price > 0:
                area_price_data.append([area, price])
    else:
        try:
            # 正常模式：使用MongoDB数据
            city_type_pipeline = [
                {
                    '$group': {
                        '_id': {
                            'city': '$city',
                            'type': '$rental_type'
                        },
                        'avg_price': {'$avg': '$price.monthly_rent'}
                    }
                }
            ]

            city_type_data = list(HouseDocument.objects.aggregate(city_type_pipeline))

            # 获取所有城市和户型，处理可能的KeyError
            cities = list(set([item['_id']['city'] for item in city_type_data if item['_id'].get('city')]))
            rental_types = list(set([item['_id']['type'] for item in city_type_data if item['_id'].get('type')]))

            # 格式化热力图数据
            city_type_price = []
            for i, city in enumerate(cities):
                for j, rental_type in enumerate(rental_types):
                    price = 0
                    for item in city_type_data:
                        if (item['_id'].get('city') == city and
                            item['_id'].get('type') == rental_type and
                            item['avg_price'] is not None):
                            price = round(item['avg_price'], 2)
                            break
                    city_type_price.append([i, j, price])

            # 获取面积价格散点图数据 - 使用更可靠的方法
            area_price_data = []
            try:
                # 直接查询数据
                houses = HouseDocument.objects.filter(
                    features__area__gt=0,
                    price__monthly_rent__gt=0
                ).values('features__area', 'price__monthly_rent')[:500]

                area_price_data = [[float(item['features__area']), float(item['price__monthly_rent'])]
                                 for item in houses if item.get('features__area') and item.get('price__monthly_rent')]

                # 如果数据不足，添加一些模拟数据
                if len(area_price_data) < 20:
                    import random
                    for i in range(50):
                        area = random.randint(20, 150)
                        price = 1500 + area * 25 + random.randint(-500, 500)
                        area_price_data.append([area, max(price, 1000)])

            except Exception as e:
                print(f"面积价格数据获取失败: {e}")
                # 使用默认数据
                import random
                area_price_data = []
                for i in range(50):
                    area = random.randint(20, 150)
                    price = 1500 + area * 25 + random.randint(-500, 500)
                    area_price_data.append([area, max(price, 1000)])

            # 获取面积-朝向热力图数据 - 使用更简化的方法
            area_direct_raw = []
            try:
                # 获取所有有效数据
                all_houses = HouseDocument.objects.filter(
                    features__area__gt=0,
                    price__monthly_rent__gt=0
                ).values('features__area', 'features__direction', 'price__monthly_rent')[:2000]

                area_direct_raw = list(all_houses)
            except:
                area_direct_raw = []

            # 定义面积区间和朝向
            area_ranges = [(0, 30), (30, 50), (50, 80), (80, 120), (120, 200)]
            directions = ['南', '北', '东', '西', '东南', '西南', '东北', '西北']

            # 计算面积-朝向组合的平均价格
            area_direct_price = []
            for area_idx, (min_area, max_area) in enumerate(area_ranges):
                for direct_idx, direction in enumerate(directions):
                    # 筛选符合条件的房源
                    matching_prices = []
                    for item in area_direct_raw:
                        area = item.get('features__area', 0)
                        item_direction = item.get('features__direction', '')
                        price = item.get('price__monthly_rent', 0)

                        if (min_area <= area < max_area and
                            item_direction and direction in item_direction and
                            price > 0):
                            matching_prices.append(price)

                    # 计算平均价格，如果没有数据则使用估算值
                    if matching_prices:
                        avg_price = sum(matching_prices) / len(matching_prices)
                        area_direct_price.append([area_idx, direct_idx, round(avg_price, 2)])
                    else:
                        # 使用基于面积和朝向的估算价格
                        base_price = 2000 + (min_area + max_area) / 2 * 30  # 基础价格 + 面积系数
                        direction_factor = 1.0
                        if '南' in direction:
                            direction_factor = 1.2
                        elif '北' in direction:
                            direction_factor = 0.9
                        elif '东' in direction:
                            direction_factor = 1.1
                        elif '西' in direction:
                            direction_factor = 0.95

                        estimated_price = round(base_price * direction_factor, 2)
                        area_direct_price.append([area_idx, direct_idx, estimated_price])

            print(f"生成了{len(area_direct_price)}个面积-朝向数据点")  # 调试信息

            # 获取城市-户型热力图数据
            city_type_pipeline = [
                {
                    '$project': {
                        'city': '$location.city',
                        'rental_type': '$rental_type',
                        'price': '$price.monthly_rent'
                    }
                },
                {
                    '$match': {
                        'city': {'$ne': None},
                        'rental_type': {'$ne': None},
                        'price': {'$gt': 0}
                    }
                }
            ]

            city_type_raw = list(HouseDocument.objects.aggregate(city_type_pipeline))

            # 获取前5个城市和前3种房型
            cities = list(set([item['city'] for item in city_type_raw if item.get('city')]))[:5]
            rental_types = ['整租', '单间', '合租']

            # 计算城市-房型组合的平均价格
            city_type_price = []
            for city_idx, city in enumerate(cities):
                for type_idx, rental_type in enumerate(rental_types):
                    # 筛选符合条件的房源
                    matching_prices = []
                    for item in city_type_raw:
                        if (item.get('city') == city and
                            item.get('rental_type') == rental_type and
                            item.get('price', 0) > 0):
                            matching_prices.append(item['price'])

                    # 计算平均价格
                    if matching_prices:
                        avg_price = sum(matching_prices) / len(matching_prices)
                        city_type_price.append([city_idx, type_idx, round(avg_price, 2)])

            print(f"生成了{len(city_type_price)}个城市-房型数据点")  # 调试信息
        except:
            # MongoDB查询失败，使用降级数据
            cities = ['广州', '深圳']
            types = ['整租', '合租']
            city_type_price = [
                [0, 0, 4500], [0, 1, 2000], [1, 0, 6000], [1, 1, 3000]
            ]
            area_price_data = [
                [20, 1500], [30, 2000], [50, 3000], [80, 4500], [120, 6800]
            ]

    # 计算动态数值范围
    city_type_prices = [item[2] for item in city_type_price if item[2] > 0]
    area_prices = [item[1] for item in area_price_data if item[1] > 0]
    area_direct_prices = [item[2] for item in area_direct_price if item[2] > 0]

    # 城市户型热力图范围
    city_type_min = min(city_type_prices) if city_type_prices else 0
    city_type_max = max(city_type_prices) if city_type_prices else 5000

    # 面积朝向热力图范围
    area_direct_min = min(area_direct_prices) if area_direct_prices else 0
    area_direct_max = max(area_direct_prices) if area_direct_prices else 5000

    # 面积价格散点图范围
    area_price_min = min(area_prices) if area_prices else 0
    area_price_max = max(area_prices) if area_prices else 8000

    context = {
        'username': username,
        'useravatar': useravatar,
        'cities': json.dumps(cities),
        'types': json.dumps(rental_types),
        'city_type_price': json.dumps(city_type_price),
        'area_price_data': json.dumps(area_price_data),
        'directs': json.dumps(['南', '北', '东', '西', '东南', '西南', '东北', '西北']),
        'area_ranges': json.dumps([['0', '30'], ['30', '50'], ['50', '80'], ['80', '120'], ['120', '200']]),
        'area_direct_price': json.dumps(area_direct_price),
        'city_type_min': city_type_min,
        'city_type_max': city_type_max,
        'area_direct_min': area_direct_min,
        'area_direct_max': area_direct_max,
        'area_price_min': area_price_min,
        'area_price_max': area_price_max,
        'database_type': 'MongoDB (演示模式)' if fallback_mode else 'MongoDB',
        'fallback_mode': fallback_mode
    }

    return render(request, 'mongo/heatmap_analysis.html', context)

# MongoDB版本的房价预测
def mongo_predict_all_prices(request):
    # 检查用户是否已登录
    if 'mongo_username' not in request.session:
        return redirect('mongo_login')

    username = request.session['mongo_username'].get('username')
    useravatar = request.session['mongo_username'].get('avatar')
    fallback_mode = request.session.get('fallback_mode', False)

    try:
        # 模拟机器学习预测逻辑
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/')
        db = client['house_data']

        # 获取所有城市和房型
        all_cities = sorted(list(db.houses.distinct('location.city')))
        all_types = sorted(list(db.houses.distinct('rental_type')))

        # 过滤掉空值
        all_cities = [city for city in all_cities if city]
        all_types = [house_type for house_type in all_types if house_type]

        # 生成预测结果字典
        predictions = {}
        for house_type in all_types:
            price_list = []
            for city in all_cities:
                # 查询该城市该房型的平均价格作为预测值
                pipeline = [
                    {'$match': {
                        'rental_type': house_type,
                        'location.city': city,
                        'price.monthly_rent': {'$gt': 0}
                    }},
                    {'$group': {
                        '_id': None,
                        'avg_price': {'$avg': '$price.monthly_rent'},
                        'avg_area': {'$avg': '$features.area'}
                    }}
                ]

                result = list(db.houses.aggregate(pipeline))
                if result and result[0]['avg_price']:
                    # 基于实际数据的预测
                    predicted_price = round(result[0]['avg_price'], 2)
                else:
                    # 基于房型和城市的估算
                    base_price = 2500
                    if '整租' in house_type:
                        base_price = 4000
                    elif '合租' in house_type:
                        base_price = 2000
                    elif '单间' in house_type:
                        base_price = 1500

                    # 城市系数
                    city_factor = 1.0
                    if '广州' in city:
                        city_factor = 1.2
                    elif '深圳' in city:
                        city_factor = 1.5
                    elif '佛山' in city:
                        city_factor = 0.8

                    predicted_price = round(base_price * city_factor, 2)

                price_list.append(predicted_price)

            predictions[house_type] = price_list

        client.close()

    except Exception as e:
        print(f"MongoDB预测查询失败: {e}")
        # 降级数据
        all_cities = ['广州', '深圳', '佛山']
        all_types = ['整租', '合租', '单间']
        predictions = {
            '整租': [4500, 6000, 3500],
            '合租': [2500, 3500, 2000],
            '单间': [1800, 2500, 1500]
        }

    context = {
        'username': username,
        'useravatar': useravatar,
        'predictions': predictions,
        'cities': all_cities,
        'types': all_types,
        'database_type': 'MongoDB (演示模式)' if fallback_mode else 'MongoDB',
        'fallback_mode': fallback_mode
    }

    return render(request, 'mongo/pricePredict.html', context)
