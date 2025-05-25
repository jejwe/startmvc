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
from typing import Dict, Any, List, Optional, Union, Tuple
from startmvc.core.Db import Db


class Model:
    """模型基类"""
    
    # 数据库实例
    _db = None
    
    # 表名
    table = ''
    
    # 主键
    pk = 'id'
    
    # 数据库配置名称
    _config_name = 'default'
    
    def __init__(self):
        """初始化模型"""
        # 连接数据库
        self._connect()
    
    def _connect(self) -> None:
        """连接数据库"""
        self._db = Db.connect(self._config_name)
        
        # 设置表名
        if not self.table:
            self.table = self.__class__.__name__.lower().replace('model', '')
        
        # 设置表
        self._db.table(self.table)
    
    def query(self, sql: str, params: Optional[List] = None) -> List[Dict[str, Any]]:
        """
        执行SQL查询
        
        Args:
            sql: SQL语句
            params: 参数
        
        Returns:
            查询结果
        """
        return self._db.driver.query(sql, params)
    
    def execute(self, sql: str, params: Optional[List] = None) -> int:
        """
        执行SQL语句
        
        Args:
            sql: SQL语句
            params: 参数
        
        Returns:
            影响的行数
        """
        return self._db.driver.execute(sql, params)
    
    def get_by_id(self, id: Union[int, str], fields: str = '*') -> Optional[Dict[str, Any]]:
        """
        根据ID查询记录
        
        Args:
            id: 记录ID
            fields: 字段列表
        
        Returns:
            查询结果
        """
        return self._db.table(self.table).fields(fields).where(self.pk, id).first()
    
    def get_all(self, fields: str = '*', where: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        查询多条记录
        
        Args:
            fields: 字段列表
            where: WHERE条件
        
        Returns:
            查询结果
        """
        query = self._db.table(self.table).fields(fields)
        
        if where:
            query.where(where)
        
        return query.get()
    
    def insert(self, data: Dict[str, Any]) -> int:
        """
        插入记录
        
        Args:
            data: 要插入的数据
        
        Returns:
            新记录的ID
        """
        if not data:
            return 0
        
        self._db.table(self.table).insert(data)
        return self._db.driver.get_last_insert_id()
    
    def update(self, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """
        更新记录
        
        Args:
            data: 要更新的数据
            where: WHERE条件
        
        Returns:
            影响的行数
        """
        if not data:
            return 0
        
        return self._db.table(self.table).where(where).update(data)
    
    def delete(self, where: Dict[str, Any]) -> int:
        """
        删除记录
        
        Args:
            where: WHERE条件
        
        Returns:
            影响的行数
        """
        return self._db.table(self.table).where(where).delete()
    
    def count(self, where: Optional[Dict] = None) -> int:
        """
        统计记录数
        
        Args:
            where: WHERE条件
        
        Returns:
            记录数
        """
        query = self._db.table(self.table)
        
        if where:
            query.where(where)
        
        return query.count()
    
    def paginate(self, page: int = 1, per_page: int = 10, fields: str = '*', where: Optional[Dict] = None) -> Dict[str, Any]:
        """
        分页查询
        
        Args:
            page: 页码
            per_page: 每页记录数
            fields: 字段列表
            where: WHERE条件
        
        Returns:
            分页结果
        """
        query = self._db.table(self.table).fields(fields)
        
        if where:
            query.where(where)
        
        # 计算总记录数
        total = query.count()
        
        # 计算总页数
        total_pages = (total + per_page - 1) // per_page
        
        # 计算偏移量
        offset = (page - 1) * per_page
        
        # 查询数据
        data = query.limit(per_page).offset(offset).get()
        
        return {
            'total': total,
            'per_page': per_page,
            'current_page': page,
            'last_page': total_pages,
            'data': data
        }
    
    def begin_transaction(self) -> bool:
        """
        开始事务
        
        Returns:
            是否成功
        """
        return self._db.begin_transaction()
    
    def commit(self) -> bool:
        """
        提交事务
        
        Returns:
            是否成功
        """
        return self._db.commit()
    
    def rollback(self) -> bool:
        """
        回滚事务
        
        Returns:
            是否成功
        """
        return self._db.rollback()
    
    def transaction(self):
        """
        事务上下文管理器
        
        用法:
        with model.transaction():
            model.insert(data1)
            model.insert(data2)
        """
        class TransactionContextManager:
            def __init__(self, model):
                self.model = model
            
            def __enter__(self):
                self.model.begin_transaction()
                return self.model
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    self.model.rollback()
                    return False
                self.model.commit()
                return True
        
        return TransactionContextManager(self)
    
    def get_last_query(self) -> str:
        """
        获取最后执行的SQL语句
        
        Returns:
            SQL语句
        """
        return self._db.get_last_query()
    
    def __del__(self):
        """析构函数，关闭数据库连接"""
        Db.close(self._config_name)