#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

# 自定义异常类
class StartMVCException(Exception):
    """StartMVC框架基础异常类"""
    pass

class ConfigException(StartMVCException):
    """配置相关异常"""
    pass

class DatabaseException(StartMVCException):
    """数据库相关异常"""
    pass

class RouteException(StartMVCException):
    """路由相关异常"""
    pass

class ViewException(StartMVCException):
    """视图相关异常"""
    pass

class ControllerException(StartMVCException):
    """控制器相关异常"""
    pass

class CacheException(StartMVCException):
    """缓存相关异常"""
    pass

class SessionException(StartMVCException):
    """会话相关异常"""
    pass

class ModelException(StartMVCException):
    """模型相关异常"""
    pass