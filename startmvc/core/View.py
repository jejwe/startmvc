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
import re
import cherrypy
from typing import Dict, Any, List, Optional
from startmvc.core.Exceptions import ViewException

class View:
    """视图类"""
    
    # 视图变量
    _vars = {}
    
    # 模板引擎实例
    _engine = None
    
    def __init__(self):
        """初始化视图"""
        # 初始化模板引擎
        self._engine = TemplateEngine()
    
    def assign(self, name: str, value: Any) -> None:
        """
        分配变量到视图
        
        Args:
            name: 变量名
            value: 变量值
        """
        self._vars[name] = value
    
    def render(self, template: str) -> str:
        """
        渲染视图
        
        Args:
            template: 模板文件路径
        
        Returns:
            渲染后的视图内容
        """
        # 检查模板文件是否存在
        if not os.path.isfile(template):
            raise ViewException(f"模板文件不存在: {template}")
        
        # 渲染模板
        return self._engine.render(template, self._vars)


class TemplateEngine:
    """模板引擎类"""
    
    # 缓存的模板
    _cache = {}
    
    def render(self, template: str, vars: Dict[str, Any]) -> str:
        """
        渲染模板
        
        Args:
            template: 模板文件路径
            vars: 模板变量
        
        Returns:
            渲染后的内容
        """
        # 读取模板内容
        with open(template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 编译模板
        compiled = self._compile(content)
        
        # 渲染模板
        return self._evaluate(compiled, vars)
    
    def _compile(self, content: str) -> str:
        """
        编译模板
        
        Args:
            content: 模板内容
        
        Returns:
            编译后的Python代码
        """
        # 替换变量标签 {$var} -> {{ var }}
        content = re.sub(r'\{\$([a-zA-Z0-9_]+)\}', r'{{ \1 }}', content)
        
        # 替换if标签 {if condition} -> {% if condition %}
        content = re.sub(r'\{if\s+(.+?)\}', r'{% if \1 %}', content)
        content = re.sub(r'\{/if\}', r'{% endif %}', content)
        
        # 替换foreach标签 {foreach $array as $key => $value} -> {% for key, value in array.items() %}
        content = re.sub(r'\{foreach\s+\$([a-zA-Z0-9_]+)\s+as\s+\$([a-zA-Z0-9_]+)\s+=>\s+\$([a-zA-Z0-9_]+)\}', 
                         r'{% for \2, \3 in \1.items() %}', content)
        
        # 替换foreach标签 {foreach $array as $value} -> {% for value in array %}
        content = re.sub(r'\{foreach\s+\$([a-zA-Z0-9_]+)\s+as\s+\$([a-zA-Z0-9_]+)\}', 
                         r'{% for \2 in \1 %}', content)
        
        content = re.sub(r'\{/foreach\}', r'{% endfor %}', content)
        
        # 替换include标签 {include file="path/to/file"} -> {% include "path/to/file" %}
        content = re.sub(r'\{include\s+file="(.+?)"\}', r'{% include "\1" %}', content)
        
        # 替换PHP代码块 <?php ... ?> -> {% ... %}
        content = re.sub(r'<\?php\s+(.+?)\s+\?>', r'{% \1 %}', content, flags=re.DOTALL)
        
        return content
    
    def _evaluate(self, template: str, vars: Dict[str, Any]) -> str:
        """
        执行模板
        
        Args:
            template: 编译后的模板
            vars: 模板变量
        
        Returns:
            渲染后的内容
        """
        # 使用Jinja2模板引擎渲染
        try:
            from jinja2 import Template
            # 添加自动转义以提高安全性
            jinja_template = Template(template, autoescape=True)
            return jinja_template.render(**vars)
        except ImportError:
            # 如果没有安装Jinja2，使用简单的字符串替换
            result = template
            
            # 替换变量
            for name, value in vars.items():
                # 简单的HTML转义
                if isinstance(value, str):
                    value = value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
                result = result.replace(f'{{ {name} }}', str(value))
            
            return result