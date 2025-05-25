#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

import time
import json
import cherrypy
import os
import logging
from datetime import datetime
from startmvc.core.Middleware import Middleware

class Log(Middleware):
    """
    日志中间件
    用于记录请求和响应信息
    """
    
    def __init__(self):
        """
        构造函数
        """
        super().__init__()
        self.start_time = None
        self.logger = self._setup_logger()
    
    def before(self, request):
        """
        请求前处理
        
        Args:
            request: 请求对象
            
        Returns:
            mixed: 如果返回Response对象，则中断请求，直接返回该Response
        """
        # 记录开始时间
        self.start_time = time.time()
        
        # 记录请求信息
        request_info = {
            'method': cherrypy.request.method,
            'uri': cherrypy.request.path_info,
            'ip': cherrypy.request.remote.ip,
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'user_agent': cherrypy.request.headers.get('User-Agent', 'Unknown'),
        }
        
        # 记录到日志文件
        self.logger.info(f"[REQUEST] {json.dumps(request_info, ensure_ascii=False)}")
        
        # 在调试模式下输出到页面
        if cherrypy.config.get('debug', False):
            print(f"<!-- 请求日志：{json.dumps(request_info, ensure_ascii=False)} -->")
        
        # 继续请求
        return None
    
    def after(self, request, response):
        """
        请求后处理
        
        Args:
            request: 请求对象
            response: 响应对象
            
        Returns:
            Response: 响应对象
        """
        # 计算请求耗时
        if self.start_time:
            end_time = time.time()
            execution_time = round((end_time - self.start_time) * 1000, 2)
            
            # 记录响应信息
            response_info = {
                'method': cherrypy.request.method,
                'uri': cherrypy.request.path_info,
                'status': response.status if hasattr(response, 'status') else '200 OK',
                'time': execution_time,
            }
            
            # 记录到日志文件
            self.logger.info(f"[RESPONSE] {json.dumps(response_info, ensure_ascii=False)}")
            
            # 在调试模式下输出到页面
            if cherrypy.config.get('debug', False):
                print(f"<!-- 请求执行时间：{execution_time}ms -->")
        
        return response
    
    def _setup_logger(self):
        """
        设置日志记录器
        
        Returns:
            Logger: 日志记录器
        """
        # 创建日志目录
        log_dir = os.path.join(os.getcwd(), 'runtime', 'log')
        os.makedirs(log_dir, exist_ok=True)
        
        # 获取当前日期
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 设置日志文件路径
        log_file = os.path.join(log_dir, f'app-{today}.log')
        
        # 创建日志记录器
        logger = logging.getLogger('startmvc')
        
        # 避免重复添加处理器
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            
            # 创建文件处理器
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            
            # 设置日志格式
            formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
            file_handler.setFormatter(formatter)
            
            # 添加处理器
            logger.addHandler(file_handler)
        
        return logger