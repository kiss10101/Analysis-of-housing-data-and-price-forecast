# enconding='utf-8'
import time
from collections import defaultdict
from django.shortcuts import render, redirect
from app.models import House, User, Histroy
from app.utils import getHistoryTableData
from django.http import JsonResponse
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
from django.db.models import Avg, Count, Min, Max

# Create your views here.
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')
        if User.objects.filter(username=name, password=password):
            user=User.objects.get(username=name, password=password)
            request.session['username'] = {'username':user.username,'avatar':str(user.avatar)}
            return redirect('index')
        else:
            msg = '信息错误！'
            return render(request, 'login.html', {"msg": msg})

# 02用户注册
def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        avatar = request.FILES.get('avatar')
        stu = User.objects.filter(username=name)
        if stu:
            msg = '用户已存在！'
            return render(request, 'register.html', {"msg": msg})
        else:
            User.objects.create(username=name,password=password,phone=phone,email=email,avatar=avatar)
            msg = "注册成功！"
            return render(request, 'login.html', {"msg": msg})
    if request.method == 'GET':
        return render(request,'register.html')
# 退出登录
def logOut(request):
    request.session.clear()
    return redirect('login')

def index(request):
    users = User.objects.all()
    data = {}
    for u in users:
        if data.get(str(u.time),-1) == -1:
            data[str(u.time)] = 1
        else:
            data[str(u.time)] += 1
    result = []
    for k,v in data.items():
        result.append({
            'name':k,
            'value':v
        })
    timeFormat = time.localtime()
    year = timeFormat.tm_year
    month = timeFormat.tm_mon
    day = timeFormat.tm_mday
    monthList = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    username = request.session['username'].get('username')
    useravatar = request.session['username'].get('avatar')
    newuserlist = User.objects.all().order_by('-time')[0:5]
    houses=House.objects.all().distinct()
    # 数据总量
    houseslength=len(houses)
    # 用户总量
    userlength=len(User.objects.all())
    averageprice=House.objects.all().order_by('-price')[0].price
    buildingtype = House.objects.all().order_by('-price')[0].building
    area_max = House.objects.all().order_by('-area')[0].area
    dict0={};str0=""
    # 设置合理的户型筛选规则
    MAX_ROOMS = 6  # 设置最大合理房间数

    # 统计符合条件的户型数量
    for i in House.objects.all():
        # 跳过价格异常的记录
        if i.price > 10000:  # 设置合理的价格上限
            continue
        
        # 跳过户型异常的记录
        is_valid_type = True
        try:
            # 假设格式是"3室2厅"这样
            if "室" in i.type:
                room_part = i.type.split('室')[0]
                if room_part.isdigit() and int(room_part) > MAX_ROOMS:
                    is_valid_type = False
        except:
            pass
        
        if not is_valid_type:
            continue
        
        # 统计合理范围内的数据
        if dict0.get(i.type,-1)==-1:
            dict0[i.type]=1
        else:
            dict0[i.type]+=1

    # 其余排序和拼接代码保持不变
    sorted_items = sorted(dict0.items(), key=lambda x: x[1], reverse=True)
    top_type_3_keys = [item[0] for item in sorted_items[:3]]
    for s in top_type_3_keys:
        str0=str0+s+"~"
    str0=str0[:-1]
    dict1={};str1=""
    for i in House.objects.all():
        if dict1.get(i.city,-1)==-1:
            dict1[i.city]=1
        else:
            dict1[i.city]+=1
    sorted_items = sorted(dict1.items(), key=lambda x: x[1], reverse=True)
    top_3_keys = [item[0] for item in sorted_items[:3]]
    for s in top_3_keys:
        str1=str1+s+"~"
    str1=str1[:-1]
    context={'username':username,'useravatar':useravatar,'houses':houses,'userTime':result,'newuserlist':newuserlist,'year':year,'month':monthList[month-1],'day':day,'houseslength':houseslength,'userlength':userlength
             ,'averageprice':averageprice,'str1':str1,'str0':str0,'buildingtype':buildingtype,'area_max':area_max}
    return render(request,'index.html',context)

