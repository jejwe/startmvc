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
import pickle
import time
import uuid
import cherrypy
import threading
from datetime import datetime, timedelta

class Session:
    """
    会话类
    支持文件会话和内存会话
    """
    
    # 会话实例
    _instance = None
    
    # 会话锁
    _lock = threading.Lock()
    
    # 内存会话
    _memory_sessions = {}
    
    @classmethod
    def get_instance(cls):
        """
        获取会话实例（单例模式）

        Returns:
            Session: 会话实例
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
        
    # 保持向后兼容
    @classmethod
    def instance(cls):
        """
        获取会话实例（单例模式）- 保持向后兼容
        
        Returns:
            Session: 会话实例
        """
        return cls.get_instance()
    
    def __init__(self):
        """
        构造函数
        """
        # 会话配置
        self.config = {}
        
        # 会话目录
        self.session_dir = os.path.join(os.getcwd(), 'runtime', 'session')
        
        # 创建会话目录
        os.makedirs(self.session_dir, exist_ok=True)
        
        # 会话ID
        self.session_id = None
        
        # 会话数据
        self.data = {}
        
        # 会话是否已启动
        self.started = False
    
    def set_config(self, config):
        """
        设置会话配置
        
        Args:
            config: 会话配置
        """
        self.config = config
        
        # 如果配置了会话目录，则使用配置的目录
        if 'path' in config:
            self.session_dir = config['path']
            os.makedirs(self.session_dir, exist_ok=True)
    
    def start(self):
        """
        启动会话
        
        Returns:
            bool: 是否成功
        """
        # 如果会话已启动，则直接返回
        if self.started:
            return True
        
        # 获取会话ID
        self.session_id = self._get_session_id()
        
        # 加载会话数据
        self._load()
        
        # 标记会话已启动
        self.started = True
        
        return True
    
    def get(self, key, default=None):
        """
        获取会话数据
        
        Args:
            key: 会话键
            default: 默认值
            
        Returns:
            mixed: 会话值
        """
        # 如果会话未启动，则启动会话
        if not self.started:
            self.start()
        
        # 返回会话数据
        return self.data.get(key, default)
    
    def set(self, key, value):
        """
        设置会话数据
        
        Args:
            key: 会话键
            value: 会话值
            
        Returns:
            bool: 是否成功
        """
        # 如果会话未启动，则启动会话
        if not self.started:
            self.start()
        
        # 设置会话数据
        self.data[key] = value
        
        # 保存会话数据
        self._save()
        
        return True
    
    def delete(self, key):
        """
        删除会话数据
        
        Args:
            key: 会话键
            
        Returns:
            bool: 是否成功
        """
        # 如果会话未启动，则启动会话
        if not self.started:
            self.start()
        
        # 如果会话键存在，则删除
        if key in self.data:
            del self.data[key]
            
            # 保存会话数据
            self._save()
            
            return True
        
        return False
    
    def clear(self):
        """
        清空会话数据
        
        Returns:
            bool: 是否成功
        """
        # 如果会话未启动，则启动会话
        if not self.started:
            self.start()
        
        # 清空会话数据
        self.data = {}
        
        # 保存会话数据
        self._save()
        
        return True
    
    def destroy(self):
        """
        销毁会话
        
        Returns:
            bool: 是否成功
        """
        # 如果会话未启动，则直接返回
        if not self.started:
            return True
        
        # 如果配置了使用内存会话
        if self.config.get('type') == 'memory':
            # 如果会话ID存在，则删除
            if self.session_id in self._memory_sessions:
                del self._memory_sessions[self.session_id]
        else:
            # 获取会话文件路径
            session_file = self._get_session_file()
            
            # 如果会话文件存在，则删除
            if os.path.exists(session_file):
                os.remove(session_file)
        
        # 删除会话Cookie
        self._delete_cookie()
        
        # 重置会话数据
        self.data = {}
        
        # 标记会话未启动
        self.started = False
        
        return True
    
    def gc(self):
        """
        垃圾回收
        删除过期会话
        
        Returns:
            int: 删除的会话数量
        """
        # 如果配置了使用内存会话
        if self.config.get('type') == 'memory':
            return self._gc_memory()
        
        # 默认使用文件会话
        return self._gc_file()
    
    def _get_session_id(self):
        """
        获取会话ID
        
        Returns:
            str: 会话ID
        """
        # 会话Cookie名称
        cookie_name = self.config.get('name', 'STARTMVC_SESSION')
        
        # 尝试从Cookie获取会话ID
        session_id = cherrypy.request.cookie.get(cookie_name)
        
        # 如果Cookie中存在会话ID
        if session_id:
            session_id = session_id.value
            
            # 验证会话ID格式
            if self._validate_session_id(session_id):
                # 如果配置了使用内存会话
                if self.config.get('type') == 'memory':
                    # 如果会话ID存在于内存中，则返回
                    if session_id in self._memory_sessions:
                        return session_id
                else:
                    # 获取会话文件路径
                    session_file = self._get_session_file(session_id)
                    
                    # 如果会话文件存在，则返回
                    if os.path.exists(session_file):
                        return session_id
        
        # 生成新的会话ID
        session_id = self._generate_session_id()
        
        # 设置会话Cookie
        self._set_cookie(session_id)
        
        return session_id
    
    def _validate_session_id(self, session_id):
        """
        验证会话ID格式
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 是否有效
        """
        # 会话ID必须是32位字符串
        if not isinstance(session_id, str) or len(session_id) != 32:
            return False
        
        # 会话ID必须只包含16进制字符
        try:
            int(session_id, 16)
            return True
        except ValueError:
            return False
    
    def _generate_session_id(self):
        """
        生成会话ID
        
        Returns:
            str: 会话ID
        """
        # 生成UUID并去除连字符
        return uuid.uuid4().hex
    
    def _set_cookie(self, session_id):
        """
        设置会话Cookie
        
        Args:
            session_id: 会话ID
        """
        # 会话Cookie名称
        cookie_name = self.config.get('name', 'STARTMVC_SESSION')
        
        # 会话Cookie过期时间
        expire = self.config.get('expire', 86400)
        
        # 设置Cookie
        cherrypy.response.cookie[cookie_name] = session_id
        
        # 设置Cookie路径
        cherrypy.response.cookie[cookie_name]['path'] = '/'
        
        # 设置Cookie过期时间
        if expire > 0:
            expires = datetime.now() + timedelta(seconds=expire)
            cherrypy.response.cookie[cookie_name]['expires'] = expires.strftime('%a, %d-%b-%Y %H:%M:%S GMT')
        
        # 设置Cookie安全标志
        if self.config.get('secure', False):
            cherrypy.response.cookie[cookie_name]['secure'] = True
        
        # 设置Cookie HttpOnly标志
        if self.config.get('httponly', True):
            cherrypy.response.cookie[cookie_name]['httponly'] = True
        
        # 设置Cookie SameSite属性
        samesite = self.config.get('samesite', 'Lax')
        if samesite in ['Lax', 'Strict', 'None']:
            cherrypy.response.cookie[cookie_name]['samesite'] = samesite
    
    def _delete_cookie(self):
        """
        删除会话Cookie
        """
        # 会话Cookie名称
        cookie_name = self.config.get('name', 'STARTMVC_SESSION')
        
        # 设置Cookie
        cherrypy.response.cookie[cookie_name] = ''
        
        # 设置Cookie路径
        cherrypy.response.cookie[cookie_name]['path'] = '/'
        
        # 设置Cookie过期时间为过去时间
        cherrypy.response.cookie[cookie_name]['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
    
    def _load(self):
        """
        加载会话数据
        """
        # 如果配置了使用内存会话
        if self.config.get('type') == 'memory':
            self._load_memory()
        else:
            self._load_file()
    
    def _save(self):
        """
        保存会话数据
        """
        # 如果配置了使用内存会话
        if self.config.get('type') == 'memory':
            self._save_memory()
        else:
            self._save_file()
    
    def _load_memory(self):
        """
        从内存加载会话数据
        """
        # 如果会话ID存在于内存中
        if self.session_id in self._memory_sessions:
            session_data = self._memory_sessions[self.session_id]
            
            # 如果会话已过期，则删除
            if session_data['expire'] > 0 and session_data['expire'] < time.time():
                del self._memory_sessions[self.session_id]
                self.data = {}
            else:
                self.data = session_data['data']
        else:
            self.data = {}
    
    def _save_memory(self):
        """
        保存会话数据到内存
        """
        # 计算过期时间戳
        expire_time = 0
        expire = self.config.get('expire', 86400)
        if expire > 0:
            expire_time = time.time() + expire
        
        # 保存会话数据
        self._memory_sessions[self.session_id] = {
            'data': self.data,
            'expire': expire_time,
            'last_activity': time.time()
        }
    
    def _load_file(self):
        """
        从文件加载会话数据
        """
        # 获取会话文件路径
        session_file = self._get_session_file()
        
        # 如果会话文件不存在，则返回空数据
        if not os.path.exists(session_file):
            self.data = {}
            return
        
        try:
            # 读取会话文件
            with open(session_file, 'rb') as f:
                session_data = pickle.load(f)
            
            # 如果会话已过期，则删除
            if session_data['expire'] > 0 and session_data['expire'] < time.time():
                os.remove(session_file)
                self.data = {}
            else:
                self.data = session_data['data']
                
                # 更新最后活动时间
                session_data['last_activity'] = time.time()
                
                # 写入会话文件
                with open(session_file, 'wb') as f:
                    pickle.dump(session_data, f)
        except Exception:
            # 如果读取失败，则删除会话文件
            if os.path.exists(session_file):
                os.remove(session_file)
            self.data = {}
    
    def _save_file(self):
        """
        保存会话数据到文件
        """
        # 获取会话文件路径
        session_file = self._get_session_file()
        
        # 计算过期时间戳
        expire_time = 0
        expire = self.config.get('expire', 86400)
        if expire > 0:
            expire_time = time.time() + expire
        
        # 会话数据
        session_data = {
            'data': self.data,
            'expire': expire_time,
            'last_activity': time.time()
        }
        
        try:
            # 写入会话文件
            with open(session_file, 'wb') as f:
                pickle.dump(session_data, f)
        except Exception:
            pass
    
    def _get_session_file(self, session_id=None):
        """
        获取会话文件路径
        
        Args:
            session_id: 会话ID
            
        Returns:
            str: 会话文件路径
        """
        # 如果未指定会话ID，则使用当前会话ID
        if session_id is None:
            session_id = self.session_id
        
        # 返回会话文件路径
        return os.path.join(self.session_dir, f"{session_id}.session")
    
    def _gc_memory(self):
        """
        内存会话垃圾回收
        
        Returns:
            int: 删除的会话数量
        """
        # 删除计数
        count = 0
        
        # 当前时间
        now = time.time()
        
        # 遍历所有会话
        for session_id in list(self._memory_sessions.keys()):
            session_data = self._memory_sessions[session_id]
            
            # 如果会话已过期，则删除
            if session_data['expire'] > 0 and session_data['expire'] < now:
                del self._memory_sessions[session_id]
                count += 1
                continue
            
            # 如果会话超过最大生存时间，则删除
            max_lifetime = self.config.get('max_lifetime', 0)
            if max_lifetime > 0:
                lifetime = now - session_data['last_activity']
                if lifetime > max_lifetime:
                    del self._memory_sessions[session_id]
                    count += 1
        
        return count
    
    def _gc_file(self):
        """
        文件会话垃圾回收
        
        Returns:
            int: 删除的会话数量
        """
        # 删除计数
        count = 0
        
        # 当前时间
        now = time.time()
        
        # 遍历会话目录
        for file_name in os.listdir(self.session_dir):
            # 只处理会话文件
            if not file_name.endswith('.session'):
                continue
            
            # 会话文件路径
            session_file = os.path.join(self.session_dir, file_name)
            
            try:
                # 读取会话文件
                with open(session_file, 'rb') as f:
                    session_data = pickle.load(f)
                
                # 如果会话已过期，则删除
                if session_data['expire'] > 0 and session_data['expire'] < now:
                    os.remove(session_file)
                    count += 1
                    continue
                
                # 如果会话超过最大生存时间，则删除
                max_lifetime = self.config.get('max_lifetime', 0)
                if max_lifetime > 0:
                    lifetime = now - session_data['last_activity']
                    if lifetime > max_lifetime:
                        os.remove(session_file)
                        count += 1
            except Exception:
                # 如果读取失败，则删除会话文件
                if os.path.exists(session_file):
                    os.remove(session_file)
                count += 1
        
        return count