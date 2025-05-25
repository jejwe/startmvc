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
import importlib
from typing import Any, List, Type
from startmvc.core.Exceptions import StartMVCException

class Loader:
    """加载器类"""
    
    @classmethod
    def make(cls, controller_class: Any, method_name: str, params: List[Any] = None) -> Any:
        """
        创建控制器实例并调用方法
        
        Args:
            controller_class: 控制器类
            method_name: 方法名
            params: 参数列表
        
        Returns:
            方法返回值
        """
        # 如果参数为None，初始化为空列表
        if params is None:
            params = []
        
        # 创建控制器实例
        if isinstance(controller_class, type):
            # 如果是类，直接实例化
            controller = controller_class()
        else:
            # 如果是模块，获取同名类并实例化
            class_name = controller_class.__name__.split('.')[-1]
            if hasattr(controller_class, class_name):
                controller = getattr(controller_class, class_name)()
            else:
                # 尝试查找控制器类
                for attr_name in dir(controller_class):
                    attr = getattr(controller_class, attr_name)
                    if isinstance(attr, type):
                        controller = attr()
                        break
                else:
                    raise StartMVCException(f"无法找到控制器类: {controller_class.__name__}")
        
        # 检查方法是否存在
        if not hasattr(controller, method_name):
            raise StartMVCException(f"方法不存在: {method_name}")
        
        # 获取方法
        method = getattr(controller, method_name)
        
        # 调用方法
        return method(*params)