def selfInfo(request):
    username = request.session['username'].get('username')
    useravatar = request.session['username'].get('avatar')
    if request.method == 'POST':
        phone=request.POST.get("phone")
        email=request.POST.get("email")
        password=request.POST.get("password")
        selfmes=User.objects.get(username=username)
        selfmes.phone=phone
        selfmes.email=email
        selfmes.password=password
        selfmes.save()
        userInfo = User.objects.get(username=username)
        context = {'username': username, 'useravatar': useravatar, 'userInfo': userInfo}
        return render(request, 'selfInfo.html', context)
    userInfo=User.objects.get(username=username)
    context={'username':username,'useravatar':useravatar,'userInfo':userInfo}
    return render(request,'selfInfo.html',context)

def tableData(request):
    username = request.session['username'].get('username')
    useravatar = request.session['username'].get('avatar')
    houses=House.objects.all().distinct()
    context={'username':username,'useravatar':useravatar,'houses':houses,}
    return render(request,'tableData.html',context)

def historyTableData(request):
    username = request.session['username'].get('username')
    userInfo = User.objects.get(username=username)
    historyData = getHistoryTableData.getHistoryData(userInfo)
    return render(request, 'collectTableData.html', {
        'username':username,
        'userInfo': userInfo,
        'historyData':historyData
    })
# 收藏
def addHistory(request,houseID):
    username = request.session.get("username").get('username')
    userInfo = User.objects.get(username=username)
    getHistoryTableData.addHistory(userInfo,houseID)
    return redirect('historyTableData')
# 房源地区分布
def houseDistribute(request):
    username = request.session['username'].get('username')
    useravatar = request.session['username'].get('avatar')
    types = list(House.objects.values_list('type', flat=True).distinct())
    defaultType = '不限'
    type_name = request.GET.get('type_name')
    if type_name in types:
        defaultType = type_name
        house = House.objects.all().filter(type=type_name).distinct();
    else:
        house = House.objects.all();
    dict1={};result1=[];dict2={};result2=[]
    for i in house:
        if dict1.get(i.city,-1)==-1:
            dict1[i.city]=1
        else:
            dict1[i.city]+=1
    for k,v in dict1.items():
        result1.append({
            'value': v,
            "name":k
        })
    for i in house:
        if dict2.get(i.street, -1) == -1:
            dict2[i.street] = 1
        else:
            dict2[i.street] += 1
    for k, v in dict2.items():
        result2.append({
            'value': v,
            "name": k
        })
    result2 = sorted(result2, key=lambda x: x['value'], reverse=True)[:10]
    context={'result1':result1,'result2':result2,'username':username,'useravatar':useravatar,'types':types,'defaultType':defaultType}
    return render(request,'houseDistribute.html',context)

