#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

import json
import requests
from urllib.parse import urlencode

class Http:
    """
    HTTP客户端类
    用于发送HTTP请求
    """
    
    def __init__(self):
        """
        构造函数
        """
        # 请求头
        self.headers = {}
        
        # 请求超时时间（秒）
        self.timeout = 30
        
        # 是否验证SSL证书
        self.verify_ssl = True
        
        # 代理服务器
        self.proxy = None
        
        # 最大重定向次数
        self.max_redirects = 5
        
        # 请求会话
        self.session = requests.Session()
    
    def set_header(self, name, value):
        """
        设置请求头
        
        Args:
            name: 请求头名称
            value: 请求头值
            
        Returns:
            Http: HTTP客户端对象
        """
        self.headers[name] = value
        return self
    
    def set_headers(self, headers):
        """
        设置多个请求头
        
        Args:
            headers: 请求头字典
            
        Returns:
            Http: HTTP客户端对象
        """
        self.headers.update(headers)
        return self
    
    def set_timeout(self, timeout):
        """
        设置请求超时时间
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            Http: HTTP客户端对象
        """
        self.timeout = timeout
        return self
    
    def set_verify_ssl(self, verify_ssl):
        """
        设置是否验证SSL证书
        
        Args:
            verify_ssl: 是否验证SSL证书
            
        Returns:
            Http: HTTP客户端对象
        """
        self.verify_ssl = verify_ssl
        return self
    
    def set_proxy(self, proxy):
        """
        设置代理服务器
        
        Args:
            proxy: 代理服务器
            
        Returns:
            Http: HTTP客户端对象
        """
        self.proxy = proxy
        return self
    
    def set_max_redirects(self, max_redirects):
        """
        设置最大重定向次数
        
        Args:
            max_redirects: 最大重定向次数
            
        Returns:
            Http: HTTP客户端对象
        """
        self.max_redirects = max_redirects
        return self
    
    def get(self, url, params=None):
        """
        发送GET请求
        
        Args:
            url: 请求URL
            params: 请求参数
            
        Returns:
            Response: 响应对象
        """
        return self._request('GET', url, params=params)
    
    def post(self, url, data=None, json=None):
        """
        发送POST请求
        
        Args:
            url: 请求URL
            data: 请求数据
            json: JSON数据
            
        Returns:
            Response: 响应对象
        """
        return self._request('POST', url, data=data, json=json)
    
    def put(self, url, data=None, json=None):
        """
        发送PUT请求
        
        Args:
            url: 请求URL
            data: 请求数据
            json: JSON数据
            
        Returns:
            Response: 响应对象
        """
        return self._request('PUT', url, data=data, json=json)
    
    def delete(self, url, params=None):
        """
        发送DELETE请求
        
        Args:
            url: 请求URL
            params: 请求参数
            
        Returns:
            Response: 响应对象
        """
        return self._request('DELETE', url, params=params)
    
    def head(self, url, params=None):
        """
        发送HEAD请求
        
        Args:
            url: 请求URL
            params: 请求参数
            
        Returns:
            Response: 响应对象
        """
        return self._request('HEAD', url, params=params)
    
    def options(self, url, params=None):
        """
        发送OPTIONS请求
        
        Args:
            url: 请求URL
            params: 请求参数
            
        Returns:
            Response: 响应对象
        """
        return self._request('OPTIONS', url, params=params)
    
    def patch(self, url, data=None, json=None):
        """
        发送PATCH请求
        
        Args:
            url: 请求URL
            data: 请求数据
            json: JSON数据
            
        Returns:
            Response: 响应对象
        """
        return self._request('PATCH', url, data=data, json=json)
    
    def _request(self, method, url, **kwargs):
        """
        发送请求
        
        Args:
            method: 请求方法
            url: 请求URL
            **kwargs: 请求参数
            
        Returns:
            Response: 响应对象
        """
        # 设置请求头
        if self.headers:
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            kwargs['headers'].update(self.headers)
        
        # 设置请求超时时间
        kwargs['timeout'] = self.timeout
        
        # 设置是否验证SSL证书
        kwargs['verify'] = self.verify_ssl
        
        # 设置代理服务器
        if self.proxy:
            kwargs['proxies'] = {
                'http': self.proxy,
                'https': self.proxy
            }
        
        # 设置最大重定向次数
        kwargs['allow_redirects'] = True
        kwargs['max_redirects'] = self.max_redirects
        
        # 发送请求
        response = self.session.request(method, url, **kwargs)
        
        # 返回响应对象
        return Response(response)


class Response:
    """
    HTTP响应类
    用于处理HTTP响应
    """
    
    def __init__(self, response):
        """
        构造函数
        
        Args:
            response: requests响应对象
        """
        # 原始响应对象
        self.response = response
        
        # 响应状态码
        self.status_code = response.status_code
        
        # 响应头
        self.headers = response.headers
        
        # 响应内容
        self.content = response.content
        
        # 响应文本
        self.text = response.text
        
        # 响应URL
        self.url = response.url
        
        # 响应编码
        self.encoding = response.encoding
        
        # 响应Cookie
        self.cookies = response.cookies
        
        # 响应历史
        self.history = response.history
        
        # 请求时间（秒）
        self.elapsed = response.elapsed.total_seconds()
    
    def json(self):
        """
        解析JSON响应
        
        Returns:
            dict: JSON数据
        """
        try:
            return self.response.json()
        except json.JSONDecodeError:
            return None
    
    def is_ok(self):
        """
        响应是否成功
        
        Returns:
            bool: 是否成功
        """
        return 200 <= self.status_code < 300
    
    def is_redirect(self):
        """
        响应是否重定向
        
        Returns:
            bool: 是否重定向
        """
        return self.status_code in [301, 302, 303, 307, 308]
    
    def is_client_error(self):
        """
        响应是否客户端错误
        
        Returns:
            bool: 是否客户端错误
        """
        return 400 <= self.status_code < 500
    
    def is_server_error(self):
        """
        响应是否服务器错误
        
        Returns:
            bool: 是否服务器错误
        """
        return 500 <= self.status_code < 600
    
    def is_error(self):
        """
        响应是否错误
        
        Returns:
            bool: 是否错误
        """
        return 400 <= self.status_code < 600
    
    def save(self, file_path):
        """
        保存响应内容到文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            with open(file_path, 'wb') as f:
                f.write(self.content)
            return True
        except Exception:
            return False