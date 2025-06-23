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
                    msg = '信息错误！'
                    return render(request, 'mongo/login.html', {"msg": msg})
            else:
                # 使用降级数据
                from .fallback_data import FallbackMongoUser
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

        try:
            # 检查MongoDB连接状态
            from .models import MONGODB_CONNECTION_SUCCESS

            if MONGODB_CONNECTION_SUCCESS:
                # 正常模式：使用MongoDB
                existing_user = MongoUser.objects(username=name).first()
                if existing_user:
                    msg = '用户已存在！'
                    return render(request, 'mongo/register.html', {"msg": msg})
                else:
                    # 创建新用户
                    new_user = MongoUser(
                        username=name,
                        password=password,
                        phone=phone or '',
                        email=email or '',
                        avatar=str(avatar) if avatar else ''
                    )
                    new_user.save()
                    msg = "注册成功！"
                    return render(request, 'mongo/login.html', {"msg": msg})
            else:
                # 降级模式：模拟注册成功
                msg = "注册成功！（演示模式）"
                return render(request, 'mongo/login.html', {"msg": msg})

        except Exception as e:
            # MongoDB操作失败，降级处理
            msg = "注册成功！（演示模式）"
            return render(request, 'mongo/login.html', {"msg": msg})

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
        # 降级模式：使用模拟数据
        from .fallback_data import get_fallback_stats, FALLBACK_USERS

        stats = get_fallback_stats()
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
            result = [{'name': item['_id'], 'value': item['count']} for item in user_time_data]
        except:
            result = [{'name': '2025-06-23', 'value': 1}]

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

    context = {
        'username': username,
        'useravatar': useravatar,
        'userTime': result,
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
        from .fallback_data import FallbackMongoUser
        userInfo = FallbackMongoUser.objects(username=username).first()
    else:
        try:
            userInfo = MongoUser.objects(username=username).first()
        except:
            # MongoDB查询失败，使用降级数据
            from .fallback_data import FallbackMongoUser
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

    if fallback_mode:
        # 降级模式：使用模拟数据
        from .fallback_data import FALLBACK_HOUSES, get_fallback_stats

        stats = get_fallback_stats()
        houses = FALLBACK_HOUSES
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
            'database_type': 'MongoDB (演示模式)',
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

            # 获取前100条数据作为示例（避免性能问题）
            houses_cursor = collection.find({}).limit(100)
            houses = list(houses_cursor)

            total = collection.count_documents({})
            cities = collection.distinct('location.city')
            rental_types = collection.distinct('rental_type')

            context = {
                'username': username,
                'useravatar': useravatar,
                'houses': houses,
                'total': total,
                'cities': cities,
                'rental_types': rental_types,
                'database_type': 'MongoDB',
                'server_side': False
            }
        except Exception as e:
            # MongoDB连接失败，使用降级数据
            from .fallback_data import FALLBACK_HOUSES, get_fallback_stats

            stats = get_fallback_stats()
            context = {
                'username': username,
                'useravatar': useravatar,
                'houses': FALLBACK_HOUSES,
                'total': len(FALLBACK_HOUSES),
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
        # 降级模式：使用模拟数据
        from .fallback_data import FALLBACK_HOUSES

        # 过滤数据
        filtered_houses = FALLBACK_HOUSES
        if search_value:
            filtered_houses = [
                house for house in FALLBACK_HOUSES
                if search_value.lower() in house['title'].lower() or
                   search_value.lower() in house['city'].lower()
            ]

        # 分页
        total_records = len(FALLBACK_HOUSES)
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
            columns = ['title', 'type', 'city', 'street', 'building', 'area', 'direct', 'price']
            sort_column = columns[order_column] if order_column < len(columns) else 'title'

            # 连接MongoDB
            import pymongo
            client = pymongo.MongoClient('mongodb://localhost:27017/')
            db = client['house_data']
            collection = db['houses']

            # 构建查询条件
            query = {}
            if search_value:
                # 全文搜索
                query = {
                    '$or': [
                        {'title': {'$regex': search_value, '$options': 'i'}},
                        {'city': {'$regex': search_value, '$options': 'i'}},
                        {'street': {'$regex': search_value, '$options': 'i'}},
                        {'building': {'$regex': search_value, '$options': 'i'}},
                        {'type': {'$regex': search_value, '$options': 'i'}},
                        {'direct': {'$regex': search_value, '$options': 'i'}}
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

            for doc in cursor:
                # 处理价格字段，可能是数字或字典
                price_value = doc.get('price', 0)
                if isinstance(price_value, dict):
                    price_str = f"{price_value.get('monthly_rent', 0):.0f}"
                else:
                    price_str = f"{price_value:.0f}" if isinstance(price_value, (int, float)) else str(price_value)

                # 处理面积字段
                area_value = doc.get('area', 0)
                area_str = f"{area_value:.1f}" if isinstance(area_value, (int, float)) else str(area_value)

                row = [
                    doc.get('title', ''),
                    doc.get('type', ''),
                    doc.get('city', ''),
                    doc.get('street', ''),
                    doc.get('building', ''),
                    area_str,
                    doc.get('direct', ''),
                    price_str
                ]
                data.append(row)
        except:
            # MongoDB查询失败，使用降级数据
            from .fallback_data import FALLBACK_HOUSES

            total_records = len(FALLBACK_HOUSES)
            filtered_records = total_records

            data = []
            for house in FALLBACK_HOUSES[:length]:
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
        # 降级模式：使用模拟收藏数据
        from .fallback_data import FallbackMongoUser, FALLBACK_HOUSES

        user = FallbackMongoUser.objects(username=username).first()

        # 模拟收藏历史
        history_data = [
            {
                'house': FALLBACK_HOUSES[0],
                'collected_time': '2025-06-23 10:00:00'
            },
            {
                'house': FALLBACK_HOUSES[1],
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
            # MongoDB查询失败，使用降级数据
            from .fallback_data import FallbackMongoUser, FALLBACK_HOUSES

            user = FallbackMongoUser.objects(username=username).first()
            history_data = [
                {
                    'house': FALLBACK_HOUSES[0],
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
    username = request.session.get("mongo_username").get('username')
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
    fallback_mode = request.session.get('fallback_mode', False)

    if fallback_mode:
        # 降级模式：使用模拟数据
        from .fallback_data import FALLBACK_HOUSES, get_fallback_stats

        stats = get_fallback_stats()
        types = stats['rental_types']
        defaultType = '不限'
        type_name = request.GET.get('type_name')

        # 过滤数据
        filtered_houses = FALLBACK_HOUSES
        if type_name and type_name in types:
            defaultType = type_name
            filtered_houses = [h for h in FALLBACK_HOUSES if h['rental_type'] == type_name]

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

        except:
            # MongoDB查询失败，使用降级数据
            from .fallback_data import FALLBACK_HOUSES, get_fallback_stats

            stats = get_fallback_stats()
            types = stats['rental_types']
            defaultType = '不限'

            result1 = [{'value': 2, 'name': '广州'}, {'value': 1, 'name': '深圳'}]
            result2 = [{'value': 1, 'name': '体育西路'}, {'value': 1, 'name': '中山路'}]

    context = {
        'result1': result1,
        'result2': result2,
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
    fallback_mode = request.session.get('fallback_mode', False)

    if fallback_mode:
        # 降级模式：使用模拟数据
        from .fallback_data import FALLBACK_HOUSES

        # 统计房型分布
        type_count = {}
        for house in FALLBACK_HOUSES:
            rental_type = house['rental_type']
            type_count[rental_type] = type_count.get(rental_type, 0) + 1

        result = [{'name': rental_type, 'value': count} for rental_type, count in type_count.items()]

    else:
        try:
            # 正常模式：使用MongoDB数据
            type_distribution = MongoQueryHelper.get_type_distribution()

            # 格式化数据为ECharts格式
            result = []
            for item in type_distribution:
                result.append({
                    'name': item['_id'] or '未知',
                    'value': item['count']
                })
        except:
            # MongoDB查询失败，使用降级数据
            result = [
                {'name': '整租', 'value': 3},
                {'name': '合租', 'value': 2}
            ]

    context = {
        'username': username,
        'useravatar': useravatar,
        'result': json.dumps(result),
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
    fallback_mode = request.session.get('fallback_mode', False)

    if fallback_mode:
        # 降级模式：使用模拟数据
        from .fallback_data import FALLBACK_HOUSES

        # 统计房型价格
        type_stats = {}
        for house in FALLBACK_HOUSES:
            rental_type = house['rental_type']
            price = house['price']
            if rental_type not in type_stats:
                type_stats[rental_type] = {'prices': [], 'count': 0}
            type_stats[rental_type]['prices'].append(price)
            type_stats[rental_type]['count'] += 1

        # 计算平均价格并排序
        type_rank_data = []
        for rental_type, stats in type_stats.items():
            avg_price = sum(stats['prices']) / len(stats['prices'])
            type_rank_data.append({
                'type': rental_type,
                'avg_price': avg_price,
                'count': stats['count']
            })

        type_rank_data.sort(key=lambda x: x['avg_price'], reverse=True)

        types = [item['type'] for item in type_rank_data]
        avg_prices = [round(item['avg_price'], 2) for item in type_rank_data]
        counts = [item['count'] for item in type_rank_data]

    else:
        try:
            # 正常模式：使用MongoDB数据
            pipeline = [
                {
                    '$group': {
                        '_id': '$rental_type',
                        'avg_price': {'$avg': '$price.monthly_rent'},
                        'count': {'$sum': 1}
                    }
                },
                {'$sort': {'avg_price': -1}}
            ]

            type_rank_data = list(HouseDocument.objects.aggregate(pipeline))

            # 格式化数据
            types = []
            avg_prices = []
            counts = []

            for item in type_rank_data:
                types.append(item['_id'] or '未知')
                # 处理None值
                avg_price = item['avg_price']
                if avg_price is not None:
                    avg_prices.append(round(avg_price, 2))
                else:
                    avg_prices.append(0)
                counts.append(item['count'])
        except:
            # MongoDB查询失败，使用降级数据
            types = ['整租', '合租']
            avg_prices = [4500.0, 2000.0]
            counts = [3, 2]

    context = {
        'username': username,
        'useravatar': useravatar,
        'types': json.dumps(types),
        'avg_prices': json.dumps(avg_prices),
        'counts': json.dumps(counts),
        'database_type': 'MongoDB (演示模式)' if fallback_mode else 'MongoDB',
        'fallback_mode': fallback_mode
    }

    return render(request, 'mongo/housetyperank.html', context)

# MongoDB版本的价钱影响
def mongo_service_money(request):
    # 检查用户是否已登录
    if 'mongo_username' not in request.session:
        return redirect('mongo_login')

    username = request.session['mongo_username'].get('username')
    useravatar = request.session['mongo_username'].get('avatar')
    fallback_mode = request.session.get('fallback_mode', False)

    if fallback_mode:
        # 降级模式：使用模拟数据
        area_ranges = ['30㎡以下', '30-50㎡', '50-80㎡', '80-120㎡', '120㎡以上']
        avg_prices = [1500, 2500, 3500, 5000, 7000]
    else:
        try:
            # 正常模式：使用MongoDB数据
            pipeline = [
                {
                    '$project': {
                        'area': '$features.area',
                        'price': '$price.monthly_rent',
                        'area_range': {
                            '$switch': {
                                'branches': [
                                    {'case': {'$lt': ['$features.area', 30]}, 'then': '30㎡以下'},
                                    {'case': {'$lt': ['$features.area', 50]}, 'then': '30-50㎡'},
                                    {'case': {'$lt': ['$features.area', 80]}, 'then': '50-80㎡'},
                                    {'case': {'$lt': ['$features.area', 120]}, 'then': '80-120㎡'},
                                ],
                                'default': '120㎡以上'
                            }
                        }
                    }
                },
                {
                    '$group': {
                        '_id': '$area_range',
                        'avg_price': {'$avg': '$price'},
                        'count': {'$sum': 1}
                    }
                },
                {'$sort': {'avg_price': 1}}
            ]

            area_price_data = list(HouseDocument.objects.aggregate(pipeline))

            # 格式化数据
            area_ranges = []
            avg_prices = []

            for item in area_price_data:
                area_ranges.append(item['_id'])
                avg_prices.append(round(item['avg_price'], 2))
        except:
            # MongoDB查询失败，使用降级数据
            area_ranges = ['30㎡以下', '30-50㎡', '50-80㎡', '80-120㎡', '120㎡以上']
            avg_prices = [1500, 2500, 3500, 5000, 7000]

    context = {
        'username': username,
        'useravatar': useravatar,
        'area_ranges': json.dumps(area_ranges),
        'avg_prices': json.dumps(avg_prices),
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
    fallback_mode = request.session.get('fallback_mode', False)

    if fallback_mode:
        # 降级模式：使用模拟数据
        cities = ['广州', '深圳']
        types = ['整租', '合租']
        city_type_price = [
            [0, 0, 4500],  # 广州-整租
            [0, 1, 2000],  # 广州-合租
            [1, 0, 6000],  # 深圳-整租
            [1, 1, 3000]   # 深圳-合租
        ]
        area_price_data = [
            [20, 1500], [30, 2000], [50, 3000], [80, 4500], [120, 6800]
        ]
    else:
        try:
            # 正常模式：使用MongoDB数据
            city_type_pipeline = [
                {
                    '$group': {
                        '_id': {
                            'city': '$city',
                            'type': '$type'
                        },
                        'avg_price': {'$avg': '$price'}
                    }
                }
            ]

            city_type_data = list(HouseDocument.objects.aggregate(city_type_pipeline))

            # 获取所有城市和户型，处理可能的KeyError
            cities = list(set([item['_id']['city'] for item in city_type_data if item['_id'].get('city')]))
            types = list(set([item['_id']['type'] for item in city_type_data if item['_id'].get('type')]))

            # 格式化热力图数据
            city_type_price = []
            for i, city in enumerate(cities):
                for j, house_type in enumerate(types):
                    price = 0
                    for item in city_type_data:
                        if (item['_id'].get('city') == city and
                            item['_id'].get('type') == house_type and
                            item['avg_price'] is not None):
                            price = round(item['avg_price'], 2)
                            break
                    city_type_price.append([i, j, price])

            # 获取面积价格散点图数据
            area_price_pipeline = [
                {
                    '$project': {
                        'area': '$area',
                        'price': '$price'
                    }
                },
                {'$limit': 1000}  # 限制数据量以提高性能
            ]

            area_price_raw = list(HouseDocument.objects.aggregate(area_price_pipeline))
            area_price_data = [[float(item['area']), float(item['price'])] for item in area_price_raw if item.get('area') and item.get('price')]
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

    context = {
        'username': username,
        'useravatar': useravatar,
        'cities': json.dumps(cities),
        'types': json.dumps(types),
        'city_type_price': json.dumps(city_type_price),
        'area_price_data': json.dumps(area_price_data),
        'directs': json.dumps(['南', '北', '东', '西', '东南', '西南', '东北', '西北']),
        'area_ranges': json.dumps([['0', '30'], ['30', '50'], ['50', '80'], ['80', '120'], ['120', '200']]),
        'area_direct_price': json.dumps([]),  # 简化版本，可以后续完善
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

    if fallback_mode:
        # 降级模式：使用模拟数据
        price_ranges = ['2000以下', '2000-3000', '3000-4000', '4000-5000', '5000以上']
        counts = [1, 2, 1, 1, 0]
    else:
        try:
            # 正常模式：使用MongoDB数据
            price_distribution_pipeline = [
                {
                    '$group': {
                        '_id': {
                            '$switch': {
                                'branches': [
                                    {'case': {'$lt': ['$price', 2000]}, 'then': '2000以下'},
                                    {'case': {'$lt': ['$price', 3000]}, 'then': '2000-3000'},
                                    {'case': {'$lt': ['$price', 4000]}, 'then': '3000-4000'},
                                    {'case': {'$lt': ['$price', 5000]}, 'then': '4000-5000'},
                                ],
                                'default': '5000以上'
                            }
                        },
                        'count': {'$sum': 1}
                    }
                },
                {'$sort': {'_id': 1}}
            ]

            price_dist_data = list(HouseDocument.objects.aggregate(price_distribution_pipeline))

            # 格式化数据
            price_ranges = []
            counts = []

            for item in price_dist_data:
                price_ranges.append(item['_id'])
                counts.append(item['count'])
        except:
            # MongoDB查询失败，使用降级数据
            price_ranges = ['2000以下', '2000-3000', '3000-4000', '4000-5000', '5000以上']
            counts = [1, 2, 1, 1, 0]

    context = {
        'username': username,
        'useravatar': useravatar,
        'price_ranges': json.dumps(price_ranges),
        'counts': json.dumps(counts),
        'database_type': 'MongoDB (演示模式)' if fallback_mode else 'MongoDB',
        'fallback_mode': fallback_mode
    }

    return render(request, 'mongo/pricePredict.html', context)