def housetyperank(request):
    username = request.session['username'].get('username')
    useravatar = request.session['username'].get('avatar')
    list1_legend=[];list1=[];list2_legend=[];list2=[];list3_legend=[];list3=[]
    # 查询数据库，获取所有唯一的城市
    cities = House.objects.values_list('city', flat=True).distinct()
    # 将城市放入列表中
    citylist = list(cities)
    cityname=request.GET.get("cityname")
    top_3_types = House.objects.values('type').annotate(type_count=Count('type')).order_by('-type_count')[:3]
    # 如果需要返回具体的类型和数量，可以这样做：
    result = [{'type': item['type'], 'count': item['type_count']} for item in top_3_types]
    list_top_three = []
    for i in result:
        list_top_three.append(i['type'])
    if cityname !='不限':
        type1house=House.objects.filter(city=cityname).filter(type=list_top_three[0]).distinct().order_by('-price')[:5]
        type2house=House.objects.filter(city=cityname).filter(type=list_top_three[1]).distinct().order_by('-price')[:5]
        type3house=House.objects.filter(city=cityname).filter(type=list_top_three[2]).distinct().order_by('-price')[:5]
        for p in type1house:
            if p.title in list1_legend:
                pass
            else:
                list1_legend.append(p.title)
                list1.append({'value':p.price,'name':p.title})
        for p in type2house:
            if p.title in list2_legend:
                pass
            else:
                list2_legend.append(p.title)
                list2.append({'value':p.price,'name':p.title})
        for p in type3house:
            if p.title in list3_legend:
                pass
            else:
                list3_legend.append(p.title)
                list3.append({'value':p.price,'name':p.title})
        context={'username':username,'useravatar':useravatar,'citylist':citylist,'list1_legend':list1_legend,'list1':list1,'list2_legend':list2_legend,'list2':list2,'list3_legend':list3_legend,'list3':list3}
    if cityname not in citylist:
        type1house=House.objects.all().filter(type=list_top_three[0]).order_by('-price')[:10]
        type2house=House.objects.all().filter(type=list_top_three[1]).order_by('-price')[:10]
        type3house=House.objects.all().filter(type=list_top_three[2]).order_by('-price')[:10]
        for p in type1house:
            list1_legend.append(p.title)
            list1.append({'value':p.price,'name':p.title})
        for p in type2house:
            list2_legend.append(p.title)
            list2.append({'value':p.price,'name':p.title})
        for p in type3house:
            list3_legend.append(p.title)
            list3.append({'value':p.price,'name':p.title})
        context = {'username': username, 'useravatar': useravatar, 'citylist': citylist, 'list1_legend': list1_legend,'list1': list1, 'list2_legend': list2_legend, 'list2': list2,
                   'list3_legend': list3_legend,'list3': list3,'list_top_three': list_top_three}
    return render(request, 'housetyperank.html', context)

def housewordcloud(request):
    username = request.session['username'].get('username')
    useravatar = request.session['username'].get('avatar')
    # wouldCloud.wouldCloudMain_street()
    # wouldCloud.wouldCloudMain_building()
    context = {'username':username,'useravatar':useravatar}
    return render(request,'housewordcloud.html',context)

def typeincity(request):
    username = request.session['username'].get('username')
    useravatar = request.session['username'].get('avatar')

    # 获取所有独特的房源类型
    types = list(House.objects.values_list('type', flat=True).distinct())
    # 获取所有独特的城市
    cities = list(House.objects.values_list('city', flat=True).distinct())
    # 创建一个字典来存储房源类型和城市的计数
    house_counts = {}
    # 初始化字典，为每种房源类型创建一个与城市数量相同的列表，初始值为0
    for type_ in types:
        house_counts[type_] = [0] * len(cities)
    # 获取所有房源按类型和城市的计数
    annotated_houses = House.objects.values('type', 'city').annotate(count=Count('id'))
    # 填充字典
    for ah in annotated_houses:
        type_ = ah['type']
        city = ah['city']
        count = ah['count']
        # 找到城市在城市列表中的索引
        city_index = cities.index(city)
        # 更新房源类型的城市计数
        house_counts[type_][city_index] = count
    # 将字典转换为嵌套列表
    result = [house_counts[type_] for type_ in sorted(types)]

    context = {'house_counts':house_counts,'username':username,'useravatar':useravatar,'types':types,'cities':cities,'result':result}
    return render(request,'typeincity.html',context)

