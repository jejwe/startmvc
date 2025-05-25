#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库接口类

定义所有数据库驱动必须实现的方法
"""

from abc import ABC, abstractmethod


class DbInterface(ABC):
    """数据库接口类"""

    @abstractmethod
    def connect(self):
        """连接数据库"""
        pass

    @abstractmethod
    def close(self):
        """关闭数据库连接"""
        pass

    @abstractmethod
    def query(self, sql, params=None):
        """执行SQL查询"""
        pass

    @abstractmethod
    def execute(self, sql, params=None):
        """执行SQL语句"""
        pass

    @abstractmethod
    def insert(self, table, data):
        """插入数据"""
        pass

    @abstractmethod
    def update(self, table, data, where):
        """更新数据"""
        pass

    @abstractmethod
    def delete(self, table, where):
        """删除数据"""
        pass

    @abstractmethod
    def select(self, table, fields='*', where=None, order=None, limit=None, offset=None):
        """查询数据"""
        pass
        
    @abstractmethod
    def get_all(self, table, fields='*', where=None, order=None, limit=None, offset=None):
        """查询数据（select的别名，更符合Python命名风格）"""
        pass

    @abstractmethod
    def get_last_query(self):
        """获取最后执行的SQL语句"""
        pass

    @abstractmethod
    def get_last_insert_id(self):
        """获取最后插入的ID"""
        pass

    @abstractmethod
    def begin_transaction(self):
        """开始事务"""
        pass

    @abstractmethod
    def commit(self):
        """提交事务"""
        pass

    @abstractmethod
    def rollback(self):
        """回滚事务"""
        pass

    @abstractmethod
    def table_exists(self, table):
        """检查表是否存在"""
        pass

    @abstractmethod
    def get_tables(self):
        """获取所有表"""
        pass

    @abstractmethod
    def get_fields(self, table):
        """获取表字段"""
        pass