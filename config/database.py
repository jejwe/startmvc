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

# 数据库配置
config = {
    # 默认数据库连接
    'default': {
        'type': 'sqlite',  # 数据库类型: mysql, sqlite, postgresql
        'database': os.path.join(os.getcwd(), 'runtime', 'db', 'startmvc.db'),  # SQLite数据库文件路径
        'prefix': 'sm_',  # 表前缀
        'debug': True,  # 是否开启调试模式
        'cache': {
            'enabled': True,  # 是否启用查询缓存
            'ttl': 3600,  # 缓存有效期（秒）
        },
    },
    
    # MySQL数据库连接示例
    'mysql': {
        'type': 'mysql',
        'hostname': 'localhost',
        'hostport': 3306,
        'database': 'startmvc',
        'username': 'root',
        'password': 'root',
        'charset': 'utf8mb4',
        'prefix': 'sm_',
        'debug': True,
        'options': {
            'connect_timeout': 10,
            'autocommit': True,
        },
        'pool': {
            'min_connections': 1,
            'max_connections': 10,
            'max_idle_time': 60,
        },
        'cache': {
            'enabled': True,
            'ttl': 3600,
        },
    },
    
    # PostgreSQL数据库连接示例
    'postgresql': {
        'type': 'postgresql',
        'hostname': 'localhost',
        'hostport': 5432,
        'database': 'startmvc',
        'username': 'postgres',
        'password': 'postgres',
        'prefix': 'sm_',
        'schema': 'public',
        'debug': True,
        'options': {
            'connect_timeout': 10,
        },
        'pool': {
            'min_connections': 1,
            'max_connections': 10,
            'max_idle_time': 60,
        },
        'cache': {
            'enabled': True,
            'ttl': 3600,
        },
    },
}