def servicemoney(request):
    username = request.session['username'].get('username')
    useravatar = request.session['username'].get('avatar')

    # 获取所有房源数据
    houses = House.objects.all().distinct()
    cities = list(House.objects.values_list('city', flat=True).distinct())

    # 计算每个城市每种房源类型的平均价格
    avg_prices = defaultdict(lambda: defaultdict(list))

    for house in houses:
        avg_prices[house.city][house.type].append(house.price)

    # 计算平均值
    for city, types in avg_prices.items():
        for house_type, prices in types.items():
            avg_prices[city][house_type] = round(sum(prices) / len(prices),2)
    # 准备 yAxis 和 series 数据
    yAxis_data = list(avg_prices.keys())
    series = []

    for house_type in set(house.type for house in houses):
        series_data = [avg_prices[city][house_type] if house_type in avg_prices[city] else 0 for city in yAxis_data]
        series.append({
            'name': house_type,
            'type': 'bar',
            'stack': 'total',
            'label': {
                'show': 'true'
            },
            'emphasis': {
                'focus': 'series'
            },
            'data': series_data
        })
    context = {'username': username, 'useravatar':useravatar, 'series': series,'cities': cities}
    return render(request, 'servicemoney.html',context)


def train_house_model(request):
    # 获取所有房源数据
    queryset = House.objects.all().values()
    data = pd.DataFrame.from_records(queryset)

    if data.empty:
        return JsonResponse({'error': 'No data available'}, status=400)

    # 定义特征和目标
    features = ['type', 'city', 'area', 'direct']
    X = data[features]
    y = data['price']

    # 数据预处理：对分类变量进行编码
    categorical_features = ['type', 'city', 'direct']
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])

    # 创建模型管道
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100))
    ])

    # 训练模型
    model.fit(X, y)

    # 保存模型到文件
    joblib.dump(model, 'house_price_model.joblib')

    return JsonResponse({'status': 'Model trained successfully'})


def predict_all_prices(request):
    username = request.session['username'].get('username')
    useravatar = request.session['username'].get('avatar')
    try:
        model = joblib.load('house_price_model.joblib')
    except FileNotFoundError:
        return JsonResponse({'error': 'Model not found. Train the model first.'}, status=404)

    # 获取排序后的唯一值（确保顺序一致）
    all_cities = sorted(House.objects.values_list('city', flat=True).distinct())
    all_types = sorted(House.objects.values_list('type', flat=True).distinct())

    # 预加载全局统计数据
    global_stats = {
        'avg_area': House.objects.aggregate(avg=Avg('area'))['avg'] or 0,
        'common_direct': House.objects.values('direct').annotate(
            count=Count('direct')).order_by('-count').first()['direct'] or '未知'
    }

    # 批量预加载每个类型的统计数据
    type_stats = {}
    for house_type in all_types:
        type_data = House.objects.filter(type=house_type)
        type_stats[house_type] = {
            'avg_area': type_data.aggregate(avg=Avg('area'))['avg'] or global_stats['avg_area'],
            'common_direct': type_data.values('direct').annotate(
                count=Count('direct')).order_by('-count').first()['direct'] or global_stats['common_direct']
        }

    # 生成预测结果字典
    predictions = {}
    for house_type in all_types:
        price_list = []
        for city in all_cities:  # 按固定顺序遍历城市
            # 获取特征值（使用三级回退策略）
            city_data = House.objects.filter(type=house_type, city=city)

            if city_data.exists():
                area = city_data.aggregate(avg=Avg('area'))['avg']
                direct = city_data.values('direct').annotate(
                    count=Count('direct')).order_by('-count').first()['direct']
            else:
                area = type_stats[house_type]['avg_area']
                direct = type_stats[house_type]['common_direct']

            # 最终处理空值
            final_area = area or global_stats['avg_area']
            final_direct = direct or global_stats['common_direct']

            # 构建输入数据
            input_data = pd.DataFrame([{
                'type': house_type,
                'city': city,
                'area': final_area,
                'direct': final_direct
            }])

            # 执行预测
            try:
                predicted_price = round(float(model.predict(input_data)[0]), 2)
            except Exception as e:
                predicted_price = 0.00  # 错误兜底值
            price_list.append(predicted_price)
        predictions[house_type] = price_list
    context = {'username': username, 'useravatar':useravatar,'predictions': predictions,'cities': all_cities,'types': all_types}
    return render(request, 'pricePredict.html', context)

