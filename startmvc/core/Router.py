#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

import os
import re
import cherrypy
from typing import Dict, Any, List, Optional, Callable, Tuple

class Router:
    """路由类"""
    
    # 路由规则
    _routes = []
    
    # 路由装饰器
    @staticmethod
    def route(pattern, **kwargs):
        """
        路由装饰器
        
        用法:
        @Router.route('user/<id:int>')
        def user_profile(id):
            return f"User profile: {id}"
        
        Args:
            pattern: 路由模式
            **kwargs: 其他参数，如name, methods等
        """
        def decorator(func):
            # 添加路由规则
            Router._routes.append({
                'pattern': pattern,
                'target': func,
                **kwargs
            })
            return func
        return decorator
    
    @staticmethod
    def load_routes():
        """加载路由配置"""
        from startmvc.function import config
        from boot import CONFIG_PATH
        
        # 路由配置文件路径
        route_file = os.path.join(CONFIG_PATH, 'route.py')
        
        if os.path.isfile(route_file):
            # 动态导入路由配置
            import importlib.util
            spec = importlib.util.spec_from_file_location("route_config", route_file)
            if spec:
                route_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(route_module)
                
                # 获取路由配置
                if hasattr(route_module, 'config') and 'routes' in route_module.config:
                    Router._routes.extend(route_module.config['routes'])
    
    @staticmethod
    def match(uri: str) -> Tuple[Optional[str], Optional[str], Optional[str], List[str]]:
        """
        匹配路由
        
        Args:
            uri: 请求URI
        
        Returns:
            (模块, 控制器, 方法, 参数)
        """
        # 加载路由配置
        if not Router._routes:
            Router.load_routes()
        
        # 移除前后的斜杠
        uri = uri.strip('/')
        
        # 遍历路由规则
        for route in Router._routes:
            pattern = route.get('pattern', '')
            target = route.get('target', '')
            
            # 如果模式匹配
            try:
                match = re.match(f'^{pattern}$', uri)
                if match:
                    # 解析目标
                    parts = target.split('/')
                    
                    # 提取模块、控制器和方法
                    module = parts[0] if len(parts) > 0 else 'home'
                    controller = parts[1] if len(parts) > 1 else 'index'
                    action = parts[2] if len(parts) > 2 else 'index'
                    
                    # 提取参数
                    params = list(match.groups())
                    
                    return module, controller, action, params
            except re.error:
                # 忽略无效的正则表达式
                continue
        
        # 如果没有匹配的路由，使用默认解析
        return None, None, None, []