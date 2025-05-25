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
import sys
import importlib.util

class Autoload:
    @staticmethod
    def load(class_name):
        """
        加载类
        
        Args:
            class_name: 类名，包含命名空间
        
        Returns:
            加载的模块
        """
        # 将命名空间转换为文件路径
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                class_name.replace('.', os.path.sep).replace('\\', os.path.sep) + '.py')
        
        if os.path.isfile(file_path):
            # 动态导入模块
            spec = importlib.util.spec_from_file_location(class_name, file_path)
            if spec:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
        return None
    
    @staticmethod
    def register():
        """
        注册自动加载函数
        """
        # Python中不需要像PHP那样注册自动加载函数
        # 这里可以添加一些初始化代码
        pass