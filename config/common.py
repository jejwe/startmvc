#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

# 公共配置
config = {
    # 调试模式
    'debug': True,
    
    # 默认时区
    'timezone': 'Asia/Shanghai',
    
    # 默认语言
    'locale': 'zh_cn',
    
    # URL后缀
    'url_suffix': '.html',
    
    # 是否启用URL重写
    'urlrewrite': True,
    
    # 是否启用性能追踪
    'trace': True,
    
    # 模板引擎配置
    'template': {
        'engine': 'jinja2',  # 可选: jinja2, simple
        'cache': False,
        'suffix': '.html',
        'path': 'view',
        'left_delimiter': '{',
        'right_delimiter': '}',
        'globals': {},
        'filters': {},
    },
    
    # 会话配置
    'session': {
        'enable': True,
        'auto_start': True,
        'name': 'STARTMVC_SESSION',
        'type': 'file',  # 可选: file, memory
        'path': 'runtime/session',
        'expire': 86400,  # 24小时
        'secure': False,
        'httponly': True,
        'samesite': 'Lax',
        'max_lifetime': 604800,  # 7天
    },
    
    # 缓存配置
    'cache': {
        'driver': 'file',  # 可选: file, memory, redis
        'prefix': 'cache_',
        'expire': 3600,  # 1小时
        'file': {
            'path': 'runtime/cache',
        },
        'redis': {
            'host': '127.0.0.1',
            'port': 6379,
            'password': '',
            'db': 0,
            'timeout': 3,
            'prefix': 'cache:',
        },
        'memory': {
            'max_items': 1000,
        },
    },
    
    # 日志配置
    'log': {
        'level': 'DEBUG',  # 可选: DEBUG, INFO, WARNING, ERROR, CRITICAL
        'path': 'runtime/log',
        'file': '{name}.log',
        'max_size': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5,
        'format': '%(asctime)s [%(levelname)s] %(message)s',
        'date_format': '%Y-%m-%d %H:%M:%S',
        'console': True,
        'rotate_type': 'size',  # size or time
        'when': 'D',  # D=天, H=小时, M=分钟
        'interval': 1,
        'encoding': 'utf-8'
    },
    
    # 错误处理
    'error': {
        'display': True,
        'log': True,
        'template': 'startmvc/core/tpl/debug.html',
        'trace_template': 'startmvc/core/tpl/trace.html',
    },
    
    # 安全配置
    'security': {
        'csrf_protection': True,
        'csrf_token_name': '_token',
        'csrf_header_name': 'X-CSRF-TOKEN',
        'csrf_cookie_name': 'XSRF-TOKEN',
        'csrf_expire': 7200,  # 2小时
        'encrypt_key': 'startmvc',
        'xss_clean': True,
        'allowed_html_tags': ['a', 'b', 'blockquote', 'br', 'code', 'dd', 'dl', 'dt', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'li', 'ol', 'p', 'pre', 'q', 's', 'small', 'span', 'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th', 'thead', 'tr', 'tt', 'u', 'ul'],
    },
    
    # 上传配置
    'upload': {
        'upload_dir': 'public/uploads',
        'allowed_types': ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'text/plain', 'application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed'],
        'allowed_exts': ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'zip', 'rar', '7z'],
        'max_size': 10 * 1024 * 1024,  # 10MB
        'rename': True,
        'hash_filename': False,
        'overwrite': False
    },
    
    # HTTP客户端配置
    'http': {
        'timeout': 30,
        'verify_ssl': True,
        'max_redirects': 5,
        'user_agent': 'StartMVC/1.0',
    },
    
    # 分页配置
    'pagination': {
        'page_param': 'page',
        'page_size_param': 'page_size',
        'page_size': 10,
        'num_links': 5,
        'show_first_last': True,
        'show_prev_next': True,
        'show_total': True,
        'show_page_size': True,
        'page_size_options': [10, 20, 50, 100],
    },
    
    # 中间件配置
    'middleware': {
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
        ],
        
        # 路由中间件组
        'groups': {
            'web': [
                'app.middleware.CsrfMiddleware',
                'app.middleware.AuthMiddleware',
            ],
            'api': [
                'app.middleware.CorsMiddleware',
                'app.middleware.ApiMiddleware',
            ],
        },
    },
}