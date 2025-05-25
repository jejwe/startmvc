#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件缓存驱动

提供基于文件的缓存功能
"""

import os
import time
import pickle
import hashlib
import glob
from typing import Any, Optional


class File:
    """文件缓存驱动"""

    def __init__(self, config):
        """初始化文件缓存驱动

        Args:
            config (dict): 配置
        """
        self.config = config
        self.cache_dir = config.get('path', os.path.join(os.getcwd(), 'runtime', 'cache'))
        
        # 创建缓存目录
        os.makedirs(self.cache_dir, exist_ok=True)

    def get(self, key: str) -> Any:
        """获取缓存

        Args:
            key (str): 缓存键

        Returns:
            Any: 缓存值
        """
        # 获取缓存文件路径
        cache_file = self._get_cache_file(key)
        
        # 如果缓存文件不存在，则返回None
        if not os.path.exists(cache_file):
            return None
        
        try:
            # 读取缓存文件
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # 如果缓存已过期，则删除缓存文件并返回None
            if cache_data['expire'] > 0 and cache_data['expire'] < time.time():
                os.remove(cache_file)
                return None
            
            # 返回缓存值
            return cache_data['value']
        except Exception:
            # 如果读取失败，则删除缓存文件并返回None
            if os.path.exists(cache_file):
                os.remove(cache_file)
            return None

    def set(self, key: str, value: Any, ttl: int = 0) -> bool:
        """设置缓存

        Args:
            key (str): 缓存键
            value (Any): 缓存值
            ttl (int): 缓存有效期（秒）

        Returns:
            bool: 是否成功
        """
        # 获取缓存文件路径
        cache_file = self._get_cache_file(key)
        
        # 计算过期时间戳
        expire_time = 0
        if ttl > 0:
            expire_time = time.time() + ttl
        
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

    def delete(self, key: str) -> bool:
        """删除缓存

        Args:
            key (str): 缓存键

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

    def flush(self) -> bool:
        """清空缓存

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

    def flush_by_prefix(self, prefix: str) -> bool:
        """清空指定前缀的缓存

        Args:
            prefix (str): 前缀

        Returns:
            bool: 是否成功
        """
        try:
            # 遍历缓存目录
            for file_path in glob.glob(os.path.join(self.cache_dir, '*.cache')):
                # 读取缓存文件
                try:
                    with open(file_path, 'rb') as f:
                        cache_data = pickle.load(f)
                    
                    # 如果缓存键以指定前缀开头，则删除
                    if 'key' in cache_data and cache_data['key'].startswith(prefix):
                        os.remove(file_path)
                except:
                    pass
            
            return True
        except Exception:
            return False

    def increment(self, key: str, step: int = 1) -> int:
        """递增缓存值

        Args:
            key (str): 缓存键
            step (int): 步长

        Returns:
            int: 新值
        """
        # 获取当前值
        value = self.get(key)
        
        # 如果值不存在或不是数字，则设置为步长
        if value is None or not isinstance(value, (int, float)):
            value = step
        else:
            value += step
        
        # 更新缓存
        self.set(key, value)
        
        return value

    def decrement(self, key: str, step: int = 1) -> int:
        """递减缓存值

        Args:
            key (str): 缓存键
            step (int): 步长

        Returns:
            int: 新值
        """
        # 获取当前值
        value = self.get(key)
        
        # 如果值不存在或不是数字，则设置为-步长
        if value is None or not isinstance(value, (int, float)):
            value = -step
        else:
            value -= step
        
        # 更新缓存
        self.set(key, value)
        
        return value

    def _get_cache_file(self, key: str) -> str:
        """获取缓存文件路径

        Args:
            key (str): 缓存键

        Returns:
            str: 缓存文件路径
        """
        # 对缓存键进行MD5哈希
        key_hash = hashlib.md5(key.encode('utf-8')).hexdigest()
        
        # 返回缓存文件路径
        return os.path.join(self.cache_dir, f"{key_hash}.cache")