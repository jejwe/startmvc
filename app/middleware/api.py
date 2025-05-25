#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

import json
import cherrypy
from startmvc.core.Middleware import Middleware

class Api(Middleware):
    """
    API中间件
    用于处理API请求和响应
    """
    
    def before(self, request):
        """
        请求前处理
        
        Args:
            request: 请求对象
            
        Returns:
            mixed: 如果返回Response对象，则中断请求，直接返回该Response
        """
        # 设置内容类型为JSON
        cherrypy.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        
        # 解析JSON请求体
        if request.method in ['POST', 'PUT', 'PATCH'] and request.headers.get('Content-Type', '').startswith('application/json'):
            try:
                # 读取请求体
                body = request.body.read().decode('utf-8')
                if body:
                    # 解析JSON
                    request.json_data = json.loads(body)
                else:
                    request.json_data = {}
            except json.JSONDecodeError:
                # 返回错误响应
                return self.json_response({
                    'error': 'Invalid JSON',
                    'code': 400,
                    'message': 'The request body is not valid JSON'
                }, 400)
        
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
        # 如果响应已经是JSON格式，则不做处理
        if response.headers.get('Content-Type', '').startswith('application/json'):
            return response
        
        # 如果响应是字典或列表，则转换为JSON
        if isinstance(response.body, (dict, list)):
            # 创建标准API响应格式
            api_response = {
                'code': 200,
                'message': 'success',
                'data': response.body
            }
            
            # 设置响应体为JSON字符串
            response.body = json.dumps(api_response, ensure_ascii=False)
            
            # 设置内容类型
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
        
        return response
    
    def json_response(self, data, status=200):
        """
        创建JSON响应
        
        Args:
            data: 响应数据
            status: HTTP状态码
            
        Returns:
            Response: JSON响应对象
        """
        # 设置响应状态码
        cherrypy.response.status = status
        
        # 设置内容类型
        cherrypy.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        
        # 返回JSON字符串
        return json.dumps(data, ensure_ascii=False)