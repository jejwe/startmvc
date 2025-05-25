#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
事件示例控制器
"""

from startmvc.core.Controller import Controller
from startmvc.core.Event import Event as EventCore, listen, trigger, remove, has, get_listeners, clear


class Event(Controller):
    """事件示例控制器"""

    def index(self, *args):
        """事件示例首页"""
        # 清空所有事件监听器
        clear()
        
        # 注册事件监听器
        self._register_listeners()
        
        # 获取所有事件监听器
        user_created_listeners = get_listeners('user.created')
        user_updated_listeners = get_listeners('user.updated')
        user_deleted_listeners = get_listeners('user.deleted')
        
        # 渲染视图
        return self.render('event/index', {
            'title': '事件示例',
            'user_created_listeners': user_created_listeners,
            'user_updated_listeners': user_updated_listeners,
            'user_deleted_listeners': user_deleted_listeners,
        })

    def trigger_event(self, *args):
        """触发事件"""
        # 获取事件名称
        event_name = self.request.get('event', 'user.created')
        
        # 创建用户数据
        user = {
            'id': 1,
            'name': 'John Doe',
            'email': 'john@example.com',
            'created_at': '2023-01-01 12:00:00',
        }
        
        # 触发事件
        results = trigger(event_name, user)
        
        # 渲染视图
        return self.render('event/trigger', {
            'title': '触发事件',
            'event_name': event_name,
            'user': user,
            'results': results,
            'has_listeners': has(event_name),
        })

    def remove_listener(self, *args):
        """移除事件监听器"""
        # 获取事件名称
        event_name = self.request.get('event', 'user.created')
        
        # 移除事件监听器
        success = remove(event_name)
        
        # 渲染视图
        return self.render('event/remove', {
            'title': '移除事件监听器',
            'event_name': event_name,
            'success': success,
            'has_listeners': has(event_name),
        })

    def _register_listeners(self):
        """注册事件监听器"""
        # 用户创建事件
        listen('user.created', self._log_user_created, 10)
        listen('user.created', self._send_welcome_email, 5)
        listen('user.created', self._notify_admin, 0)
        
        # 用户更新事件
        listen('user.updated', self._log_user_updated, 10)
        listen('user.updated', self._send_update_notification, 5)
        
        # 用户删除事件
        listen('user.deleted', self._log_user_deleted, 10)
        listen('user.deleted', self._cleanup_user_data, 5)

    def _log_user_created(self, user):
        """记录用户创建日志"""
        return f"[LOG] 用户创建: {user['name']} ({user['email']})"

    def _send_welcome_email(self, user):
        """发送欢迎邮件"""
        return f"[EMAIL] 发送欢迎邮件给: {user['email']}"

    def _notify_admin(self, user):
        """通知管理员"""
        return f"[NOTIFY] 通知管理员: 新用户 {user['name']} 已注册"

    def _log_user_updated(self, user):
        """记录用户更新日志"""
        return f"[LOG] 用户更新: {user['name']} ({user['email']})"

    def _send_update_notification(self, user):
        """发送更新通知"""
        return f"[EMAIL] 发送更新通知给: {user['email']}"

    def _log_user_deleted(self, user):
        """记录用户删除日志"""
        return f"[LOG] 用户删除: {user['name']} ({user['email']})"

    def _cleanup_user_data(self, user):
        """清理用户数据"""
        return f"[CLEANUP] 清理用户数据: {user['id']}"