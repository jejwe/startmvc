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
import traceback
from typing import Optional

class AppException(Exception):
    """应用异常类"""
    
    # 错误级别
    LEVEL_INFO = 'info'
    LEVEL_WARNING = 'warning'
    LEVEL_ERROR = 'error'
    
    # 错误代码
    code = 500
    
    # 错误文件
    file = None
    
    # 错误行号
    line = None
    
    def __init__(self, message: str, level: str = 'error', code: int = 500):
        """
        初始化异常
        
        Args:
            message: 错误信息
            level: 错误级别
            code: 错误代码
        """
        super().__init__(message)
        
        # 设置错误级别和代码
        self.level = level
        self.code = code
        
        # 获取错误文件和行号
        tb = traceback.extract_tb(sys.exc_info()[2])
        if tb:
            self.file = tb[-1].filename
            self.line = tb[-1].lineno
    
    @classmethod
    def init(cls):
        """初始化异常处理"""
        # 设置Python异常处理器
        sys.excepthook = cls.handle_exception
    
    @classmethod
    def handle_exception(cls, exc_type, exc_value, exc_traceback):
        """
        处理未捕获的异常
        
        Args:
            exc_type: 异常类型
            exc_value: 异常值
            exc_traceback: 异常追踪信息
        """
        # 如果是系统退出异常，直接退出
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # 获取错误信息
        error_message = str(exc_value)
        
        # 获取错误文件和行号
        tb = traceback.extract_tb(exc_traceback)
        file = tb[-1].filename if tb else 'Unknown'
        line = tb[-1].lineno if tb else 0
        
        # 获取错误追踪信息
        trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # 输出错误信息
        print(f"Error: {error_message}", file=sys.stderr)
        print(f"File: {file}, Line: {line}", file=sys.stderr)
        print(f"Trace: {trace}", file=sys.stderr)