#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session验证中间件
防止用户信息显示错误和session数据混乱
"""

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
import logging

logger = logging.getLogger(__name__)

class SessionValidationMiddleware(MiddlewareMixin):
    """
    Session验证中间件
    确保用户session数据的完整性和一致性
    """
    
    def process_request(self, request):
        """
        处理请求前验证session
        """
        path = request.path
        
        # 跳过不需要验证的路径
        skip_paths = [
            '/app/login/',
            '/app/register/',
            '/mongo/login/',
            '/mongo/register/',
            '/admin/',
            '/static/',
            '/media/',
            '/'
        ]
        
        # 检查是否需要跳过验证
        for skip_path in skip_paths:
            if path.startswith(skip_path):
                return None
        
        # MySQL版本路径验证
        if path.startswith('/app/'):
            return self._validate_mysql_session(request)
        
        # MongoDB版本路径验证
        elif path.startswith('/mongo/'):
            return self._validate_mongo_session(request)
        
        return None
    
    def _validate_mysql_session(self, request):
        """
        验证MySQL版本的session
        """
        if 'username' not in request.session:
            logger.warning(f"MySQL版本访问未登录: {request.path}")
            return redirect('login')
        
        # 验证session数据完整性
        username_data = request.session.get('username')
        if not isinstance(username_data, dict):
            logger.error(f"MySQL版本session数据格式错误: {username_data}")
            request.session.clear()
            return redirect('login')
        
        if 'username' not in username_data:
            logger.error(f"MySQL版本session缺少用户名: {username_data}")
            request.session.clear()
            return redirect('login')
        
        # 清理可能的MongoDB session数据冲突
        if 'mongo_username' in request.session:
            logger.info("清理MySQL版本中的MongoDB session数据")
            del request.session['mongo_username']
            if 'fallback_mode' in request.session:
                del request.session['fallback_mode']
        
        return None
    
    def _validate_mongo_session(self, request):
        """
        验证MongoDB版本的session
        """
        if 'mongo_username' not in request.session:
            logger.warning(f"MongoDB版本访问未登录: {request.path}")
            return redirect('mongo_login')
        
        # 验证session数据完整性
        mongo_username_data = request.session.get('mongo_username')
        if not isinstance(mongo_username_data, dict):
            logger.error(f"MongoDB版本session数据格式错误: {mongo_username_data}")
            request.session.clear()
            return redirect('mongo_login')
        
        if 'username' not in mongo_username_data:
            logger.error(f"MongoDB版本session缺少用户名: {mongo_username_data}")
            request.session.clear()
            return redirect('mongo_login')
        
        # 清理可能的MySQL session数据冲突
        if 'username' in request.session:
            logger.info("清理MongoDB版本中的MySQL session数据")
            del request.session['username']
        
        return None
    
    def process_response(self, request, response):
        """
        处理响应，记录session状态
        """
        if hasattr(request, 'session') and request.session.session_key:
            # 记录当前session状态用于调试
            path = request.path
            if path.startswith('/app/') and 'username' in request.session:
                username = request.session['username'].get('username', 'unknown')
                logger.debug(f"MySQL版本响应 - 用户: {username}, 路径: {path}")
            elif path.startswith('/mongo/') and 'mongo_username' in request.session:
                username = request.session['mongo_username'].get('username', 'unknown')
                logger.debug(f"MongoDB版本响应 - 用户: {username}, 路径: {path}")
        
        return response
