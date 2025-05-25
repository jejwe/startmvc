#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

StartMVC是一个轻量级的Python MVC框架，基于CherryPy构建。

原作者: Shao Bing
Python移植: OpenHands
版权所有: Copyright (c) 2020-2025
许可证: Apache2开源协议，需保留开发者信息
项目主页: http://startmvc.com
"""

import os
import cherrypy
from typing import Dict, Any, List, Optional, Union
from startmvc.core.Exceptions import ControllerException

from startmvc.core.View import View
from startmvc.core.Model import Model

class Controller:
    """控制器基类"""
    
    # 视图变量
    _view_vars = {}
    
    # 视图对象
    _view = None
    
    def __init__(self):
        """初始化控制器"""
        # 初始化视图对象
        self._view = View()
    
    def assign(self, name: str, value: Any) -> None:
        """
        分配变量到视图
        
        Args:
            name: 变量名
            value: 变量值
        """
        self._view_vars[name] = value
    
    def render(self, template: Optional[str] = None) -> str:
        """
        渲染视图
        
        Args:
            template: 模板文件路径，如果为None则使用默认模板
        
        Returns:
            渲染后的视图内容
        """
        # 将所有变量传递给视图
        for name, value in self._view_vars.items():
            self._view.assign(name, value)
        
        # 如果没有指定模板，使用默认模板
        if template is None:
            # 获取当前模块、控制器和方法
            module = cherrypy.request.module
            controller = cherrypy.request.controller.lower()
            action = cherrypy.request.action
            
            # 构建默认模板路径
            from boot import APP_PATH
            template = os.path.join(APP_PATH, module, 'view', controller, f'{action}.html')
        
        # 渲染视图
        return self._view.render(template)
        
    # 为了向后兼容，保留display方法作为render的别名
    def display(self, template: Optional[str] = None) -> str:
        """
        渲染视图（render的别名，为了向后兼容）
        
        Args:
            template: 模板文件路径，如果为None则使用默认模板
        
        Returns:
            渲染后的视图内容
        """
        return self.render(template)
    
    def get_model(self, name: str, module: Optional[str] = None) -> Model:
        """
        加载模型
        
        Args:
            name: 模型名称
            module: 模块名称，如果为None则使用当前模块
        
        Returns:
            模型实例
        """
        # 如果没有指定模块，使用当前模块
        if module is None:
            module = cherrypy.request.module
        
        # 构建模型类名 - 使用Python风格的类名，不添加Model后缀
        from boot import APP_NAMESPACE
        model_class = f"{APP_NAMESPACE}.{module}.model.{name}"
        
        try:
            # 动态导入模型
            parts = model_class.split('.')
            module_path = '.'.join(parts[:-1])
            class_name = parts[-1]
            
            # 导入模块
            module_obj = __import__(module_path, fromlist=[class_name])
            
            # 获取模型类
            if hasattr(module_obj, class_name):
                model_class_obj = getattr(module_obj, class_name)
                # 创建模型实例
                return model_class_obj()
            else:
                # 尝试查找模型类（向后兼容）
                model_class_name = f"{name}Model"
                if hasattr(module_obj, model_class_name):
                    model_class_obj = getattr(module_obj, model_class_name)
                    return model_class_obj()
                
                # 尝试查找其他模型类
                for attr_name in dir(module_obj):
                    attr = getattr(module_obj, attr_name)
                    if isinstance(attr, type) and (attr_name == name or attr_name == model_class_name):
                        return attr()
                
                raise ControllerException(f"模型类不存在: {class_name}")
            
        except (ImportError, AttributeError) as e:
            raise ControllerException(f"模型不存在: {model_class}")
            
    # 为了向后兼容，保留model方法作为get_model的别名
    def model(self, name: str, module: Optional[str] = None) -> Model:
        """
        加载模型（get_model的别名，为了向后兼容）
        
        Args:
            name: 模型名称
            module: 模块名称，如果为None则使用当前模块
        
        Returns:
            模型实例
        """
        return self.get_model(name, module)
    
    def redirect(self, url: str, code: int = 302) -> None:
        """
        重定向到指定URL
        
        Args:
            url: 目标URL
            code: HTTP状态码
        """
        # 使用CherryPy的重定向
        raise cherrypy.HTTPRedirect(url, status=code)
    
    def json(self, data: Any) -> str:
        """
        返回JSON响应
        
        Args:
            data: 要转换为JSON的数据
        
        Returns:
            JSON字符串
        """
        # 设置响应头
        cherrypy.response.headers['Content-Type'] = 'application/json'
        
        # 转换为JSON
        import json
        return json.dumps(data)
    
    def input(self, name: Optional[str] = None, default: Any = None) -> Any:
        """
        获取输入参数
        
        Args:
            name: 参数名，如果为None则返回所有参数
            default: 默认值
        
        Returns:
            参数值
        """
        # 合并GET和POST参数
        params = {**cherrypy.request.params}
        
        # 如果没有指定参数名，返回所有参数
        if name is None:
            return params
        
        # 返回指定参数，如果不存在返回默认值
        return params.get(name, default)
    
    def is_post(self) -> bool:
        """
        判断是否为POST请求
        
        Returns:
            是否为POST请求
        """
        return cherrypy.request.method.upper() == 'POST'
    
    def is_get(self) -> bool:
        """
        判断是否为GET请求
        
        Returns:
            是否为GET请求
        """
        return cherrypy.request.method.upper() == 'GET'
    
    def is_ajax(self) -> bool:
        """
        判断是否为AJAX请求
        
        Returns:
            是否为AJAX请求
        """
        return cherrypy.request.headers.get('X-Requested-With', '').lower() == 'xmlhttprequest'