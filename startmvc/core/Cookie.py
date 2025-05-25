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
import base64
import hmac
import hashlib
import cherrypy
from datetime import datetime, timedelta

class Cookie:
    """
    Cookie类
    用于管理Cookie
    """
    
    def __init__(self):
        """
        构造函数
        """
        # Cookie配置
        self.config = {
            'path': '/',
            'domain': '',
            'secure': False,
            'httponly': True,
            'samesite': 'Lax',
            'expire': 0,
            'encrypt': False,
            'encrypt_key': 'startmvc',
        }
    
    def set_config(self, config):
        """
        设置Cookie配置
        
        Args:
            config: Cookie配置
        """
        self.config.update(config)
    
    def get(self, name, default=None):
        """
        获取Cookie
        
        Args:
            name: Cookie名称
            default: 默认值
            
        Returns:
            str: Cookie值
        """
        # 获取Cookie
        cookie = cherrypy.request.cookie.get(name)
        
        # 如果Cookie不存在，则返回默认值
        if not cookie:
            return default
        
        # 获取Cookie值
        value = cookie.value
        
        # 如果启用了加密，则解密
        if self.config['encrypt']:
            value = self._decrypt(value)
        
        return value
    
    def set(self, name, value, expire=None, path=None, domain=None, secure=None, httponly=None, samesite=None):
        """
        设置Cookie
        
        Args:
            name: Cookie名称
            value: Cookie值
            expire: 过期时间（秒）
            path: 路径
            domain: 域名
            secure: 是否只在HTTPS下传输
            httponly: 是否只能通过HTTP访问
            samesite: 跨站策略
            
        Returns:
            bool: 是否成功
        """
        # 如果启用了加密，则加密
        if self.config['encrypt']:
            value = self._encrypt(value)
        
        # 设置Cookie
        cherrypy.response.cookie[name] = value
        
        # 设置Cookie路径
        cherrypy.response.cookie[name]['path'] = path or self.config['path']
        
        # 设置Cookie域名
        if domain or self.config['domain']:
            cherrypy.response.cookie[name]['domain'] = domain or self.config['domain']
        
        # 设置Cookie过期时间
        if expire is not None:
            expires = datetime.now() + timedelta(seconds=expire)
            cherrypy.response.cookie[name]['expires'] = expires.strftime('%a, %d-%b-%Y %H:%M:%S GMT')
        elif self.config['expire'] > 0:
            expires = datetime.now() + timedelta(seconds=self.config['expire'])
            cherrypy.response.cookie[name]['expires'] = expires.strftime('%a, %d-%b-%Y %H:%M:%S GMT')
        
        # 设置Cookie安全标志
        if secure is not None:
            cherrypy.response.cookie[name]['secure'] = secure
        elif self.config['secure']:
            cherrypy.response.cookie[name]['secure'] = True
        
        # 设置Cookie HttpOnly标志
        if httponly is not None:
            cherrypy.response.cookie[name]['httponly'] = httponly
        elif self.config['httponly']:
            cherrypy.response.cookie[name]['httponly'] = True
        
        # 设置Cookie SameSite属性
        if samesite is not None and samesite in ['Lax', 'Strict', 'None']:
            cherrypy.response.cookie[name]['samesite'] = samesite
        elif self.config['samesite'] in ['Lax', 'Strict', 'None']:
            cherrypy.response.cookie[name]['samesite'] = self.config['samesite']
        
        return True
    
    def delete(self, name, path=None, domain=None):
        """
        删除Cookie
        
        Args:
            name: Cookie名称
            path: 路径
            domain: 域名
            
        Returns:
            bool: 是否成功
        """
        # 设置Cookie
        cherrypy.response.cookie[name] = ''
        
        # 设置Cookie路径
        cherrypy.response.cookie[name]['path'] = path or self.config['path']
        
        # 设置Cookie域名
        if domain or self.config['domain']:
            cherrypy.response.cookie[name]['domain'] = domain or self.config['domain']
        
        # 设置Cookie过期时间为过去时间
        cherrypy.response.cookie[name]['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
        
        return True
    
    def has(self, name):
        """
        检查Cookie是否存在
        
        Args:
            name: Cookie名称
            
        Returns:
            bool: 是否存在
        """
        return name in cherrypy.request.cookie
    
    def all(self):
        """
        获取所有Cookie
        
        Returns:
            dict: 所有Cookie
        """
        # 所有Cookie
        cookies = {}
        
        # 遍历Cookie
        for name, cookie in cherrypy.request.cookie.items():
            # 获取Cookie值
            value = cookie.value
            
            # 如果启用了加密，则解密
            if self.config['encrypt']:
                value = self._decrypt(value)
            
            # 添加到结果
            cookies[name] = value
        
        return cookies
    
    def _encrypt(self, value):
        """
        加密Cookie值
        
        Args:
            value: Cookie值
            
        Returns:
            str: 加密后的Cookie值
        """
        try:
            # 转换为字符串
            if not isinstance(value, str):
                value = json.dumps(value)
            
            # 当前时间戳
            timestamp = int(time.time())
            
            # 加密数据
            data = {
                'value': value,
                'timestamp': timestamp
            }
            
            # 转换为JSON字符串
            data_str = json.dumps(data)
            
            # Base64编码
            data_base64 = base64.b64encode(data_str.encode('utf-8')).decode('utf-8')
            
            # 计算签名
            signature = self._sign(data_base64)
            
            # 返回加密后的值
            return f"{data_base64}.{signature}"
        except Exception:
            return value
    
    def _decrypt(self, value):
        """
        解密Cookie值
        
        Args:
            value: 加密后的Cookie值
            
        Returns:
            str: 解密后的Cookie值
        """
        try:
            # 分割数据和签名
            parts = value.split('.')
            
            # 如果格式不正确，则返回原值
            if len(parts) != 2:
                return value
            
            # 获取数据和签名
            data_base64, signature = parts
            
            # 验证签名
            if not self._verify(data_base64, signature):
                return value
            
            # Base64解码
            data_str = base64.b64decode(data_base64).decode('utf-8')
            
            # 解析JSON
            data = json.loads(data_str)
            
            # 返回原始值
            return data['value']
        except Exception:
            return value
    
    def _sign(self, data):
        """
        计算签名
        
        Args:
            data: 数据
            
        Returns:
            str: 签名
        """
        # 计算HMAC
        h = hmac.new(
            self.config['encrypt_key'].encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        )
        
        # 返回签名
        return h.hexdigest()
    
    def _verify(self, data, signature):
        """
        验证签名
        
        Args:
            data: 数据
            signature: 签名
            
        Returns:
            bool: 是否有效
        """
        # 计算签名
        expected = self._sign(data)
        
        # 验证签名
        return hmac.compare_digest(expected, signature)