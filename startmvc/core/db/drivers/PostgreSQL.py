#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PostgreSQL数据库驱动

提供PostgreSQL数据库操作功能
"""

import psycopg2
import psycopg2.extras
from startmvc.core.db.DbInterface import DbInterface
from startmvc.core.Exceptions import DatabaseException


class PostgreSQL(DbInterface):
    """PostgreSQL数据库驱动"""

    def __init__(self, config):
        """初始化PostgreSQL驱动

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
            self.conn = psycopg2.connect(
                host=self.config.get('hostname', 'localhost'),
                port=int(self.config.get('hostport', 5432)),
                user=self.config.get('username', 'postgres'),
                password=self.config.get('password', ''),
                dbname=self.config.get('database', ''),
            )
            self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            return True
        except psycopg2.Error as e:
            raise DatabaseException(f"PostgreSQL连接错误: {str(e)}")

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
        except psycopg2.Error as e:
            raise DatabaseException(f"PostgreSQL查询错误: {str(e)}\nSQL: {sql}")

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
            
            # 获取最后插入的ID（如果有）
            if sql.strip().upper().startswith('INSERT'):
                try:
                    self.cursor.execute("SELECT lastval()")
                    result = self.cursor.fetchone()
                    if result:
                        self.last_insert_id = result['lastval']
                except:
                    self.last_insert_id = None
            
            self.conn.commit()
            return self.affected_rows
        except psycopg2.Error as e:
            self.conn.rollback()
            raise DatabaseException(f"PostgreSQL执行错误: {str(e)}\nSQL: {sql}")

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
        
        for i, (field, value) in enumerate(data.items(), 1):
            fields.append(f"\"{field}\"")
            placeholders.append(f"%s")
            values.append(value)
        
        sql = f"INSERT INTO \"{table}\" ({', '.join(fields)}) VALUES ({', '.join(placeholders)}) RETURNING id"
        
        try:
            self.cursor.execute(sql, values)
            result = self.cursor.fetchone()
            if result and 'id' in result:
                self.last_insert_id = result['id']
            self.conn.commit()
            return self.cursor.rowcount
        except psycopg2.Error as e:
            self.conn.rollback()
            raise DatabaseException(f"PostgreSQL插入错误: {str(e)}\nSQL: {sql}")

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
        
        for i, (field, value) in enumerate(data.items(), 1):
            set_parts.append(f"\"{field}\" = %s")
            values.append(value)
        
        sql = f"UPDATE \"{table}\" SET {', '.join(set_parts)}"
        
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
        sql = f"DELETE FROM \"{table}\""
        
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
        sql = f"SELECT {fields} FROM \"{table}\""
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
        self.execute("BEGIN")
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
        sql = "SELECT to_regclass(%s) IS NOT NULL"
        result = self.query(sql, [table])
        return result[0]['?column?'] if result else False

    def get_tables(self):
        """获取所有表

        Returns:
            list: 表名列表
        """
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        result = self.query(sql)
        return [row['table_name'] for row in result]

    def get_fields(self, table):
        """获取表字段

        Args:
            table (str): 表名

        Returns:
            list: 字段信息列表
        """
        sql = """
        SELECT 
            column_name, 
            data_type, 
            is_nullable, 
            column_default,
            (SELECT count(*) FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.constraint_type = 'PRIMARY KEY'
                    AND tc.table_name = c.table_name
                    AND kcu.column_name = c.column_name) > 0 as is_primary
        FROM information_schema.columns c
        WHERE table_name = %s
        """
        result = self.query(sql, [table])
        fields = []
        
        for row in result:
            fields.append({
                'name': row['column_name'],
                'type': row['data_type'],
                'null': row['is_nullable'] == 'YES',
                'default': row['column_default'],
                'primary_key': row['is_primary']
            })
        
        return fields