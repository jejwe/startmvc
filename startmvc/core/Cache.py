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
import pickle
import time
import hashlib
import json
import threading
from functools import wraps

class Cache:
    """
    缓存类
    支持文件缓存和内存缓存
    """
    
    # 缓存实例
    _instance = None
    
    # 缓存锁
    _lock = threading.Lock()
    
    # 内存缓存
    _memory_cache = {}
    
    @classmethod
    def get_instance(cls):
        """
        获取缓存实例（单例模式）

        Returns:
            Cache: 缓存实例
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
        获取缓存实例（单例模式）- 保持向后兼容
        
        Returns:
            Cache: 缓存实例
        """
        return cls.get_instance()
    
    def __init__(self):
        """
        构造函数
        """
        # 缓存配置
        self.config = {}
        
        # 缓存目录
        self.cache_dir = os.path.join(os.getcwd(), 'runtime', 'cache')
        
        # 创建缓存目录
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def set_config(self, config):
        """
        设置缓存配置
        
        Args:
            config: 缓存配置
        """
        self.config = config
        
        # 如果配置了缓存目录，则使用配置的目录
        if 'path' in config:
            self.cache_dir = config['path']
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def get(self, key, default=None):
        """
        获取缓存
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            mixed: 缓存值
        """
        # 如果配置了使用内存缓存
        if self.config.get('type') == 'memory':
            return self._get_memory(key, default)
        
        # 默认使用文件缓存
        return self._get_file(key, default)
    
    def set(self, key, value, expire=0):
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒）
            
        Returns:
            bool: 是否成功
        """
        # 如果配置了使用内存缓存
        if self.config.get('type') == 'memory':
            return self._set_memory(key, value, expire)
        
        # 默认使用文件缓存
        return self._set_file(key, value, expire)
    
    def delete(self, key):
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否成功
        """
        # 如果配置了使用内存缓存
        if self.config.get('type') == 'memory':
            return self._delete_memory(key)
        
        # 默认使用文件缓存
        return self._delete_file(key)
    
    def clear(self):
        """
        清空缓存
        
        Returns:
            bool: 是否成功
        """
        # 如果配置了使用内存缓存
        if self.config.get('type') == 'memory':
            return self._clear_memory()
        
        # 默认使用文件缓存
        return self._clear_file()
    
    def _get_memory(self, key, default=None):
        """
        从内存获取缓存
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            mixed: 缓存值
        """
        # 如果缓存不存在，则返回默认值
        if key not in self._memory_cache:
            return default
        
        # 获取缓存数据
        cache_data = self._memory_cache[key]
        
        # 如果缓存已过期，则删除缓存并返回默认值
        if cache_data['expire'] > 0 and cache_data['expire'] < time.time():
            del self._memory_cache[key]
            return default
        
        # 返回缓存值
        return cache_data['value']
    
    def _set_memory(self, key, value, expire=0):
        """
        设置内存缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒）
            
        Returns:
            bool: 是否成功
        """
        # 计算过期时间戳
        expire_time = 0
        if expire > 0:
            expire_time = time.time() + expire
        
        # 设置缓存
        self._memory_cache[key] = {
            'value': value,
            'expire': expire_time
        }
        
        return True
    
    def _delete_memory(self, key):
        """
        删除内存缓存
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否成功
        """
        # 如果缓存存在，则删除
        if key in self._memory_cache:
            del self._memory_cache[key]
            return True
        
        return False
    
    def _clear_memory(self):
        """
        清空内存缓存
        
        Returns:
            bool: 是否成功
        """
        self._memory_cache.clear()
        return True
    
    def _get_file(self, key, default=None):
        """
        从文件获取缓存
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            mixed: 缓存值
        """
        # 获取缓存文件路径
        cache_file = self._get_cache_file(key)
        
        # 如果缓存文件不存在，则返回默认值
        if not os.path.exists(cache_file):
            return default
        
        try:
            # 读取缓存文件
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # 如果缓存已过期，则删除缓存文件并返回默认值
            if cache_data['expire'] > 0 and cache_data['expire'] < time.time():
                os.remove(cache_file)
                return default
            
            # 返回缓存值
            return cache_data['value']
        except Exception:
            # 如果读取失败，则删除缓存文件并返回默认值
            if os.path.exists(cache_file):
                os.remove(cache_file)
            return default
    
    def _set_file(self, key, value, expire=0):
        """
        设置文件缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒）
            
        Returns:
            bool: 是否成功
        """
        # 获取缓存文件路径
        cache_file = self._get_cache_file(key)
        
        # 计算过期时间戳
        expire_time = 0
        if expire > 0:
            expire_time = time.time() + expire
        
        # 缓存数据
        cache_data = {
            'value': value,
            'expire': expire_time
        }
        
        try:
            # 写入缓存文件
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            return True
        except Exception:
            return False
    
    def _delete_file(self, key):
        """
        删除文件缓存
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否成功
        """
        # 获取缓存文件路径
        cache_file = self._get_cache_file(key)
        
        # 如果缓存文件存在，则删除
        if os.path.exists(cache_file):
            os.remove(cache_file)
            return True
        
        return False
    
    def _clear_file(self):
        """
        清空文件缓存
        
        Returns:
            bool: 是否成功
        """
        try:
            # 遍历缓存目录
            for file_name in os.listdir(self.cache_dir):
                # 只删除缓存文件
                if file_name.endswith('.cache'):
                    os.remove(os.path.join(self.cache_dir, file_name))
            
            return True
        except Exception:
            return False
    
    def _get_cache_file(self, key):
        """
        获取缓存文件路径
        
        Args:
            key: 缓存键
            
        Returns:
            str: 缓存文件路径
        """
        # 对缓存键进行MD5哈希
        key_hash = hashlib.md5(str(key).encode('utf-8')).hexdigest()
        
        # 返回缓存文件路径
        return os.path.join(self.cache_dir, f"{key_hash}.cache")


def cached(expire=0):
    """
    缓存装饰器
    用于缓存函数返回值
    
    Args:
        expire: 过期时间（秒）
        
    Returns:
        function: 装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取缓存实例
            cache = Cache.instance()
            
            # 生成缓存键
            key = f"{func.__module__}.{func.__name__}:{json.dumps(args)}:{json.dumps(kwargs, sort_keys=True)}"
            
            # 尝试从缓存获取
            result = cache.get(key)
            
            # 如果缓存不存在，则调用函数并缓存结果
            if result is None:
                result = func(*args, **kwargs)
                cache.set(key, result, expire)
            
            return result
        return wrapper
    return decorator