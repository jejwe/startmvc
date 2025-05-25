#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

# 缓存配置
config = {
    # 默认缓存驱动
    'default': 'file',
    
    # 缓存驱动
    'drivers': {
        # 文件缓存
        'file': {
            'type': 'file',
            'path': 'runtime/cache',
            'expire': 3600,  # 1小时
        },
        
        # 内存缓存
        'memory': {
            'type': 'memory',
            'expire': 3600,  # 1小时
        },
        
        # Redis缓存
        'redis': {
            'type': 'redis',
            'host': '127.0.0.1',
            'port': 6379,
            'password': '',
            'database': 0,
            'prefix': 'startmvc:',
            'expire': 3600,  # 1小时
        },
        
        # Memcached缓存
        'memcached': {
            'type': 'memcached',
            'host': '127.0.0.1',
            'port': 11211,
            'prefix': 'startmvc:',
            'expire': 3600,  # 1小时
        },
    },
}