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
import secrets
import cherrypy
from datetime import datetime, timedelta

class Csrf:
    """
    CSRF类
    用于防止跨站请求伪造
    """
    
    def __init__(self):
        """
        构造函数
        """
        # CSRF配置
        self.config = {
            'token_name': '_token',
            'header_name': 'X-CSRF-TOKEN',
            'cookie_name': 'XSRF-TOKEN',
            'expire': 7200,  # 2小时
            'encrypt_key': 'startmvc',
        }
    
    def set_config(self, config):
        """
        设置CSRF配置
        
        Args:
            config: CSRF配置
        """
        self.config.update(config)
    
    def generate(self):
        """
        生成CSRF令牌
        
        Returns:
            str: CSRF令牌
        """
        # 生成随机令牌
        token = secrets.token_hex(32)
        
        # 当前时间戳
        timestamp = int(time.time())
        
        # 令牌数据
        data = {
            'token': token,
            'timestamp': timestamp
        }
        
        # 转换为JSON字符串
        data_str = json.dumps(data)
        
        # Base64编码
        data_base64 = base64.b64encode(data_str.encode('utf-8')).decode('utf-8')
        
        # 计算签名
        signature = self._sign(data_base64)
        
        # 返回CSRF令牌
        return f"{data_base64}.{signature}"
    
    def validate(self, token=None):
        """
        验证CSRF令牌
        
        Args:
            token: CSRF令牌
            
        Returns:
            bool: 是否有效
        """
        # 如果未指定令牌，则从请求中获取
        if token is None:
            token = self._get_token_from_request()
        
        # 如果令牌为空，则验证失败
        if not token:
            return False
        
        try:
            # 分割数据和签名
            parts = token.split('.')
            
            # 如果格式不正确，则验证失败
            if len(parts) != 2:
                return False
            
            # 获取数据和签名
            data_base64, signature = parts
            
            # 验证签名
            if not self._verify(data_base64, signature):
                return False
            
            # Base64解码
            data_str = base64.b64decode(data_base64).decode('utf-8')
            
            # 解析JSON
            data = json.loads(data_str)
            
            # 验证过期时间
            if self.config['expire'] > 0:
                # 当前时间戳
                now = int(time.time())
                
                # 如果令牌已过期，则验证失败
                if data['timestamp'] + self.config['expire'] < now:
                    return False
            
            return True
        except Exception:
            return False
    
    def store(self, token=None):
        """
        存储CSRF令牌
        
        Args:
            token: CSRF令牌
            
        Returns:
            str: CSRF令牌
        """
        # 如果未指定令牌，则生成新令牌
        if token is None:
            token = self.generate()
        
        # 设置Cookie
        cherrypy.response.cookie[self.config['cookie_name']] = token
        
        # 设置Cookie路径
        cherrypy.response.cookie[self.config['cookie_name']]['path'] = '/'
        
        # 设置Cookie过期时间
        if self.config['expire'] > 0:
            expires = datetime.now() + timedelta(seconds=self.config['expire'])
            cherrypy.response.cookie[self.config['cookie_name']]['expires'] = expires.strftime('%a, %d-%b-%Y %H:%M:%S GMT')
        
        # 设置Cookie SameSite属性
        cherrypy.response.cookie[self.config['cookie_name']]['samesite'] = 'Lax'
        
        return token
    
    def get_token(self):
        """
        获取CSRF令牌
        
        Returns:
            str: CSRF令牌
        """
        # 从请求中获取令牌
        token = self._get_token_from_request()
        
        # 如果令牌为空或无效，则生成新令牌
        if not token or not self.validate(token):
            token = self.generate()
            
            # 存储令牌
            self.store(token)
        
        return token
    
    def get_input_tag(self):
        """
        获取CSRF输入标签
        
        Returns:
            str: CSRF输入标签
        """
        # 获取CSRF令牌
        token = self.get_token()
        
        # 返回输入标签
        return f'<input type="hidden" name="{self.config["token_name"]}" value="{token}">'
    
    def _get_token_from_request(self):
        """
        从请求中获取CSRF令牌
        
        Returns:
            str: CSRF令牌
        """
        # 从表单中获取令牌
        if hasattr(cherrypy.request, 'params') and self.config['token_name'] in cherrypy.request.params:
            return cherrypy.request.params[self.config['token_name']]
        
        # 从请求头中获取令牌
        if self.config['header_name'] in cherrypy.request.headers:
            return cherrypy.request.headers[self.config['header_name']]
        
        # 从Cookie中获取令牌
        if self.config['cookie_name'] in cherrypy.request.cookie:
            return cherrypy.request.cookie[self.config['cookie_name']].value
        
        return None
    
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