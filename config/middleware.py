#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

# 中间件配置
config = {
    # 中间件别名
    'aliases': {
        'auth': 'app.middleware.AuthMiddleware',
        'log': 'app.middleware.LogMiddleware',
        'api': 'app.middleware.ApiMiddleware',
        'cors': 'app.middleware.CorsMiddleware',
        'csrf': 'app.middleware.CsrfMiddleware',
    },
    
    # 全局中间件
    'global': [
        'app.middleware.LogMiddleware',
        'app.middleware.CsrfMiddleware',
    ],
    
    # 路由中间件
    'route': {
        '/api/*': [
            'app.middleware.ApiMiddleware',
            'app.middleware.CorsMiddleware',
        ],
        '/admin/*': [
            'app.middleware.AuthMiddleware',
        ],
        '/user/*': [
            'app.middleware.AuthMiddleware',
        ],
        '/login': [
            'app.middleware.CsrfMiddleware',
        ],
    },
    
    # 中间件组
    'groups': {
        'web': [
            'app.middleware.CsrfMiddleware',
            'app.middleware.AuthMiddleware',
        ],
        'api': [
            'app.middleware.ApiMiddleware',
            'app.middleware.CorsMiddleware',
        ],
        'admin': [
            'app.middleware.AuthMiddleware',
            'app.middleware.CsrfMiddleware',
        ],
    },
}