#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Redis缓存驱动

提供基于Redis的缓存功能
"""

import pickle
from typing import Any, Optional

try:
    import redis
except ImportError:
    redis = None


class Redis:
    """Redis缓存驱动"""

    def __init__(self, config):
        """初始化Redis缓存驱动

        Args:
            config (dict): 配置
        """
        self.config = config
        self.redis = None
        
        # 如果Redis模块不可用，则抛出异常
        if redis is None:
            raise ImportError("Redis模块不可用，请安装：pip install redis")
        
        # 连接Redis
        self._connect()

    def _connect(self):
        """连接Redis"""
        self.redis = redis.Redis(
            host=self.config.get('host', '127.0.0.1'),
            port=self.config.get('port', 6379),
            password=self.config.get('password', ''),
            db=self.config.get('db', 0),
            decode_responses=False
        )

    def get(self, key: str) -> Any:
        """获取缓存

        Args:
            key (str): 缓存键

        Returns:
            Any: 缓存值
        """
        try:
            # 获取缓存
            value = self.redis.get(key)
            
            # 如果缓存不存在，则返回None
            if value is None:
                return None
            
            # 反序列化缓存值
            return pickle.loads(value)
        except Exception:
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
        try:
            # 序列化缓存值
            value = pickle.dumps(value)
            
            # 设置缓存
            if ttl > 0:
                self.redis.setex(key, ttl, value)
            else:
                self.redis.set(key, value)
            
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
        try:
            # 删除缓存
            self.redis.delete(key)
            return True
        except Exception:
            return False

    def flush(self) -> bool:
        """清空缓存

        Returns:
            bool: 是否成功
        """
        try:
            # 清空当前数据库
            self.redis.flushdb()
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
            # 获取所有匹配的键
            keys = self.redis.keys(f"{prefix}*")
            
            # 如果有匹配的键，则删除
            if keys:
                self.redis.delete(*keys)
            
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
        try:
            # 如果键不存在，则先设置为0
            if not self.redis.exists(key):
                self.redis.set(key, pickle.dumps(0))
            
            # 获取当前值
            value = pickle.loads(self.redis.get(key))
            
            # 如果值不是数字，则设置为步长
            if not isinstance(value, (int, float)):
                value = step
            else:
                value += step
            
            # 更新缓存
            self.redis.set(key, pickle.dumps(value))
            
            return value
        except Exception:
            return 0

    def decrement(self, key: str, step: int = 1) -> int:
        """递减缓存值

        Args:
            key (str): 缓存键
            step (int): 步长

        Returns:
            int: 新值
        """
        try:
            # 如果键不存在，则先设置为0
            if not self.redis.exists(key):
                self.redis.set(key, pickle.dumps(0))
            
            # 获取当前值
            value = pickle.loads(self.redis.get(key))
            
            # 如果值不是数字，则设置为-步长
            if not isinstance(value, (int, float)):
                value = -step
            else:
                value -= step
            
            # 更新缓存
            self.redis.set(key, pickle.dumps(value))
            
            return value
        except Exception:
            return 0