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
from startmvc.core.Middleware import Middleware

class Cors(Middleware):
    """
    CORS中间件
    用于处理跨域资源共享
    """
    
    def before(self, request):
        """
        请求前处理
        
        Args:
            request: 请求对象
            
        Returns:
            mixed: 如果返回Response对象，则中断请求，直接返回该Response
        """
        # 获取请求的Origin
        origin = request.headers.get('Origin', '*')
        
        # 设置CORS响应头
        cherrypy.response.headers['Access-Control-Allow-Origin'] = origin
        cherrypy.response.headers['Access-Control-Allow-Credentials'] = 'true'
        cherrypy.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        cherrypy.response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        
        # 处理预检请求
        if request.method == 'OPTIONS':
            # 设置预检请求的有效期为1小时
            cherrypy.response.headers['Access-Control-Max-Age'] = '3600'
            
            # 返回空响应，状态码为200
            cherrypy.response.status = 200
            return ''
        
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
        # 确保CORS响应头存在
        if 'Access-Control-Allow-Origin' not in response.headers:
            origin = request.headers.get('Origin', '*')
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        return response