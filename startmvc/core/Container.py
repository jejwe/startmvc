#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

import inspect
import threading
from functools import wraps

class Container:
    """
    容器类
    用于依赖注入
    """
    
    # 容器实例
    _instance = None
    
    # 容器锁
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        """
        获取容器实例（单例模式）

        Returns:
            Container: 容器实例
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
        
    # 保持向后兼容
    @classmethod
    def instance(cls):
        """
        获取容器实例（单例模式）- 保持向后兼容
        
        Returns:
            Container: 容器实例
        """
        return cls.get_instance()
    
    def __init__(self):
        """
        构造函数
        """
        # 绑定列表
        self.bindings = {}
        
        # 实例列表
        self.instances = {}
        
        # 别名列表
        self.aliases = {}
    
    def bind(self, abstract, concrete=None, shared=False):
        """
        绑定服务
        
        Args:
            abstract: 抽象名称
            concrete: 具体实现
            shared: 是否共享
            
        Returns:
            Container: 容器对象
        """
        # 如果未指定具体实现，则使用抽象名称
        if concrete is None:
            concrete = abstract
        
        # 绑定服务
        self.bindings[abstract] = {
            'concrete': concrete,
            'shared': shared
        }
        
        return self
    
    def singleton(self, abstract, concrete=None):
        """
        绑定单例服务
        
        Args:
            abstract: 抽象名称
            concrete: 具体实现
            
        Returns:
            Container: 容器对象
        """
        return self.bind(abstract, concrete, True)
    
    def instance(self, abstract, instance):
        """
        绑定实例
        
        Args:
            abstract: 抽象名称
            instance: 实例
            
        Returns:
            Container: 容器对象
        """
        # 绑定实例
        self.instances[abstract] = instance
        
        return self
    
    def alias(self, abstract, alias):
        """
        绑定别名
        
        Args:
            abstract: 抽象名称
            alias: 别名
            
        Returns:
            Container: 容器对象
        """
        # 绑定别名
        self.aliases[alias] = abstract
        
        return self
    
    def make(self, abstract, parameters=None):
        """
        解析服务
        
        Args:
            abstract: 抽象名称
            parameters: 参数
            
        Returns:
            object: 服务实例
        """
        # 如果是别名，则获取原始抽象名称
        abstract = self.get_alias(abstract)
        
        # 如果已经有实例，则直接返回
        if abstract in self.instances:
            return self.instances[abstract]
        
        # 如果未绑定，则尝试自动解析
        if abstract not in self.bindings:
            return self.build(abstract, parameters)
        
        # 获取绑定信息
        binding = self.bindings[abstract]
        
        # 构建实例
        instance = self.build(binding['concrete'], parameters)
        
        # 如果是共享的，则保存实例
        if binding['shared']:
            self.instances[abstract] = instance
        
        return instance
    
    def build(self, concrete, parameters=None):
        """
        构建服务实例
        
        Args:
            concrete: 具体实现
            parameters: 参数
            
        Returns:
            object: 服务实例
        """
        # 如果是字符串，则尝试解析类
        if isinstance(concrete, str):
            # 如果包含点号，则按模块路径解析
            if '.' in concrete:
                # 分割模块路径和类名
                module_path, class_name = concrete.rsplit('.', 1)
                
                # 导入模块
                module = __import__(module_path, fromlist=[class_name])
                
                # 获取类
                concrete = getattr(module, class_name)
            else:
                # 尝试从全局变量中获取
                concrete = globals().get(concrete)
        
        # 如果是可调用对象，则调用
        if callable(concrete):
            # 如果指定了参数，则使用指定的参数
            if parameters:
                return concrete(**parameters)
            
            # 获取构造函数参数
            signature = inspect.signature(concrete)
            
            # 解析参数
            args = {}
            for param_name, param in signature.parameters.items():
                # 如果参数有默认值或者是可变参数，则跳过
                if param.default != inspect.Parameter.empty or param.kind != inspect.Parameter.POSITIONAL_OR_KEYWORD:
                    continue
                
                # 尝试解析参数
                args[param_name] = self.make(param_name)
            
            # 创建实例
            return concrete(**args)
        
        # 返回具体实现
        return concrete
    
    def get_alias(self, abstract):
        """
        获取原始抽象名称
        
        Args:
            abstract: 抽象名称
            
        Returns:
            str: 原始抽象名称
        """
        # 如果是别名，则获取原始抽象名称
        if abstract in self.aliases:
            return self.aliases[abstract]
        
        return abstract
    
    def has(self, abstract):
        """
        检查服务是否已绑定
        
        Args:
            abstract: 抽象名称
            
        Returns:
            bool: 是否已绑定
        """
        # 如果是别名，则获取原始抽象名称
        abstract = self.get_alias(abstract)
        
        # 检查是否已绑定
        return abstract in self.bindings or abstract in self.instances
    
    def bound(self, abstract):
        """
        检查服务是否已绑定
        
        Args:
            abstract: 抽象名称
            
        Returns:
            bool: 是否已绑定
        """
        return self.has(abstract)
    
    def resolved(self, abstract):
        """
        检查服务是否已解析
        
        Args:
            abstract: 抽象名称
            
        Returns:
            bool: 是否已解析
        """
        # 如果是别名，则获取原始抽象名称
        abstract = self.get_alias(abstract)
        
        # 检查是否已解析
        return abstract in self.instances
    
    def flush(self):
        """
        清空容器
        
        Returns:
            Container: 容器对象
        """
        # 清空绑定列表
        self.bindings = {}
        
        # 清空实例列表
        self.instances = {}
        
        # 清空别名列表
        self.aliases = {}
        
        return self
    
    def __call__(self, abstract, parameters=None):
        """
        解析服务
        
        Args:
            abstract: 抽象名称
            parameters: 参数
            
        Returns:
            object: 服务实例
        """
        return self.make(abstract, parameters)


# 依赖注入装饰器
def inject(**dependencies):
    """
    依赖注入装饰器
    
    Args:
        **dependencies: 依赖
        
    Returns:
        function: 装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取容器实例
            container = Container.instance()
            
            # 解析依赖
            for name, abstract in dependencies.items():
                # 如果未指定参数，则使用名称作为抽象名称
                if abstract is None:
                    abstract = name
                
                # 如果参数未传入，则从容器中解析
                if name not in kwargs:
                    kwargs[name] = container.make(abstract)
            
            # 调用原函数
            return func(*args, **kwargs)
        return wrapper
    return decorator