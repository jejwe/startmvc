#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

from startmvc.core.Controller import Controller
from startmvc.function import lang

class Index(Controller):
    """首页控制器"""
    
    def index(self, *args):
        """首页方法"""
        # 获取语言包
        title = lang('startmvc', 'StartMVC Python Framework')
        
        # 分配变量到视图
        self.assign('title', title)
        self.assign('welcome', 'Welcome to StartMVC Python Framework!')
        self.assign('description', 'A lightweight MVC framework based on CherryPy')
        self.assign('version', '1.0.0')
        
        # 显示视图
        return self.render()