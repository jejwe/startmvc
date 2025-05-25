#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

from startmvc.core.Middleware import Middleware
import cherrypy

class Auth(Middleware):
    """
    认证中间件
    用于验证用户是否已登录
    """
    
    def before(self, request):
        """
        请求前处理
        
        Args:
            request: 请求对象
            
        Returns:
            mixed: 如果返回Response对象，则中断请求，直接返回该Response
        """
        # 检查用户是否已登录
        if 'user_id' not in cherrypy.session:
            # 如果是管理员路由，则跳转到登录页面
            if request.path.startswith('/admin'):
                # 保存当前URL，登录后可以跳转回来
                cherrypy.session['redirect_url'] = request.path
                return self.redirect('/login')
            else:
                # 非管理员路由，设置未认证标志但允许继续访问
                request.authenticated = False
        else:
            # 用户已登录
            request.authenticated = True
            # 可以在这里加载用户信息
            request.user = self.load_user(cherrypy.session.get('user_id'))
        
        # 继续请求
        return None
    
    def after(self, request, response):
        """
        请求后处理
        
        Args:
            request: 请求对象
            response: 响应对象
            
        Returns:
            Response: 响应对象
        """
        # 可以在这里修改响应，例如添加响应头
        if hasattr(request, 'authenticated') and request.authenticated:
            response.headers['X-Authenticated'] = 'true'
        
        return response
    
    def load_user(self, user_id):
        """
        加载用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            dict: 用户信息
        """
        # 这里应该从数据库加载用户信息
        # 为了示例，我们返回一个模拟的用户对象
        return {
            'id': user_id,
            'username': 'user' + str(user_id),
            'email': 'user' + str(user_id) + '@example.com',
            'role': 'admin' if int(user_id) == 1 else 'user'
        }