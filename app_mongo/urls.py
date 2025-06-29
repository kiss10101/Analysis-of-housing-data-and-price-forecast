# -*- coding: utf-8 -*-
"""
MongoDB版本的URL配置
"""

from django.urls import path
from app_mongo import views
from app_mongo import python_viz_views

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

    # Python可视化模块
    path('python-viz/', python_viz_views.python_dashboard, name='python_dashboard'),
    path('python-viz/static-charts/', python_viz_views.static_charts_page, name='static_charts_page'),
    path('python-viz/interactive-charts/', python_viz_views.interactive_charts_page, name='interactive_charts_page'),
    path('python-viz/api/chart/', python_viz_views.chart_api, name='chart_api'),

    # Python可视化版本的页面
    path('python-housetyperank/', python_viz_views.python_housetyperank, name='python_housetyperank'),
    path('python-servicemoney/', python_viz_views.python_servicemoney, name='python_servicemoney'),

    # 默认重定向到登录页
    path('', views.mongo_login, name='mongo_default'),
]
