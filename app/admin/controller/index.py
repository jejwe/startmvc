#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

import cherrypy
from startmvc.core.Controller import Controller

class Index(Controller):
    """管理员首页控制器"""
    
    def index(self, *args):
        """管理员首页"""
        # 获取用户信息
        user_id = cherrypy.session.get('user_id')
        username = cherrypy.session.get('username')
        
        # 传递数据到视图
        self.assign('user_id', user_id)
        self.assign('username', username)
        self.assign('title', '管理员控制面板')
        self.assign('admin', f"欢迎管理员 {username} 登录系统")
        
        # 渲染视图
        return self.render()
    
    def dashboard(self, *args):
        """仪表盘"""
        # 获取用户信息
        user_id = cherrypy.session.get('user_id')
        username = cherrypy.session.get('username')
        
        # 传递数据到视图
        self.assign('user_id', user_id)
        self.assign('username', username)
        self.assign('title', '系统仪表盘')
        
        # 渲染视图
        return self.render('dashboard')
    
    def profile(self, *args):
        """个人资料"""
        # 获取用户信息
        user_id = cherrypy.session.get('user_id')
        username = cherrypy.session.get('username')
        
        # 传递数据到视图
        self.assign('user_id', user_id)
        self.assign('username', username)
        self.assign('title', '个人资料')
        
        # 渲染视图
        return self.render('profile')