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
from typing import Dict, Any, List, Optional, Union

class Request:
    """请求类"""
    
    def __init__(self):
        """初始化请求"""
        # 解析请求
        self.parse_request()
    
    def parse_request(self) -> None:
        """解析请求"""
        # 获取请求URI
        uri = cherrypy.request.path_info
        
        # 使用路由器匹配路由
        from startmvc.core.Router import Router
        module, controller, action, params = Router.match(uri)
        
        # 如果路由匹配成功，设置请求参数
        if module and controller and action:
            cherrypy.request.module = module
            cherrypy.request.controller = controller
            cherrypy.request.action = action
            cherrypy.request.params = params
    
    @classmethod
    def get(cls, name: Optional[str] = None, default: Any = None) -> Any:
        """
        获取GET参数
        
        Args:
            name: 参数名，如果为None则返回所有参数
            default: 默认值
        
        Returns:
            参数值
        """
        # 获取所有GET参数
        params = {}
        try:
            # 检查query_string是否存在
            query_string = cherrypy.request.query_string
            for key, value in cherrypy.request.params.items():
                if key in query_string:
                    params[key] = value
        except AttributeError:
            # 如果query_string不存在，使用请求方法判断
            if cherrypy.request.method.upper() == 'GET':
                params = dict(cherrypy.request.params)
        
        # 如果没有指定参数名，返回所有参数
        if name is None:
            return params
        
        # 返回指定参数，如果不存在返回默认值
        return params.get(name, default)
    
    @classmethod
    def post(cls, name: Optional[str] = None, default: Any = None) -> Any:
        """
        获取POST参数
        
        Args:
            name: 参数名，如果为None则返回所有参数
            default: 默认值
        
        Returns:
            参数值
        """
        # 获取所有POST参数
        params = {}
        if cherrypy.request.method.upper() == 'POST':
            try:
                # 检查query_string是否存在
                query_string = cherrypy.request.query_string
                for key, value in cherrypy.request.params.items():
                    if key not in query_string:
                        params[key] = value
            except AttributeError:
                # 如果query_string不存在，假设所有参数都是POST参数
                params = dict(cherrypy.request.params)
        
        # 如果没有指定参数名，返回所有参数
        if name is None:
            return params
        
        # 返回指定参数，如果不存在返回默认值
        return params.get(name, default)
    
    @classmethod
    def input(cls, name: Optional[str] = None, default: Any = None) -> Any:
        """
        获取输入参数（GET或POST）
        
        Args:
            name: 参数名，如果为None则返回所有参数
            default: 默认值
        
        Returns:
            参数值
        """
        # 合并GET和POST参数
        params = {}
        params.update(cls.get())
        params.update(cls.post())
        
        # 如果没有指定参数名，返回所有参数
        if name is None:
            return params
        
        # 返回指定参数，如果不存在返回默认值
        return params.get(name, default)
    
    @classmethod
    def is_post(cls) -> bool:
        """
        判断是否为POST请求
        
        Returns:
            是否为POST请求
        """
        return cherrypy.request.method.upper() == 'POST'
    
    @classmethod
    def is_get(cls) -> bool:
        """
        判断是否为GET请求
        
        Returns:
            是否为GET请求
        """
        return cherrypy.request.method.upper() == 'GET'
    
    @classmethod
    def is_ajax(cls) -> bool:
        """
        判断是否为AJAX请求
        
        Returns:
            是否为AJAX请求
        """
        return cherrypy.request.headers.get('X-Requested-With', '').lower() == 'xmlhttprequest'
    
    @classmethod
    def get_ip(cls) -> str:
        """
        获取客户端的真实IP地址
        
        Returns:
            IP地址
        """
        # 优先检查HTTP_X_FORWARDED_FOR
        if 'X-Forwarded-For' in cherrypy.request.headers:
            ips = cherrypy.request.headers['X-Forwarded-For'].split(',')
            for ip in ips:
                ip = ip.strip()
                if ip and ip.lower() != 'unknown':
                    return ip
        
        # 如果没有通过X-Forwarded-For获取到IP，使用远程地址
        return cherrypy.request.remote.ip