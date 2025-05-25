#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库缓存类

提供数据库查询结果缓存功能
"""

import os
import time
import pickle
import hashlib
import threading
from startmvc.core.Cache import Cache


class DbCache:
    """数据库缓存类"""

    def __init__(self, cache_dir=None, ttl=3600):
        """初始化数据库缓存

        Args:
            cache_dir (str): 缓存目录
            ttl (int): 缓存有效期（秒）
        """
        self.cache = Cache()
        self.ttl = ttl
        self.enabled = True
        self.prefix = 'db_cache_'
        self._lock = threading.Lock()

    def get(self, sql, params=None):
        """获取缓存

        Args:
            sql (str): SQL语句
            params (list): 参数

        Returns:
            mixed: 缓存数据或None
        """
        if not self.enabled:
            return None
        
        key = self._generate_key(sql, params)
        return self.cache.get(key)

    def set(self, sql, params, data, ttl=None):
        """设置缓存

        Args:
            sql (str): SQL语句
            params (list): 参数
            data (mixed): 缓存数据
            ttl (int): 缓存有效期（秒）

        Returns:
            bool: 是否成功
        """
        if not self.enabled:
            return False
        
        key = self._generate_key(sql, params)
        return self.cache.set(key, data, ttl or self.ttl)

    def delete(self, sql, params=None):
        """删除缓存

        Args:
            sql (str): SQL语句
            params (list): 参数

        Returns:
            bool: 是否成功
        """
        key = self._generate_key(sql, params)
        return self.cache.delete(key)

    def flush(self):
        """清空缓存

        Returns:
            bool: 是否成功
        """
        return self.cache.flush_by_prefix(self.prefix)

    def enable(self):
        """启用缓存"""
        self.enabled = True

    def disable(self):
        """禁用缓存"""
        self.enabled = False

    def _generate_key(self, sql, params=None):
        """生成缓存键

        Args:
            sql (str): SQL语句
            params (list): 参数

        Returns:
            str: 缓存键
        """
        if params:
            key_data = sql + str(params)
        else:
            key_data = sql
        
        hash_obj = hashlib.md5(key_data.encode())
        return self.prefix + hash_obj.hexdigest()