#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志类

提供日志记录功能
"""

import os
import time
import logging
import traceback
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class Logger:
    """日志类"""

    # 日志级别
    LEVEL_DEBUG = logging.DEBUG
    LEVEL_INFO = logging.INFO
    LEVEL_WARNING = logging.WARNING
    LEVEL_ERROR = logging.ERROR
    LEVEL_CRITICAL = logging.CRITICAL

    # 日志实例
    _instances = {}

    @classmethod
    def get_logger(cls, name='app', config=None):
        """获取日志实例

        Args:
            name (str): 日志名称
            config (dict): 配置

        Returns:
            Logger: 日志实例
        """
        # 如果已经存在实例，直接返回
        if name in cls._instances:
            return cls._instances[name]
        
        # 创建新实例
        logger = cls(name, config)
        cls._instances[name] = logger
        
        return logger

    def __init__(self, name='app', config=None):
        """初始化日志类

        Args:
            name (str): 日志名称
            config (dict): 配置
        """
        self.name = name
        
        # 加载配置
        self._load_config(config)
        
        # 创建日志目录
        os.makedirs(self.config['path'], exist_ok=True)
        
        # 创建日志记录器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.config['level'])
        
        # 清除已有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 添加处理器
        self._add_handlers()

    def _load_config(self, config=None):
        """加载配置

        Args:
            config (dict): 配置
        """
        # 默认配置
        default_config = {
            'level': logging.DEBUG,
            'path': os.path.join(os.getcwd(), 'runtime', 'log'),
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
        }
        
        # 合并配置
        if config is None:
            # 从全局配置加载
            from startmvc.function import config as get_config
            log_config = get_config('common', {}).get('log', {})
            self.config = {**default_config, **log_config}
        else:
            self.config = {**default_config, **config}
        
        # 替换文件名中的变量
        self.config['file'] = self.config['file'].format(name=self.name)

    def _add_handlers(self):
        """添加处理器"""
        # 创建格式化器
        formatter = logging.Formatter(
            fmt=self.config['format'],
            datefmt=self.config['date_format']
        )
        
        # 添加文件处理器
        file_path = os.path.join(self.config['path'], self.config['file'])
        
        if self.config['rotate_type'] == 'size':
            # 按大小轮转
            file_handler = RotatingFileHandler(
                filename=file_path,
                maxBytes=self.config['max_size'],
                backupCount=self.config['backup_count'],
                encoding=self.config['encoding']
            )
        else:
            # 按时间轮转
            file_handler = TimedRotatingFileHandler(
                filename=file_path,
                when=self.config['when'],
                interval=self.config['interval'],
                backupCount=self.config['backup_count'],
                encoding=self.config['encoding']
            )
        
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # 添加控制台处理器
        if self.config['console']:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def debug(self, message, *args, **kwargs):
        """记录调试日志

        Args:
            message: 日志消息
            *args: 参数
            **kwargs: 关键字参数
        """
        self.logger.debug(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        """记录信息日志

        Args:
            message: 日志消息
            *args: 参数
            **kwargs: 关键字参数
        """
        self.logger.info(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        """记录警告日志

        Args:
            message: 日志消息
            *args: 参数
            **kwargs: 关键字参数
        """
        self.logger.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        """记录错误日志

        Args:
            message: 日志消息
            *args: 参数
            **kwargs: 关键字参数
        """
        self.logger.error(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        """记录严重错误日志

        Args:
            message: 日志消息
            *args: 参数
            **kwargs: 关键字参数
        """
        self.logger.critical(message, *args, **kwargs)

    def exception(self, message, *args, **kwargs):
        """记录异常日志

        Args:
            message: 日志消息
            *args: 参数
            **kwargs: 关键字参数
        """
        self.logger.exception(message, *args, **kwargs)

    def log(self, level, message, *args, **kwargs):
        """记录日志

        Args:
            level: 日志级别
            message: 日志消息
            *args: 参数
            **kwargs: 关键字参数
        """
        self.logger.log(level, message, *args, **kwargs)

    @classmethod
    def log_exception(cls, e, level=logging.ERROR):
        """记录异常

        Args:
            e: 异常
            level: 日志级别
        """
        logger = cls.get_logger()
        logger.log(level, f"Exception: {str(e)}\n{traceback.format_exc()}")

    @classmethod
    def log_request(cls, request, response=None):
        """记录请求

        Args:
            request: 请求对象
            response: 响应对象
        """
        logger = cls.get_logger('request')
        
        # 请求信息
        method = getattr(request, 'method', 'UNKNOWN')
        path = getattr(request, 'path_info', 'UNKNOWN')
        ip = getattr(request, 'remote_addr', 'UNKNOWN')
        
        # 响应信息
        status = getattr(response, 'status', 'UNKNOWN')
        
        # 记录日志
        logger.info(f"{ip} {method} {path} {status}")

    @classmethod
    def log_sql(cls, sql, params=None, time=0):
        """记录SQL

        Args:
            sql: SQL语句
            params: 参数
            time: 执行时间（秒）
        """
        logger = cls.get_logger('sql')
        
        # 记录日志
        if params:
            logger.debug(f"SQL: {sql} Params: {params} Time: {time:.6f}s")
        else:
            logger.debug(f"SQL: {sql} Time: {time:.6f}s")