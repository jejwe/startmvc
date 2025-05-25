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
import json
import time
from startmvc.core.Controller import Controller

class Index(Controller):
    """API控制器"""
    
    def index(self, *args):
        """
        API首页
        """
        # 返回API信息
        return {
            'name': 'StartMVC API',
            'version': '2.3.7',
            'timestamp': int(time.time()),
            'status': 'running'
        }
    
    def user(self, *args):
        """
        获取用户信息
        """
        # 检查用户ID
        user_id = args[0] if args else None
        
        if not user_id:
            # 返回用户列表
            return {
                'users': [
                    {'id': 1, 'username': 'admin', 'email': 'admin@example.com', 'role': 'admin'},
                    {'id': 2, 'username': 'user1', 'email': 'user1@example.com', 'role': 'user'},
                    {'id': 3, 'username': 'user2', 'email': 'user2@example.com', 'role': 'user'}
                ]
            }
        else:
            # 返回指定用户信息
            try:
                user_id = int(user_id)
                if user_id == 1:
                    return {'id': 1, 'username': 'admin', 'email': 'admin@example.com', 'role': 'admin'}
                elif user_id == 2:
                    return {'id': 2, 'username': 'user1', 'email': 'user1@example.com', 'role': 'user'}
                elif user_id == 3:
                    return {'id': 3, 'username': 'user2', 'email': 'user2@example.com', 'role': 'user'}
                else:
                    # 用户不存在
                    cherrypy.response.status = 404
                    return {'error': 'User not found', 'code': 404}
            except ValueError:
                # 用户ID格式错误
                cherrypy.response.status = 400
                return {'error': 'Invalid user ID', 'code': 400}
    
    def stats(self, *args):
        """
        获取统计信息
        """
        # 返回统计信息
        return {
            'users': 1234,
            'visits': 5678,
            'articles': 90,
            'comments': 456,
            'system_load': 23,
            'memory_usage': 45,
            'disk_usage': 67,
            'uptime': 123456
        }