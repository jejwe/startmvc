#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

import cherrypy
import secrets
import re
from startmvc.core.Middleware import Middleware

class Csrf(Middleware):
    """
    CSRF中间件
    用于防止跨站请求伪造
    """
    
    def __init__(self):
        """
        构造函数
        """
        super().__init__()
        self.token_name = '_token'
        self.header_name = 'X-CSRF-TOKEN'
        self.cookie_name = 'XSRF-TOKEN'
        self.exempt_urls = [
            r'^/api/',  # API路由豁免
            r'^/webhook/',  # Webhook路由豁免
        ]
    
    def before(self, request):
        """
        请求前处理
        
        Args:
            request: 请求对象
            
        Returns:
            mixed: 如果返回Response对象，则中断请求，直接返回该Response
        """
        # 检查是否需要CSRF保护
        if not self._should_check(request):
            return None
        
        # 获取会话中的CSRF令牌
        token = cherrypy.session.get(self.token_name)
        
        # 如果令牌不存在，则生成一个新的
        if not token:
            token = self._generate_token()
            cherrypy.session[self.token_name] = token
        
        # 设置CSRF令牌Cookie
        cherrypy.response.cookie[self.cookie_name] = token
        cherrypy.response.cookie[self.cookie_name]['path'] = '/'
        cherrypy.response.cookie[self.cookie_name]['httponly'] = False
        cherrypy.response.cookie[self.cookie_name]['samesite'] = 'Lax'
        
        # 如果是GET请求，则不需要验证令牌
        if request.method == 'GET':
            return None
        
        # 验证CSRF令牌
        if not self._validate_token(request, token):
            # 返回错误响应
            return self.error_response('CSRF token mismatch', 403)
        
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
        return response
    
    def _should_check(self, request):
        """
        检查是否需要CSRF保护
        
        Args:
            request: 请求对象
            
        Returns:
            bool: 是否需要CSRF保护
        """
        # 如果是只读请求，则不需要CSRF保护
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return False
        
        # 检查是否在豁免列表中
        for pattern in self.exempt_urls:
            if re.match(pattern, request.path):
                return False
        
        return True
    
    def _generate_token(self):
        """
        生成CSRF令牌
        
        Returns:
            str: CSRF令牌
        """
        return secrets.token_hex(32)
    
    def _validate_token(self, request, token):
        """
        验证CSRF令牌
        
        Args:
            request: 请求对象
            token: CSRF令牌
            
        Returns:
            bool: 是否有效
        """
        # 从请求头中获取令牌
        header_token = request.headers.get(self.header_name)
        if header_token and header_token == token:
            return True
        
        # 从表单中获取令牌
        form_token = request.params.get(self.token_name)
        if form_token and form_token == token:
            return True
        
        # 从Cookie中获取令牌
        cookie_token = request.cookie.get(self.cookie_name)
        if cookie_token and cookie_token.value == token:
            return True
        
        return False
    
    def error_response(self, message, status=403):
        """
        创建错误响应
        
        Args:
            message: 错误消息
            status: HTTP状态码
            
        Returns:
            Response: 错误响应对象
        """
        # 设置响应状态码
        cherrypy.response.status = status
        
        # 返回错误页面
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error {status}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .error {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 4px; }}
                h1 {{ margin-top: 0; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h1>Error {status}</h1>
                <p>{message}</p>
            </div>
        </body>
        </html>
        """