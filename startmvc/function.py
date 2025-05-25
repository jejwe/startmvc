#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

StartMVC是一个轻量级的Python MVC框架，基于CherryPy构建。

原作者: Shao Bing
Python移植: OpenHands
版权所有: Copyright (c) 2020-2025
许可证: Apache2开源协议，需保留开发者信息
项目主页: http://startmvc.com
"""

import os
import json
import pprint
import cherrypy
import importlib.util
from typing import Any, Dict, Optional, Union

# 全局配置缓存
_config_cache = None

class Config:
    """配置管理类"""
    
    @staticmethod
    def get(key: Optional[str] = None, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键名
            default: 默认值
        
        Returns:
            配置值
        """
        return config(key, default)

class Lang:
    """语言管理类"""
    
    @staticmethod
    def get(key: str, default: str = '') -> str:
        """
        获取语言文本
        
        Args:
            key: 语言键名
            default: 默认值
        
        Returns:
            语言文本
        """
        return lang(key, default)

class Debug:
    """调试工具类"""
    
    @staticmethod
    def dump(var: Any, label: Optional[str] = None, echo: bool = True) -> str:
        """
        格式化输出变量
        
        Args:
            var: 变量
            label: 标签
            echo: 是否直接输出
        
        Returns:
            格式化后的字符串
        """
        return dump(var, label, echo)

class Utils:
    """工具类"""
    
    @staticmethod
    def get_ip() -> str:
        """
        获取客户端IP
        
        Returns:
            IP地址
        """
        return get_ip()
    
    @staticmethod
    def url(url: str) -> str:
        """
        生成URL
        
        Args:
            url: 原始URL
        
        Returns:
            处理后的URL
        """
        return url(url)

def lang(key: str, default: str = '') -> str:
    """
    语言包调用
    
    Args:
        key: 语言包键名
        default: 默认值
    
    Returns:
        对应的语言文本
    """
    global _lang_cache
    if not hasattr(lang, '_lang_cache'):
        lang._lang_cache = {}
    
    if not key:
        return default
    
    # 如果语言包已经加载过，则直接返回对应的值
    if key in lang._lang_cache:
        return lang._lang_cache[key]
    
    # 获取当前模块和语言设置
    from boot import APP_PATH, ROOT_PATH
    import cherrypy
    
    # 获取当前模块
    if hasattr(cherrypy.request, 'module'):
        module = cherrypy.request.module
    else:
        module = 'home'
    
    # 获取语言设置
    conf = config()
    locale = conf.get('locale', 'zh_cn')
    
    # 加载语言包
    lang_path = os.path.join(APP_PATH, module, 'language', f'{locale}.py')
    
    if os.path.isfile(lang_path):
        spec = importlib.util.spec_from_file_location(f"{module}_language", lang_path)
        if spec:
            lang_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lang_module)
            
            # 获取语言包内容
            if hasattr(lang_module, 'lang_data'):
                lang_data = lang_module.lang_data
                if key in lang_data:
                    lang._lang_cache[key] = lang_data[key]
                    return lang_data[key]
    
    # 如果未找到对应的语言包键值，则返回默认值或者键名本身
    return default if default else key

def dump(var: Any, label: Optional[str] = None, echo: bool = True) -> str:
    """
    格式化变量输出
    
    Args:
        var: 要输出的变量
        label: 标签
        echo: 是否直接输出
    
    Returns:
        格式化后的字符串
    """
    output = pprint.pformat(var)
    
    # 判断是否在命令行环境
    cli = not hasattr(cherrypy, 'request')
    
    if cli:
        output = f"\n{label}\n{output}\n" if label else f"\n{output}\n"
    else:
        output = f"<pre>\n{label}\n{output}</pre>\n" if label else f"<pre>\n{output}</pre>\n"
    
    if echo:
        print(output)
    
    return output

def config(key: Optional[str] = None, default: Any = None) -> Any:
    """
    配置文件函数
    
    Args:
        key: 配置键名
        default: 默认值
    
    Returns:
        配置值
    """
    global _config_cache
    
    # 如果配置未加载，先加载配置
    if _config_cache is None:
        from boot import ROOT_PATH, ENV
        import importlib
        
        _config_cache = {}
        
        # 尝试导入配置模块
        try:
            # 先导入公共配置
            try:
                common_config = importlib.import_module('config.common')
                if hasattr(common_config, 'config'):
                    _config_cache.update(common_config.config)
            except ImportError:
                # 如果导入失败，尝试使用动态导入
                common_config_path = os.path.join(ROOT_PATH, 'config', 'common.py')
                if os.path.isfile(common_config_path):
                    spec = importlib.util.spec_from_file_location("common_config", common_config_path)
                    if spec:
                        common_config = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(common_config)
                        if hasattr(common_config, 'config'):
                            _config_cache.update(common_config.config)
            
            # 再导入环境配置
            try:
                env_config = importlib.import_module(f'config.{ENV}')
                if hasattr(env_config, 'config'):
                    _config_cache.update(env_config.config)
            except ImportError:
                # 如果导入失败，尝试使用动态导入
                env_config_path = os.path.join(ROOT_PATH, 'config', f'{ENV}.py')
                if os.path.isfile(env_config_path):
                    spec = importlib.util.spec_from_file_location(f"{ENV}_config", env_config_path)
                    if spec:
                        env_config = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(env_config)
                        if hasattr(env_config, 'config'):
                            _config_cache.update(env_config.config)
        except Exception as e:
            print(f"Error loading configuration: {e}")
    
    # 如果没有指定 key，返回所有配置
    if key is None:
        return _config_cache
    
    # 支持点号分隔的多级配置访问
    if '.' in key:
        parts = key.split('.')
        value = _config_cache
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        return value
    
    # 返回指定配置项，如果不存在返回默认值
    return _config_cache.get(key, default)

def url(url: str) -> str:
    """
    URL生成函数
    
    Args:
        url: 原始URL
    
    Returns:
        处理后的URL
    """
    url_suffix = config('url_suffix', '.html')
    url = url + url_suffix
    
    if config('urlrewrite', True):
        url = '/' + url
    else:
        url = '/index.py/' + url
    
    return url.replace('%2F', '/')

def get_ip() -> str:
    """
    获取客户端的真实IP地址
    
    Returns:
        IP地址
    """
    if not hasattr(cherrypy, 'request'):
        return '127.0.0.1'
    
    # 优先检查HTTP_X_FORWARDED_FOR
    if 'X-Forwarded-For' in cherrypy.request.headers:
        ips = cherrypy.request.headers['X-Forwarded-For'].split(',')
        for ip in ips:
            ip = ip.strip()
            if ip and ip.lower() != 'unknown':
                return ip
    
    # 如果没有通过X-Forwarded-For获取到IP，使用远程地址
    return cherrypy.request.remote.ip