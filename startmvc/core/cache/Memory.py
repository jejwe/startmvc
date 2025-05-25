#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
内存缓存驱动

提供基于内存的缓存功能
"""

import time
import threading
from typing import Any, Dict, Optional


class Memory:
    """内存缓存驱动"""

    # 缓存数据
    _cache = {}
    
    # 缓存锁
    _lock = threading.Lock()

    def __init__(self, config):
        """初始化内存缓存驱动

        Args:
            config (dict): 配置
        """
        self.config = config

    def get(self, key: str) -> Any:
        """获取缓存

        Args:
            key (str): 缓存键

        Returns:
            Any: 缓存值
        """
        # 如果缓存不存在，则返回None
        if key not in self._cache:
            return None
        
        # 获取缓存数据
        cache_data = self._cache[key]
        
        # 如果缓存已过期，则删除缓存并返回None
        if cache_data['expire'] > 0 and cache_data['expire'] < time.time():
            with self._lock:
                if key in self._cache:
                    del self._cache[key]
            return None
        
        # 返回缓存值
        return cache_data['value']

    def set(self, key: str, value: Any, ttl: int = 0) -> bool:
        """设置缓存

        Args:
            key (str): 缓存键
            value (Any): 缓存值
            ttl (int): 缓存有效期（秒）

        Returns:
            bool: 是否成功
        """
        # 计算过期时间戳
        expire_time = 0
        if ttl > 0:
            expire_time = time.time() + ttl
        
        # 设置缓存
        with self._lock:
            self._cache[key] = {
                'value': value,
                'expire': expire_time,
                'key': key  # 存储原始键，用于前缀匹配
            }
        
        return True

    def delete(self, key: str) -> bool:
        """删除缓存

        Args:
            key (str): 缓存键

        Returns:
            bool: 是否成功
        """
        # 如果缓存存在，则删除
        if key in self._cache:
            with self._lock:
                if key in self._cache:
                    del self._cache[key]
            return True
        
        return False

    def flush(self) -> bool:
        """清空缓存

        Returns:
            bool: 是否成功
        """
        with self._lock:
            self._cache.clear()
        return True

    def flush_by_prefix(self, prefix: str) -> bool:
        """清空指定前缀的缓存

        Args:
            prefix (str): 前缀

        Returns:
            bool: 是否成功
        """
        with self._lock:
            # 找出所有匹配的键
            keys_to_delete = [k for k, v in self._cache.items() if 'key' in v and v['key'].startswith(prefix)]
            
            # 删除匹配的键
            for key in keys_to_delete:
                del self._cache[key]
        
        return True

    def increment(self, key: str, step: int = 1) -> int:
        """递增缓存值

        Args:
            key (str): 缓存键
            step (int): 步长

        Returns:
            int: 新值
        """
        with self._lock:
            # 获取当前值
            cache_data = self._cache.get(key, {'value': 0, 'expire': 0, 'key': key})
            
            # 如果值不是数字，则设置为步长
            if not isinstance(cache_data['value'], (int, float)):
                value = step
            else:
                value = cache_data['value'] + step
            
            # 更新缓存
            self._cache[key] = {
                'value': value,
                'expire': cache_data['expire'],
                'key': key
            }
            
            return value

    def decrement(self, key: str, step: int = 1) -> int:
        """递减缓存值

        Args:
            key (str): 缓存键
            step (int): 步长

        Returns:
            int: 新值
        """
        with self._lock:
            # 获取当前值
            cache_data = self._cache.get(key, {'value': 0, 'expire': 0, 'key': key})
            
            # 如果值不是数字，则设置为-步长
            if not isinstance(cache_data['value'], (int, float)):
                value = -step
            else:
                value = cache_data['value'] - step
            
            # 更新缓存
            self._cache[key] = {
                'value': value,
                'expire': cache_data['expire'],
                'key': key
            }
            
            return value