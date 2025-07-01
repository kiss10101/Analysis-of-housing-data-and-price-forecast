# -*- coding: utf-8 -*-
"""
MongoDB版本自定义装饰器
"""

from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

def mongo_login_required(view_func):
    """
    MongoDB版本的登录验证装饰器
    检查session中是否有mongo_username
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # 检查session中是否有MongoDB用户信息
        if 'mongo_username' not in request.session:
            # 如果没有登录，重定向到MongoDB登录页面
            login_url = reverse('mongo_login')
            # 保存当前页面URL，登录后跳转回来
            next_url = request.get_full_path()
            return redirect(f"{login_url}?next={next_url}")
        
        # 如果已登录，继续执行原视图
        return view_func(request, *args, **kwargs)
    
    return wrapper
