#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MySQL数据库驱动

提供MySQL数据库操作功能
"""

import pymysql
from startmvc.core.db.DbInterface import DbInterface
from startmvc.core.Exceptions import DatabaseException


class MySQL(DbInterface):
    """MySQL数据库驱动"""

    def __init__(self, config):
        """初始化MySQL驱动

        Args:
            config (dict): 数据库配置
        """
        self.config = config
        self.conn = None
        self.cursor = None
        self.last_query = ''
        self.last_insert_id = None
        self.affected_rows = 0
        
        self.connect()

    def connect(self):
        """连接数据库"""
        try:
            self.conn = pymysql.connect(
                host=self.config.get('hostname', 'localhost'),
                port=int(self.config.get('hostport', 3306)),
                user=self.config.get('username', 'root'),
                password=self.config.get('password', ''),
                database=self.config.get('database', ''),
                charset=self.config.get('charset', 'utf8mb4'),
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.conn.cursor()
            return True
        except pymysql.Error as e:
            raise DatabaseException(f"MySQL连接错误: {str(e)}")

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
        return True

    def query(self, sql, params=None):
        """执行SQL查询

        Args:
            sql (str): SQL语句
            params (list): 参数

        Returns:
            list: 查询结果
        """
        self.last_query = sql
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            
            return self.cursor.fetchall()
        except pymysql.Error as e:
            raise DatabaseException(f"MySQL查询错误: {str(e)}\nSQL: {sql}")

    def execute(self, sql, params=None):
        """执行SQL语句

        Args:
            sql (str): SQL语句
            params (list): 参数

        Returns:
            int: 影响行数
        """
        self.last_query = sql
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            
            self.affected_rows = self.cursor.rowcount
            self.last_insert_id = self.conn.insert_id()
            self.conn.commit()
            
            return self.affected_rows
        except pymysql.Error as e:
            self.conn.rollback()
            raise DatabaseException(f"MySQL执行错误: {str(e)}\nSQL: {sql}")

    def insert(self, table, data):
        """插入数据

        Args:
            table (str): 表名
            data (dict): 数据

        Returns:
            int: 影响行数
        """
        fields = []
        placeholders = []
        values = []
        
        for field, value in data.items():
            fields.append(f"`{field}`")
            placeholders.append("%s")
            values.append(value)
        
        sql = f"INSERT INTO `{table}` ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        
        return self.execute(sql, values)

    def update(self, table, data, where, where_params=None):
        """更新数据

        Args:
            table (str): 表名
            data (dict): 数据
            where (str): WHERE条件
            where_params (list): WHERE参数

        Returns:
            int: 影响行数
        """
        set_parts = []
        values = []
        
        for field, value in data.items():
            set_parts.append(f"`{field}` = %s")
            values.append(value)
        
        sql = f"UPDATE `{table}` SET {', '.join(set_parts)}"
        
        if where:
            sql += f" {where}"
            if where_params:
                values.extend(where_params)
        
        return self.execute(sql, values)

    def delete(self, table, where, where_params=None):
        """删除数据

        Args:
            table (str): 表名
            where (str): WHERE条件
            where_params (list): WHERE参数

        Returns:
            int: 影响行数
        """
        sql = f"DELETE FROM `{table}`"
        
        if where:
            sql += f" {where}"
            return self.execute(sql, where_params)
        else:
            return self.execute(sql)

    def select(self, table, fields='*', where=None, order=None, limit=None, offset=None):
        """查询数据

        Args:
            table (str): 表名
            fields (str): 查询字段
            where (str): WHERE条件
            order (str): ORDER BY条件
            limit (int): LIMIT条件
            offset (int): OFFSET条件

        Returns:
            list: 查询结果
        """
        sql = f"SELECT {fields} FROM `{table}`"
        params = []
        
        if where:
            sql += f" WHERE {where}"
        
        if order:
            sql += f" ORDER BY {order}"
        
        if limit:
            sql += f" LIMIT {limit}"
            
            if offset:
                sql += f" OFFSET {offset}"
        
        return self.query(sql, params)
        
    def get_all(self, table, fields='*', where=None, order=None, limit=None, offset=None):
        """查询数据（select的别名，更符合Python命名风格）

        Args:
            table (str): 表名
            fields (str): 查询字段
            where (str): WHERE条件
            order (str): ORDER BY条件
            limit (int): LIMIT条件
            offset (int): OFFSET条件

        Returns:
            list: 查询结果
        """
        return self.select(table, fields, where, order, limit, offset)

    def get_last_query(self):
        """获取最后执行的SQL语句

        Returns:
            str: SQL语句
        """
        return self.last_query

    def get_last_insert_id(self):
        """获取最后插入的ID

        Returns:
            int: ID
        """
        return self.last_insert_id

    def begin_transaction(self):
        """开始事务"""
        self.execute("START TRANSACTION")
        return True

    def commit(self):
        """提交事务"""
        self.conn.commit()
        return True

    def rollback(self):
        """回滚事务"""
        self.conn.rollback()
        return True

    def table_exists(self, table):
        """检查表是否存在

        Args:
            table (str): 表名

        Returns:
            bool: 是否存在
        """
        sql = "SHOW TABLES LIKE %s"
        result = self.query(sql, [table])
        return len(result) > 0

    def get_tables(self):
        """获取所有表

        Returns:
            list: 表名列表
        """
        sql = "SHOW TABLES"
        result = self.query(sql)
        return [list(row.values())[0] for row in result]

    def get_fields(self, table):
        """获取表字段

        Args:
            table (str): 表名

        Returns:
            list: 字段信息列表
        """
        sql = f"DESCRIBE `{table}`"
        result = self.query(sql)
        fields = []
        
        for row in result:
            fields.append({
                'name': row['Field'],
                'type': row['Type'],
                'null': row['Null'] == 'YES',
                'default': row['Default'],
                'primary_key': row['Key'] == 'PRI'
            })
        
        return fields