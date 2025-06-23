"""
URL configuration for 基于Python的携程Top10热门景点数据分析与展示 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views
urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('index/', views.index, name='index'),
    path('logOut/', views.logOut, name='logOut'),
    path('selfInfo/', views.selfInfo, name='selfInfo'),
    path('tableData/', views.tableData, name='tableData'),
    path('addHistory/<int:houseID>', views.addHistory, name='addHistory'),
    path('historyTableData/', views.historyTableData, name='historyTableData'),
    path('houseDistribute/', views.houseDistribute, name='houseDistribute'),
    path('housetyperank/', views.housetyperank, name='housetyperank'),
    path('typeincity/', views.typeincity, name='typeincity'),

    path('housewordcloud/', views.housewordcloud, name='housewordcloud'),
    path('servicemoney/', views.servicemoney, name='servicemoney'),
    path('train-model/', views.train_house_model, name='train_model'),
    path('predict-all-prices/', views.predict_all_prices, name='predict_all_prices'),
    path('pricePredict/', views.predict_all_prices, name='price_predict_alt'),
    path('heatmap-analysis/', views.heatmap_analysis, name='heatmap_analysis'),
    path('heatmap_analysis/', views.heatmap_analysis, name='heatmap_analysis_alt'),

]