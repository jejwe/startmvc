#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

import threading
from collections import defaultdict
from functools import wraps

class Event:
    """
    事件类
    用于事件触发与监听
    """
    
    # 事件实例
    _instance = None
    
    # 事件锁
    _lock = threading.Lock()
    
    # 事件监听器
    _listeners = defaultdict(list)
    
    # 通配符监听器
    _wildcard_listeners = []
    
    @classmethod
    def get_instance(cls):
        """
        获取事件实例（单例模式）

        Returns:
            Event: 事件实例
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
        获取事件实例（单例模式）- 保持向后兼容
        
        Returns:
            Event: 事件实例
        """
        return cls.get_instance()
    
    def listen(self, event, callback, priority=0):
        """
        监听事件
        
        Args:
            event: 事件名称
            callback: 回调函数
            priority: 优先级
            
        Returns:
            bool: 是否成功
        """
        # 如果是通配符，则添加到通配符监听器
        if event == '*':
            self._wildcard_listeners.append({
                'callback': callback,
                'priority': priority
            })
            
            # 按优先级排序
            self._wildcard_listeners.sort(key=lambda x: x['priority'], reverse=True)
            
            return True
        
        # 添加到事件监听器
        self._listeners[event].append({
            'callback': callback,
            'priority': priority
        })
        
        # 按优先级排序
        self._listeners[event].sort(key=lambda x: x['priority'], reverse=True)
        
        return True
    
    def remove(self, event, callback=None):
        """
        移除事件监听器
        
        Args:
            event: 事件名称
            callback: 回调函数
            
        Returns:
            bool: 是否成功
        """
        # 如果是通配符
        if event == '*':
            # 如果未指定回调函数，则移除所有通配符监听器
            if callback is None:
                self._wildcard_listeners = []
                return True
            
            # 移除指定回调函数的通配符监听器
            self._wildcard_listeners = [
                listener for listener in self._wildcard_listeners
                if listener['callback'] != callback
            ]
            
            return True
        
        # 如果事件不存在，则返回失败
        if event not in self._listeners:
            return False
        
        # 如果未指定回调函数，则移除所有事件监听器
        if callback is None:
            del self._listeners[event]
            return True
        
        # 移除指定回调函数的事件监听器
        self._listeners[event] = [
            listener for listener in self._listeners[event]
            if listener['callback'] != callback
        ]
        
        # 如果事件监听器为空，则删除事件
        if not self._listeners[event]:
            del self._listeners[event]
        
        return True
    
    def has(self, event, callback=None):
        """
        检查事件监听器是否存在
        
        Args:
            event: 事件名称
            callback: 回调函数
            
        Returns:
            bool: 是否存在
        """
        # 如果是通配符
        if event == '*':
            # 如果未指定回调函数，则检查是否有通配符监听器
            if callback is None:
                return len(self._wildcard_listeners) > 0
            
            # 检查是否有指定回调函数的通配符监听器
            return any(
                listener['callback'] == callback
                for listener in self._wildcard_listeners
            )
        
        # 如果事件不存在，则返回失败
        if event not in self._listeners:
            return False
        
        # 如果未指定回调函数，则检查是否有事件监听器
        if callback is None:
            return len(self._listeners[event]) > 0
        
        # 检查是否有指定回调函数的事件监听器
        return any(
            listener['callback'] == callback
            for listener in self._listeners[event]
        )
    
    def trigger(self, event, *args, **kwargs):
        """
        触发事件
        
        Args:
            event: 事件名称
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            list: 事件结果列表
        """
        # 事件结果列表
        results = []
        
        # 触发事件监听器
        if event in self._listeners:
            for listener in self._listeners[event]:
                try:
                    # 调用回调函数
                    result = listener['callback'](*args, **kwargs)
                    
                    # 添加到结果列表
                    results.append(result)
                except Exception as e:
                    # 添加异常到结果列表
                    results.append(e)
        
        # 触发通配符监听器
        for listener in self._wildcard_listeners:
            try:
                # 调用回调函数
                result = listener['callback'](event, *args, **kwargs)
                
                # 添加到结果列表
                results.append(result)
            except Exception as e:
                # 添加异常到结果列表
                results.append(e)
        
        return results
    
    def once(self, event, callback, priority=0):
        """
        监听一次事件
        
        Args:
            event: 事件名称
            callback: 回调函数
            priority: 优先级
            
        Returns:
            bool: 是否成功
        """
        # 创建一次性回调函数
        @wraps(callback)
        def once_callback(*args, **kwargs):
            # 移除事件监听器
            self.remove(event, once_callback)
            
            # 调用原始回调函数
            return callback(*args, **kwargs)
        
        # 监听事件
        return self.listen(event, once_callback, priority)
    
    def clear(self):
        """
        清空所有事件监听器
        
        Returns:
            bool: 是否成功
        """
        # 清空事件监听器
        self._listeners.clear()
        
        # 清空通配符监听器
        self._wildcard_listeners = []
        
        return True


# 事件装饰器
def on(event, priority=0):
    """
    事件监听装饰器
    
    Args:
        event: 事件名称
        priority: 优先级
        
    Returns:
        function: 装饰器函数
    """
    def decorator(func):
        # 获取事件实例
        event_instance = Event.instance()
        
        # 监听事件
        event_instance.listen(event, func, priority)
        
        return func
    return decorator


# 一次性事件装饰器
def once(event, priority=0):
    """
    一次性事件监听装饰器
    
    Args:
        event: 事件名称
        priority: 优先级
        
    Returns:
        function: 装饰器函数
    """
    def decorator(func):
        # 获取事件实例
        event_instance = Event.instance()
        
        # 监听一次事件
        event_instance.once(event, func, priority)
        
        return func
    return decorator