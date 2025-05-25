#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库工厂类

提供数据库连接和操作功能
"""

import os
import importlib
from startmvc.core.db.DbCore import DbCore
from startmvc.core.Exceptions import StartMVCException, ConfigException, DatabaseException, RouteException, ViewException, ControllerException


class Db:
    """数据库工厂类"""

    # 数据库连接实例
    _instances = {}

    @staticmethod
    def connect(config_name='default'):
        """连接数据库

        Args:
            config_name (str): 配置名称

        Returns:
            DbCore: 数据库核心实例
        """
        # 如果已经存在连接实例，直接返回
        if config_name in Db._instances:
            return Db._instances[config_name]
        
        # 加载数据库配置
        from startmvc.function import config
        db_config = config('database', {})
        
        if not db_config:
            raise ConfigException("数据库配置不存在")
        
        # 获取指定配置
        if config_name not in db_config:
            raise ConfigException(f"数据库配置 \'{config_name}\' 不存在")
        
        config = db_config[config_name]
        
        # 创建数据库核心实例
        db = DbCore(config)
        
        # 根据类型创建驱动实例
        driver_type = config.get('type', 'sqlite').lower()
        
        try:
            # 动态导入驱动类
            driver_module = importlib.import_module(f"startmvc.core.db.drivers.{driver_type.capitalize()}")
            driver_class = getattr(driver_module, driver_type.capitalize())
            
            # 创建驱动实例
            driver = driver_class(config)
            
            # 初始化驱动
            db.init_driver(driver)
            
            # 保存实例
            Db._instances[config_name] = db
            
            return db
        except ImportError:
            raise DatabaseException(f"数据库驱动 \'{driver_type}\' 不存在")
        except Exception as e:
            raise Exception(f"数据库连接错误: {str(e)}")

    @staticmethod
    def close(config_name='default'):
        """关闭数据库连接

        Args:
            config_name (str): 配置名称

        Returns:
            bool: 是否成功
        """
        if config_name in Db._instances:
            db = Db._instances[config_name]
            db.driver.close()
            del Db._instances[config_name]
            return True
        return False

    @staticmethod
    def close_all():
        """关闭所有数据库连接

        Returns:
            bool: 是否成功
        """
        for config_name in list(Db._instances.keys()):
            Db.close(config_name)
        return True