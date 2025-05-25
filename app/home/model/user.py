#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

from startmvc.core.Model import Model

class User(Model):
    """
    用户模型
    """
    
    def __init__(self):
        """
        构造函数
        """
        super().__init__()
        
        # 设置表名
        self.table = 'user'
    
    def get_user_by_id(self, user_id):
        """
        根据ID获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            dict: 用户信息
        """
        return self._db.where('id', user_id).first()
    
    def get_user_list(self, page=1, limit=10):
        """
        获取用户列表
        
        Args:
            page: 页码
            limit: 每页数量
            
        Returns:
            list: 用户列表
        """
        return self.paginate(page, limit)['data']
    
    def add_user(self, data):
        """
        添加用户
        
        Args:
            data: 用户数据
            
        Returns:
            int: 新增用户ID
        """
        return self.insert(data)
    
    def update_user(self, user_id, data):
        """
        更新用户
        
        Args:
            user_id: 用户ID
            data: 用户数据
            
        Returns:
            bool: 是否成功
        """
        return self.where('id', user_id).update(data)
    
    def delete_user(self, user_id):
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否成功
        """
        return self.where('id', user_id).delete()