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

class Login(Controller):
    """登录控制器"""
    
    def index(self, *args):
        """
        登录页面
        """
        # 如果已经登录，则重定向到首页
        if 'user_id' in cherrypy.session:
            # 检查是否有重定向URL
            redirect_url = cherrypy.session.get('redirect_url', '/')
            # 清除重定向URL
            if 'redirect_url' in cherrypy.session:
                del cherrypy.session['redirect_url']
            # 重定向
            raise cherrypy.HTTPRedirect(redirect_url)
        
        # 渲染登录页面
        return self.render('index')
    
    def login(self, *args):
        """
        处理登录请求
        """
        # 获取表单数据
        username = cherrypy.request.params.get('username', '')
        password = cherrypy.request.params.get('password', '')
        
        # 验证用户名和密码
        if username == 'admin' and password == 'admin':
            # 登录成功，设置会话
            cherrypy.session['user_id'] = 1
            cherrypy.session['username'] = username
            
            # 检查是否有重定向URL
            redirect_url = cherrypy.session.get('redirect_url', '/')
            # 清除重定向URL
            if 'redirect_url' in cherrypy.session:
                del cherrypy.session['redirect_url']
            
            # 返回成功消息和重定向URL
            return {
                'code': 0,
                'message': '登录成功',
                'redirect': redirect_url
            }
        else:
            # 登录失败
            return {
                'code': 1,
                'message': '用户名或密码错误'
            }
    
    def logout(self, *args):
        """
        退出登录
        """
        # 清除会话
        cherrypy.session.clear()
        
        # 重定向到登录页面
        raise cherrypy.HTTPRedirect('/login')