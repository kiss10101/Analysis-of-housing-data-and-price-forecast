# -*- coding: utf-8 -*-
"""
MongoDB版本的URL配置
"""

from django.urls import path
from app_mongo import views

urlpatterns = [
    # 用户认证
    path('login/', views.mongo_login, name='mongo_login'),
    path('register/', views.mongo_register, name='mongo_register'),
    path('logOut/', views.mongo_logout, name='mongo_logout'),
    
    # 主要页面
    path('index/', views.mongo_index, name='mongo_index'),
    path('selfInfo/', views.mongo_self_info, name='mongo_self_info'),
    
    # 数据统计
    path('tableData/', views.mongo_table_data, name='mongo_table_data'),
    path('api/tableData/', views.mongo_table_data_api, name='mongo_table_data_api'),
    path('historyTableData/', views.mongo_history_table_data, name='mongo_history_table_data'),
    path('addHistory/<str:house_id>/', views.mongo_add_history, name='mongo_add_history'),
    
    # 可视化图表
    path('houseDistribute/', views.mongo_house_distribute, name='mongo_house_distribute'),
    path('typeincity/', views.mongo_type_in_city, name='mongo_type_in_city'),
    path('housewordcloud/', views.mongo_house_wordcloud, name='mongo_house_wordcloud'),
    path('housetyperank/', views.mongo_house_type_rank, name='mongo_house_type_rank'),
    path('servicemoney/', views.mongo_service_money, name='mongo_service_money'),
    path('heatmap-analysis/', views.mongo_heatmap_analysis, name='mongo_heatmap_analysis'),
    path('heatmap_analysis/', views.mongo_heatmap_analysis, name='mongo_heatmap_analysis_alt'),

    # 房价预测
    path('predict-all-prices/', views.mongo_predict_all_prices, name='mongo_predict_all_prices'),
    path('pricePredict/', views.mongo_predict_all_prices, name='mongo_price_predict_alt'),

    # 默认重定向到登录页
    path('', views.mongo_login, name='mongo_default'),
]
