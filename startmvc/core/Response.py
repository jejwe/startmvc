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
import cherrypy
from io import BytesIO

class Response:
    """
    响应类
    用于处理HTTP响应
    """
    
    def __init__(self):
        """
        构造函数
        """
        # 响应内容
        self.body = ''
        
        # 响应状态码
        self.status = 200
        
        # 响应头
        self.headers = {}
        
        # 响应类型
        self.content_type = 'text/html'
        
        # 字符集
        self.charset = 'utf-8'
    
    def set_content(self, content):
        """
        设置响应内容
        
        Args:
            content: 响应内容
            
        Returns:
            Response: 响应对象
        """
        self.body = content
        return self
    
    def set_status(self, status):
        """
        设置响应状态码
        
        Args:
            status: 响应状态码
            
        Returns:
            Response: 响应对象
        """
        self.status = status
        return self
    
    def set_header(self, name, value):
        """
        设置响应头
        
        Args:
            name: 响应头名称
            value: 响应头值
            
        Returns:
            Response: 响应对象
        """
        self.headers[name] = value
        return self
    
    def set_content_type(self, content_type, charset=None):
        """
        设置响应类型
        
        Args:
            content_type: 响应类型
            charset: 字符集
            
        Returns:
            Response: 响应对象
        """
        self.content_type = content_type
        if charset:
            self.charset = charset
        return self
    
    def json(self, data, status=200):
        """
        返回JSON响应
        
        Args:
            data: 响应数据
            status: 响应状态码
            
        Returns:
            Response: 响应对象
        """
        self.body = data
        self.status = status
        self.content_type = 'application/json'
        return self
    
    def html(self, html, status=200):
        """
        返回HTML响应
        
        Args:
            html: HTML内容
            status: 响应状态码
            
        Returns:
            Response: 响应对象
        """
        self.body = html
        self.status = status
        self.content_type = 'text/html'
        return self
    
    def text(self, text, status=200):
        """
        返回文本响应
        
        Args:
            text: 文本内容
            status: 响应状态码
            
        Returns:
            Response: 响应对象
        """
        self.body = text
        self.status = status
        self.content_type = 'text/plain'
        return self
    
    def xml(self, xml, status=200):
        """
        返回XML响应
        
        Args:
            xml: XML内容
            status: 响应状态码
            
        Returns:
            Response: 响应对象
        """
        self.body = xml
        self.status = status
        self.content_type = 'application/xml'
        return self
    
    def redirect(self, url, status=302):
        """
        重定向
        
        Args:
            url: 重定向URL
            status: 响应状态码
            
        Returns:
            Response: 响应对象
        """
        self.status = status
        self.headers['Location'] = url
        return self
    
    def file(self, file_path, content_type=None, download_name=None):
        """
        返回文件响应
        
        Args:
            file_path: 文件路径
            content_type: 响应类型
            download_name: 下载文件名
            
        Returns:
            Response: 响应对象
        """
        # 读取文件内容
        with open(file_path, 'rb') as f:
            self.body = f.read()
        
        # 设置响应类型
        if content_type:
            self.content_type = content_type
        else:
            # 根据文件扩展名设置响应类型
            import mimetypes
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type:
                self.content_type = content_type
            else:
                self.content_type = 'application/octet-stream'
        
        # 设置下载文件名
        if download_name:
            self.headers['Content-Disposition'] = f'attachment; filename="{download_name}"'
        
        return self
    
    def stream(self, stream, content_type='application/octet-stream', download_name=None):
        """
        返回流响应
        
        Args:
            stream: 数据流
            content_type: 响应类型
            download_name: 下载文件名
            
        Returns:
            Response: 响应对象
        """
        # 设置响应内容
        if isinstance(stream, BytesIO):
            self.body = stream.getvalue()
        else:
            self.body = stream
        
        # 设置响应类型
        self.content_type = content_type
        
        # 设置下载文件名
        if download_name:
            self.headers['Content-Disposition'] = f'attachment; filename="{download_name}"'
        
        return self
    
    def send(self):
        """
        发送响应
        """
        # 设置响应状态码
        cherrypy.response.status = self.status
        
        # 设置响应头
        for name, value in self.headers.items():
            cherrypy.response.headers[name] = value
        
        # 设置响应类型
        if self.charset:
            cherrypy.response.headers['Content-Type'] = f'{self.content_type}; charset={self.charset}'
        else:
            cherrypy.response.headers['Content-Type'] = self.content_type
        
        # 处理响应内容
        if isinstance(self.body, (dict, list, tuple)):
            # 如果是JSON数据，则转换为JSON字符串
            return json.dumps(self.body, ensure_ascii=False)
        elif isinstance(self.body, bytes):
            # 如果是二进制数据，则直接返回
            return self.body
        else:
            # 其他类型转换为字符串
            return str(self.body)
    
    def __str__(self):
        """
        字符串表示
        
        Returns:
            str: 响应内容
        """
        if isinstance(self.body, (dict, list, tuple)):
            return json.dumps(self.body, ensure_ascii=False)
        elif isinstance(self.body, bytes):
            return self.body.decode(self.charset, errors='replace')
        else:
            return str(self.body)