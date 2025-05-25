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

class User(Controller):
    """用户API控制器"""
    
    def index(self, *args):
        """
        获取用户列表
        """
        # 返回用户列表
        return {
            'users': [
                {'id': 1, 'username': 'admin', 'email': 'admin@example.com', 'role': 'admin'},
                {'id': 2, 'username': 'user1', 'email': 'user1@example.com', 'role': 'user'},
                {'id': 3, 'username': 'user2', 'email': 'user2@example.com', 'role': 'user'}
            ]
        }
    
    def get(self, *args):
        """
        获取用户信息
        """
        # 检查用户ID
        user_id = args[0] if args else None
        
        if not user_id:
            # 用户ID不能为空
            cherrypy.response.status = 400
            return {'error': 'User ID is required', 'code': 400}
        
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
    
    def create(self, *args):
        """
        创建用户
        """
        # 获取请求体
        try:
            # 获取JSON数据
            if hasattr(cherrypy.request, 'json_data'):
                data = cherrypy.request.json_data
            else:
                # 尝试从请求体读取JSON
                body = cherrypy.request.body.read().decode('utf-8')
                data = json.loads(body) if body else {}
            
            # 验证必填字段
            required_fields = ['username', 'email', 'password']
            for field in required_fields:
                if field not in data:
                    cherrypy.response.status = 400
                    return {'error': f'Missing required field: {field}', 'code': 400}
            
            # 模拟创建用户
            new_user = {
                'id': 4,  # 模拟自增ID
                'username': data['username'],
                'email': data['email'],
                'role': data.get('role', 'user'),
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 返回创建的用户
            return {
                'message': 'User created successfully',
                'user': new_user
            }
            
        except json.JSONDecodeError:
            # JSON解析错误
            cherrypy.response.status = 400
            return {'error': 'Invalid JSON data', 'code': 400}
        except Exception as e:
            # 其他错误
            cherrypy.response.status = 500
            return {'error': str(e), 'code': 500}
    
    def update(self, *args):
        """
        更新用户
        """
        # 检查用户ID
        user_id = args[0] if args else None
        
        if not user_id:
            # 用户ID不能为空
            cherrypy.response.status = 400
            return {'error': 'User ID is required', 'code': 400}
        
        try:
            # 获取JSON数据
            if hasattr(cherrypy.request, 'json_data'):
                data = cherrypy.request.json_data
            else:
                # 尝试从请求体读取JSON
                body = cherrypy.request.body.read().decode('utf-8')
                data = json.loads(body) if body else {}
            
            # 验证用户ID
            user_id = int(user_id)
            if user_id not in [1, 2, 3]:
                # 用户不存在
                cherrypy.response.status = 404
                return {'error': 'User not found', 'code': 404}
            
            # 模拟更新用户
            updated_user = {
                'id': user_id,
                'username': data.get('username', f'user{user_id}'),
                'email': data.get('email', f'user{user_id}@example.com'),
                'role': data.get('role', 'user' if user_id != 1 else 'admin'),
                'updated_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 返回更新的用户
            return {
                'message': 'User updated successfully',
                'user': updated_user
            }
            
        except json.JSONDecodeError:
            # JSON解析错误
            cherrypy.response.status = 400
            return {'error': 'Invalid JSON data', 'code': 400}
        except ValueError:
            # 用户ID格式错误
            cherrypy.response.status = 400
            return {'error': 'Invalid user ID', 'code': 400}
        except Exception as e:
            # 其他错误
            cherrypy.response.status = 500
            return {'error': str(e), 'code': 500}
    
    def delete(self, *args):
        """
        删除用户
        """
        # 检查用户ID
        user_id = args[0] if args else None
        
        if not user_id:
            # 用户ID不能为空
            cherrypy.response.status = 400
            return {'error': 'User ID is required', 'code': 400}
        
        try:
            # 验证用户ID
            user_id = int(user_id)
            if user_id not in [1, 2, 3]:
                # 用户不存在
                cherrypy.response.status = 404
                return {'error': 'User not found', 'code': 404}
            
            # 模拟删除用户
            return {
                'message': 'User deleted successfully',
                'id': user_id
            }
            
        except ValueError:
            # 用户ID格式错误
            cherrypy.response.status = 400
            return {'error': 'Invalid user ID', 'code': 400}
        except Exception as e:
            # 其他错误
            cherrypy.response.status = 500
            return {'error': str(e), 'code': 500}