#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

# 路由配置
config = {
    # 路由规则
    'routes': [
        # 首页路由
        {
            'pattern': '',
            'target': 'home/index/index',
        },
        
        # 登录路由
        {
            'pattern': 'login',
            'target': 'home/login/index',
        },
        {
            'pattern': 'login/login',
            'target': 'home/login/login',
        },
        {
            'pattern': 'login/logout',
            'target': 'home/login/logout',
        },
        
        # 静态页面路由
        {
            'pattern': 'page/([a-zA-Z0-9_-]+)',
            'target': 'home/page/show',
        },
        
        # 文章路由
        {
            'pattern': 'article/([0-9]+)',
            'target': 'home/article/show',
        },
        
        # 分类路由
        {
            'pattern': 'category/([a-zA-Z0-9_-]+)',
            'target': 'home/category/show',
        },
        
        # 标签路由
        {
            'pattern': 'tag/([a-zA-Z0-9_-]+)',
            'target': 'home/tag/show',
        },
        
        # 搜索路由
        {
            'pattern': 'search',
            'target': 'home/search/index',
        },
        
        # 用户路由
        {
            'pattern': 'user/([a-zA-Z0-9_-]+)',
            'target': 'home/user/profile',
            'middleware': ['auth'],  # 应用中间件
        },
        
        # 管理员路由
        {
            'pattern': 'admin',
            'target': 'admin/index/index',
            'middleware': ['auth'],  # 应用中间件
        },
        {
            'pattern': 'admin/index/dashboard',
            'target': 'admin/index/dashboard',
            'middleware': ['auth'],  # 应用中间件
        },
        {
            'pattern': 'admin/index/profile',
            'target': 'admin/index/profile',
            'middleware': ['auth'],  # 应用中间件
        },
        
        # 测试路由
        {
            'pattern': 'test',
            'target': 'home/test/index',
        },
        
        # 数据库示例路由
        {
            'pattern': 'database',
            'target': 'home/database/index',
        },
        {
            'pattern': 'database/query',
            'target': 'home/database/query',
        },
        {
            'pattern': 'database/find',
            'target': 'home/database/find',
        },
        {
            'pattern': 'database/insert',
            'target': 'home/database/insert',
        },
        {
            'pattern': 'database/update',
            'target': 'home/database/update',
        },
        {
            'pattern': 'database/delete',
            'target': 'home/database/delete',
        },
        {
            'pattern': 'database/transaction',
            'target': 'home/database/transaction',
        },
        
        # 分页示例路由
        {
            'pattern': 'pagination',
            'target': 'home/pagination/index',
        },
        {
            'pattern': 'pagination/custom',
            'target': 'home/pagination/custom',
        },
        {
            'pattern': 'pagination/simple',
            'target': 'home/pagination/simple',
        },
        
        # 事件示例路由
        {
            'pattern': 'event',
            'target': 'home/event/index',
        },
        {
            'pattern': 'event/trigger_event',
            'target': 'home/event/trigger_event',
        },
        {
            'pattern': 'event/remove_listener',
            'target': 'home/event/remove_listener',
        },
        
        # 带参数的路由
        {
            'pattern': 'user/:id',
            'target': 'home/user/view',
            'params': {
                'id': r'\d+',  # 只匹配数字
            },
        },
    ],
    
    # 路由分组
    'groups': [
        {
            'prefix': 'api',
            'middleware': ['app.middleware.ApiMiddleware', 'app.middleware.CorsMiddleware'],
            'routes': [
                # API首页
                {
                    'pattern': '',
                    'target': 'api/index/index',
                },
                # 用户API
                {
                    'pattern': 'user',
                    'target': 'api/user/index',
                },
                {
                    'pattern': 'user/:id',
                    'target': 'api/user/get',
                    'params': {
                        'id': '\\d+',  # 只匹配数字
                    },
                },
                {
                    'pattern': 'user/create',
                    'target': 'api/user/create',
                },
                {
                    'pattern': 'user/:id/update',
                    'target': 'api/user/update',
                    'params': {
                        'id': '\\d+',  # 只匹配数字
                    },
                },
                {
                    'pattern': 'user/:id/delete',
                    'target': 'api/user/delete',
                    'params': {
                        'id': '\\d+',  # 只匹配数字
                    },
                },
                # 统计API
                {
                    'pattern': 'stats',
                    'target': 'api/index/stats',
                },
            ],
        },
    ],
}