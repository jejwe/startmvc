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
import traceback
import cherrypy
from typing import Dict, Any, List, Callable, Optional
from startmvc.core.Exceptions import StartMVCException

from startmvc.core.Request import Request
from startmvc.core.Middleware import Middleware
from startmvc.core.Exception import AppException
from startmvc.core.Loader import Loader

class App:
    """应用程序主类"""
    
    trace = {}  # 跟踪信息
    
    def __init__(self):
        """初始化应用"""
        # 注册默认中间件
        self.register_middleware()
        
        # 设置CherryPy配置
        self.setup_cherrypy()
    
    def setup_cherrypy(self):
        """设置CherryPy配置"""
        from startmvc.function import config
        
        # 全局配置
        cherrypy.config.update({
            'log.screen': config('debug', True),
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 12000,  # 使用指定的端口
            'engine.autoreload.on': config('debug', True),
            'tools.sessions.on': True,
            'tools.sessions.timeout': 60,
        })
        
        # 静态文件配置
        static_config = {
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static')
            }
        }
        
        # 注册主分发器
        cherrypy.tree.mount(self, '/', config=static_config)
    
    def run(self, module, controller, action, params):
        """运行应用
        
        Args:
            module: 模块名
            controller: 控制器名
            action: 方法名
            params: 参数列表
        
        Returns:
            响应结果
        """
        # 调用应用处理请求
        return self.start_app(module, controller, action, params)
    
    @cherrypy.expose
    def default(self, *args, **kwargs):
        """默认请求处理方法"""
        # 记录开始时间和内存
        begin_time = time.time()
        
        try:
            # 初始化异常处理
            from startmvc.core.Exception import AppException
            AppException.init()
            
            # 加载自定义函数
            self.load_function()
            
            # 创建请求对象
            request = Request()
            
            # 通过中间件管道处理请求
            response = Middleware.run(self, lambda: self.handle_request(args))
            
            # 记录结束时间
            end_time = time.time()
            
            # 计算运行时间
            App.trace = {
                'begin_time': begin_time,
                'end_time': end_time,
                'runtime': f"{((end_time - begin_time) * 1000):.2f}ms",
                'memory': 'N/A',  # Python中不直接支持内存使用量获取
                'files': [],  # Python中不直接跟踪加载的文件
                'uri': cherrypy.request.path_info,
                'request_method': cherrypy.request.method
            }
            
            # 处理响应内容
            if isinstance(response, str):
                return response
            elif isinstance(response, dict):
                cherrypy.response.headers['Content-Type'] = 'application/json'
                import json
                return json.dumps(response)
            else:
                return str(response)
            
        except Exception as e:
            # 处理异常
            return self.exception_handler(e)
    
    @classmethod
    def load_function(cls, dir_path=None):
        """加载自定义函数"""
        if dir_path is None:
            from boot import ROOT_PATH, DS
            dir_path = os.path.join(ROOT_PATH, 'function', '*.py')
        
        import glob
        files = glob.glob(dir_path)
        
        for file_path in files:
            if os.path.isfile(file_path):
                # 动态导入模块
                import importlib.util
                spec = importlib.util.spec_from_file_location(f"function_{os.path.basename(file_path)}", file_path)
                if spec:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
    
    @classmethod
    def start_app(cls, module, controller, action, argv):
        """配置控制器的路径"""
        # 定义常量
        cherrypy.request.module = module
        cherrypy.request.controller = controller
        cherrypy.request.action = action
        
        # 构建控制器类名 - 使用Python风格的类名，不添加Controller后缀
        from boot import APP_NAMESPACE
        # 控制器文件名使用小写
        controller_file = controller.lower()
        controller_class = f"{APP_NAMESPACE}.{module}.controller.{controller_file}"
        
        # 检查控制器是否存在
        try:
            # 动态导入控制器
            parts = controller_class.split('.')
            module_path = '.'.join(parts[:-1])
            class_name = parts[-1]
            
            # 导入模块
            module_obj = __import__(module_path, fromlist=[class_name])
            
            # 尝试直接从模块中获取控制器类
            try:
                # 首先尝试从模块中获取Index类
                controller_class_name = controller
                if not controller_class_name[0].isupper():
                    controller_class_name = controller_class_name[0].upper() + controller_class_name[1:]
                controller_obj = getattr(module_obj, controller_class_name)
            except AttributeError:
                # 如果找不到，尝试从模块中获取index模块
                controller_module = getattr(module_obj, controller)
                # 然后从index模块中获取Index类
                controller_class_name = controller[0].upper() + controller[1:]
                controller_obj = getattr(controller_module, controller_class_name)
            
            # 构建方法名 - 使用Python风格的方法名，不添加Action后缀
            action_method = action
            
            # 调用控制器方法
            return Loader.make(controller_obj, action_method, argv)
            
        except (ImportError, AttributeError) as e:
            raise StartMVCException(f"控制器不存在: {controller_class}，错误: {str(e)}")
    
    @classmethod
    def error_handler(cls, level, message, file, line):
        """自定义错误处理触发错误"""
        error_message = f"错误提示：{message}，文件：{file}，行号：{line}"
        raise StartMVCException(error_message, level)
    
    @classmethod
    def exception_handler(cls, exception):
        """异常错误处理"""
        from startmvc.function import config
        
        # 设置HTTP状态码
        code = getattr(exception, 'code', 500)
        if code != 404:
            code = 500
        
        cherrypy.response.status = code
        
        if config('debug', True):
            # 在调试模式下显示详细错误信息
            error_template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tpl', 'debug.html')
            if os.path.exists(error_template):
                with open(error_template, 'r') as f:
                    template = f.read()
                
                # 替换模板变量
                error_info = {
                    'message': str(exception),
                    'file': getattr(exception, 'file', 'Unknown'),
                    'line': getattr(exception, 'line', 'Unknown'),
                    'trace': traceback.format_exc()
                }
                
                for key, value in error_info.items():
                    template = template.replace(f'{{{key}}}', str(value))
                
                return template
            else:
                return f"<h1>Error {code}</h1><p>{str(exception)}</p><pre>{traceback.format_exc()}</pre>"
        else:
            # 在生产模式下只显示简单错误信息
            return f"<h1>Error {code}</h1><p>An error occurred. Please try again later.</p>"
    
    def register_middleware(self):
        """注册默认中间件"""
        from startmvc.function import config
        import re
        
        # 从配置文件加载中间件
        middleware_config = config('middleware', {})
        
        # 注册中间件别名
        aliases = middleware_config.get('aliases', {})
        for alias, class_name in aliases.items():
            Middleware.alias(alias, class_name)
        
        # 注册全局中间件
        global_middleware = middleware_config.get('global', [])
        for middleware_class in global_middleware:
            Middleware.register(middleware_class)
        
        # 注册路由中间件
        route_middleware = middleware_config.get('route', {})
        
        # 定义路由中间件处理函数
        def route_middleware_handler():
            # 获取当前路径
            path = cherrypy.request.path_info
            
            # 检查路径是否匹配路由中间件
            for pattern, middleware_list in route_middleware.items():
                # 将通配符转换为正则表达式
                regex_pattern = pattern.replace('*', '.*')
                
                # 检查路径是否匹配
                if re.match(regex_pattern, path):
                    # 注册匹配的中间件
                    for middleware_class in middleware_list:
                        Middleware.register(middleware_class)
        
        # 添加路由中间件处理函数到CherryPy请求钩子
        cherrypy.request.hooks.attach('before_handler', route_middleware_handler)
    
    def handle_request(self, args):
        """处理请求"""
        try:
            # 首先尝试使用路由器匹配路由
            from startmvc.core.Router import Router
            uri = cherrypy.request.path_info
            module, controller, action, params = Router.match(uri.strip('/'))
            
            # 如果路由匹配成功，使用匹配结果
            if module and controller and action:
                return self.start_app(module, controller, action, params)
            
            # 如果路由匹配失败，使用默认解析
            # 移除前后的斜杠
            uri = uri.strip('/')
            
            # 如果URI为空，使用默认路由
            if not uri:
                module = 'home'  # 默认模块
                controller = 'index'  # 默认控制器
                action = 'index'  # 默认方法
                params = []
            else:
                # 解析URI
                parts = uri.split('/')
                module = parts[0] if parts else 'home'
                controller = parts[1].lower() if len(parts) > 1 else 'index'
                action = parts[2] if len(parts) > 2 else 'index'
                params = parts[3:] if len(parts) > 3 else []
            
            # 校验模块是否存在
            from boot import APP_PATH
            if not os.path.isdir(os.path.join(APP_PATH, module)):
                # 模块不存在，使用默认模块
                params = [controller, action] + params
                module = 'home'
                controller = 'index'
                action = 'index'
            
            # 使用start_app方法
            return self.start_app(module, controller, action, params)
            
        except Exception as e:
            raise e
    
    @classmethod
    def show_trace(cls):
        """显示追踪信息"""
        # 在页面最后输出追踪信息
        from startmvc.function import config
        
        if config('trace', False):
            trace_template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tpl', 'trace.html')
            if os.path.exists(trace_template):
                with open(trace_template, 'r') as f:
                    template = f.read()
                
                # 替换模板变量
                for key, value in cls.trace.items():
                    template = template.replace(f'{{{key}}}', str(value))
                
                return f"\n<!-- Trace Info Start -->\n{template}\n<!-- Trace Info End -->\n"
        
        return ""