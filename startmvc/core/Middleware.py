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
import cherrypy
from typing import Dict, Any, List, Optional, Callable, Union

class Middleware:
    """中间件管理类"""
    
    # 全局中间件
    _global = []
    
    # 中间件别名
    _aliases = {}
    
    @staticmethod
    def register(middleware_class: str) -> None:
        """
        注册全局中间件
        
        Args:
            middleware_class: 中间件类名
        """
        # 解析中间件类名
        if middleware_class in Middleware._aliases:
            middleware_class = Middleware._aliases[middleware_class]
        
        # 添加到全局中间件列表
        if middleware_class not in Middleware._global:
            Middleware._global.append(middleware_class)
    
    @staticmethod
    def alias(name: str, class_name: str) -> None:
        """
        注册中间件别名
        
        Args:
            name: 别名
            class_name: 中间件类名
        """
        Middleware._aliases[name] = class_name
    
    @staticmethod
    def run(app, callback: Callable) -> Any:
        """
        运行中间件管道
        
        Args:
            app: 应用实例
            callback: 回调函数
        
        Returns:
            响应结果
        """
        # 创建请求对象
        request = cherrypy.request
        
        # 构建中间件管道
        pipeline = Middleware._build_pipeline(app, callback)
        
        # 执行中间件管道
        return pipeline(request)
    
    @staticmethod
    def _build_pipeline(app, callback: Callable) -> Callable:
        """
        构建中间件管道
        
        Args:
            app: 应用实例
            callback: 回调函数
        
        Returns:
            中间件管道
        """
        # 最后一个中间件是回调函数
        pipeline = lambda request: callback()
        
        # 从后往前构建中间件管道
        for middleware_class in reversed(Middleware._global):
            # 动态导入中间件类
            try:
                parts = middleware_class.split('.')
                module_path = '.'.join(parts[:-1])
                class_name = parts[-1]
                
                # 导入模块
                module = __import__(module_path, fromlist=[class_name])
                middleware_class = getattr(module, class_name)
                
                # 创建中间件实例
                middleware = middleware_class()
                
                # 检查中间件类型
                if hasattr(middleware, 'handle'):
                    # 旧版中间件，使用handle方法
                    current_pipeline = pipeline
                    pipeline = lambda request, middleware=middleware, next_pipeline=current_pipeline: middleware.handle(request, lambda: next_pipeline(request))
                else:
                    # 新版中间件，使用before/after方法
                    current_pipeline = pipeline
                    def middleware_wrapper(request, middleware=middleware, next_pipeline=current_pipeline):
                        # 执行before方法
                        if hasattr(middleware, 'before'):
                            result = middleware.before(request)
                            if result is not None:
                                # 如果before方法返回了结果，则中断管道
                                return result
                        
                        # 执行下一个中间件
                        response = next_pipeline(request)
                        
                        # 执行after方法
                        if hasattr(middleware, 'after'):
                            response = middleware.after(request, response)
                        
                        return response
                    
                    pipeline = middleware_wrapper
                
            except (ImportError, AttributeError) as e:
                # 如果中间件类不存在，跳过
                continue
        
        return pipeline


class MiddlewareBase:
    """中间件基类（旧版兼容）"""
    
    def handle(self, request, next_callback: Callable) -> Any:
        """
        处理请求
        
        Args:
            request: 请求对象
            next_callback: 下一个中间件
        
        Returns:
            响应结果
        """
        # 默认实现直接调用下一个中间件
        return next_callback()


class Middleware(Middleware):
    """中间件基类（新版）"""
    
    def before(self, request) -> Optional[Any]:
        """
        请求前处理
        
        Args:
            request: 请求对象
            
        Returns:
            mixed: 如果返回值不为None，则中断管道并返回该值
        """
        return None
    
    def after(self, request, response) -> Any:
        """
        请求后处理
        
        Args:
            request: 请求对象
            response: 响应对象
            
        Returns:
            响应对象
        """
        return response
    
    def redirect(self, url: str, status: int = 302) -> str:
        """
        重定向
        
        Args:
            url: 重定向URL
            status: HTTP状态码
            
        Returns:
            str: 重定向HTML
        """
        cherrypy.response.status = status
        cherrypy.response.headers['Location'] = url
        return ""