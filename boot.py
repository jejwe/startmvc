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
import sys
import time
import cherrypy
import importlib
from datetime import datetime

# 定义环境变量
ENV = os.environ.get('ENV', 'development')  # 可以是 development 或 production
DS = os.path.sep

# 定义路径常量
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
APP_NAMESPACE = 'app'
APP_PATH = os.path.join(ROOT_PATH, 'app', '')
BASE_PATH = os.path.dirname(os.path.abspath(__file__)) + DS
CORE_PATH = os.path.join(ROOT_PATH, 'startmvc', '')
CACHE_PATH = os.path.join(ROOT_PATH, 'runtime', 'cache', '')
TEMP_PATH = os.path.join(ROOT_PATH, 'runtime', 'temp', '')
CONFIG_PATH = os.path.join(ROOT_PATH, 'config', '')
_STATIC_ = '/static/'

# 版本信息
SM_VERSION = '2.3.7'
SM_UPDATE = '20250525'

# 性能监控
START_MEMORY = 0  # Python中不直接支持内存使用量获取，可以使用第三方库如psutil
START_TIME = time.time()

# 添加项目路径到系统路径
sys.path.append(ROOT_PATH)

# 加载函数库
from startmvc.function import *

# 导入自动加载模块
from startmvc.autoload import Autoload
Autoload.register()

# 导入框架核心类
from startmvc.core.App import App
from startmvc.core.Exceptions import StartMVCException as SMException
from startmvc.core.Router import Router
from startmvc.core.Request import Request

# 初始化异常处理已在Exceptions.py中完成

# 创建应用实例
app = App()

class StartMVC(object):
    """StartMVC应用入口类"""
    
    @cherrypy.expose
    def default(self, *args, **kwargs):
        """默认处理方法"""
        # 初始化请求
        request = Request()
        
        # 获取路由参数
        module = cherrypy.request.module if hasattr(cherrypy.request, 'module') else 'home'
        controller = cherrypy.request.controller if hasattr(cherrypy.request, 'controller') else 'Index'
        action = cherrypy.request.action if hasattr(cherrypy.request, 'action') else 'index'
        params = cherrypy.request.params if hasattr(cherrypy.request, 'params') else []
        
        # 调用应用处理请求
        return app.run(module, controller, action, params)

def main():
    """主函数"""
    # 创建必要的目录
    os.makedirs(os.path.join(ROOT_PATH, 'runtime', 'cache'), exist_ok=True)
    os.makedirs(os.path.join(ROOT_PATH, 'runtime', 'log'), exist_ok=True)
    os.makedirs(os.path.join(ROOT_PATH, 'runtime', 'db'), exist_ok=True)
    os.makedirs(os.path.join(ROOT_PATH, 'runtime', 'sessions'), exist_ok=True)
    
    # 加载配置
    common_config = config('common', {})
    
    # 配置CherryPy
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 12000,  # 使用分配的端口
        'engine.autoreload.on': common_config.get('debug', True),
        'log.screen': common_config.get('debug', True),
        'tools.sessions.on': True,
        'tools.sessions.storage_type': 'file',
        'tools.sessions.storage_path': os.path.join(ROOT_PATH, 'runtime', 'sessions'),
        'tools.sessions.timeout': 60,
        'tools.staticdir.root': ROOT_PATH,
    })
    
    # 静态文件配置
    static_config = {
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'static',
        }
    }
    
    # 启动应用
    cherrypy.quickstart(StartMVC(), '/', config=static_config)

if __name__ == '__main__':
    main()