def heatmap_analysis(request):
    """热力图分析房价影响因素"""
    from django.db.models import Avg, Min, Max
    
    username = request.session['username'].get('username')
    useravatar = request.session['username'].get('avatar')
    
    # 获取所有房源数据
    houses = House.objects.all()
    
    # 提取面积与价格关系数据
    area_price_data = []
    for house in houses:
        # 过滤异常值
        if house.price < 10000 and house.area > 0 and house.area < 300:
            area_price_data.append([house.area, house.price])
    
    # 提取城市与价格关系数据
    cities = list(House.objects.values_list('city', flat=True).distinct())
    city_type_price = []
    
    # 获取所有独特的房源类型
    types = list(House.objects.values_list('type', flat=True).distinct())
    
    # 计算每个城市每种类型的平均价格
    for city_idx, city in enumerate(cities):
        for type_idx, house_type in enumerate(types):
            avg_price = House.objects.filter(city=city, type=house_type).aggregate(avg=Avg('price'))['avg']
            if avg_price:  # 确保有数据
                city_type_price.append([city_idx, type_idx, avg_price])
    
    # 定义有效的朝向列表
    valid_directions = ['东', '南', '西', '北', '东南', '东北', '西南', '西北', '南北', '东西']
    
    # 直接使用有效朝向过滤房源数据
    filtered_houses = houses.filter(direct__in=valid_directions)
    
    # 如果过滤后没有数据，说明没有正确的朝向数据
    if not filtered_houses.exists():
        # 只创建一个默认朝向，避免展示错误数据
        directs = ['未知']
        area_direct_price = []
        
        # 将area分为10个区间
        area_ranges = []
        min_area = houses.aggregate(min_area=Min('area'))['min_area'] or 0
        max_area = houses.aggregate(max_area=Max('area'))['max_area'] or 100
        step = (max_area - min_area) / 10
        
        for i in range(10):
            area_ranges.append([min_area + i * step, min_area + (i + 1) * step])
        
        # 不按朝向筛选，只按面积区间计算平均价格
        for area_idx, area_range in enumerate(area_ranges):
            avg_price = houses.filter(
                area__gte=area_range[0], 
                area__lt=area_range[1]
            ).aggregate(avg=Avg('price'))['avg']
            
            if avg_price:  # 确保有数据
                area_direct_price.append([area_idx, 0, avg_price])  # 使用索引0作为默认朝向
    else:
        # 使用已过滤的正确朝向数据
        directs = valid_directions
        area_direct_price = []
        
        # 将area分为10个区间
        area_ranges = []
        min_area = filtered_houses.aggregate(min_area=Min('area'))['min_area'] or 0
        max_area = filtered_houses.aggregate(max_area=Max('area'))['max_area'] or 100
        step = (max_area - min_area) / 10
        
        for i in range(10):
            area_ranges.append([min_area + i * step, min_area + (i + 1) * step])
        
        # 计算每个面积区间和朝向组合的平均价格
        for area_idx, area_range in enumerate(area_ranges):
            for direct_idx, direct in enumerate(directs):
                # 计算该区间内该朝向的平均价格
                avg_price = filtered_houses.filter(
                    area__gte=area_range[0], 
                    area__lt=area_range[1], 
                    direct=direct
                ).aggregate(avg=Avg('price'))['avg']
                
                if avg_price:  # 确保有数据
                    area_direct_price.append([area_idx, direct_idx, avg_price])
    
    context = {
        'username': username,
        'useravatar': useravatar,
        'area_price_data': area_price_data,
        'city_type_price': city_type_price,
        'area_direct_price': area_direct_price,
        'cities': cities,
        'types': types,
        'directs': directs,
        'area_ranges': area_ranges
    }
    
    return render(request, 'heatmap_analysis.html', context)