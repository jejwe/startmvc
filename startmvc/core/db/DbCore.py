#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库核心类

提供基础的数据库操作和查询构建器功能
"""

import re
import time
from startmvc.core.db.DbInterface import DbInterface


class DbCore:
    """数据库核心类"""

    def __init__(self, config):
        """初始化数据库核心类

        Args:
            config (dict): 数据库配置
        """
        self.config = config
        self.driver = None
        self.prefix = config.get('prefix', '')
        self.last_query = ''
        self.query_count = 0
        self.query_time = 0
        self.transaction_count = 0
        self._where = []
        self._order = []
        self._limit = None
        self._offset = None
        self._join = []
        self._group = []
        self._having = []
        self._table = ''
        self._fields = '*'

    def init_driver(self, driver):
        """初始化数据库驱动

        Args:
            driver (DbInterface): 数据库驱动实例
        """
        if not isinstance(driver, DbInterface):
            raise TypeError("数据库驱动必须实现DbInterface接口")
        self.driver = driver

    def table(self, table):
        """设置表名

        Args:
            table (str): 表名

        Returns:
            DbCore: 当前实例
        """
        self._table = self.prefix + table
        return self

    def fields(self, fields):
        """设置查询字段

        Args:
            fields (str|list): 查询字段

        Returns:
            DbCore: 当前实例
        """
        if isinstance(fields, list):
            self._fields = ', '.join(fields)
        else:
            self._fields = fields
        return self

    def where(self, field, operator=None, value=None):
        """添加WHERE条件

        支持多种调用方式:
        where('id', '=', 1)
        where('id', 1)  # 默认使用 = 操作符
        where({'id': 1, 'status': 'active'})  # 批量设置条件

        Args:
            field: 字段名或条件字典
            operator: 操作符或值
            value: 值

        Returns:
            DbCore: 当前实例
        """
        if isinstance(field, dict):
            for k, v in field.items():
                self._where.append({
                    'field': k,
                    'operator': '=',
                    'value': v,
                    'logic': 'AND'
                })
        else:
            if value is None:
                value = operator
                operator = '='
            
            self._where.append({
                'field': field,
                'operator': operator,
                'value': value,
                'logic': 'AND'
            })
        
        return self

    def or_where(self, field, operator=None, value=None):
        """添加OR WHERE条件

        Args:
            field: 字段名或条件字典
            operator: 操作符或值
            value: 值

        Returns:
            DbCore: 当前实例
        """
        if isinstance(field, dict):
            for k, v in field.items():
                self._where.append({
                    'field': k,
                    'operator': '=',
                    'value': v,
                    'logic': 'OR'
                })
        else:
            if value is None:
                value = operator
                operator = '='
            
            self._where.append({
                'field': field,
                'operator': operator,
                'value': value,
                'logic': 'OR'
            })
        
        return self

    def where_in(self, field, values):
        """添加WHERE IN条件

        Args:
            field (str): 字段名
            values (list): 值列表

        Returns:
            DbCore: 当前实例
        """
        self._where.append({
            'field': field,
            'operator': 'IN',
            'value': values,
            'logic': 'AND'
        })
        return self

    def where_not_in(self, field, values):
        """添加WHERE NOT IN条件

        Args:
            field (str): 字段名
            values (list): 值列表

        Returns:
            DbCore: 当前实例
        """
        self._where.append({
            'field': field,
            'operator': 'NOT IN',
            'value': values,
            'logic': 'AND'
        })
        return self

    def like(self, field, value):
        """添加LIKE条件

        Args:
            field (str): 字段名
            value (str): 值

        Returns:
            DbCore: 当前实例
        """
        self._where.append({
            'field': field,
            'operator': 'LIKE',
            'value': value,
            'logic': 'AND'
        })
        return self

    def not_like(self, field, value):
        """添加NOT LIKE条件

        Args:
            field (str): 字段名
            value (str): 值

        Returns:
            DbCore: 当前实例
        """
        self._where.append({
            'field': field,
            'operator': 'NOT LIKE',
            'value': value,
            'logic': 'AND'
        })
        return self

    def order_by(self, field, direction='ASC'):
        """添加ORDER BY条件

        Args:
            field (str): 字段名
            direction (str): 排序方向，ASC或DESC

        Returns:
            DbCore: 当前实例
        """
        self._order.append({
            'field': field,
            'direction': direction.upper()
        })
        return self

    def limit(self, limit):
        """设置LIMIT

        Args:
            limit (int): 限制数量

        Returns:
            DbCore: 当前实例
        """
        self._limit = int(limit)
        return self

    def offset(self, offset):
        """设置OFFSET

        Args:
            offset (int): 偏移量

        Returns:
            DbCore: 当前实例
        """
        self._offset = int(offset)
        return self

    def join(self, table, on, type='INNER'):
        """添加JOIN

        Args:
            table (str): 表名
            on (str): 连接条件
            type (str): 连接类型，INNER, LEFT, RIGHT等

        Returns:
            DbCore: 当前实例
        """
        self._join.append({
            'table': self.prefix + table,
            'on': on,
            'type': type.upper()
        })
        return self

    def left_join(self, table, on):
        """添加LEFT JOIN

        Args:
            table (str): 表名
            on (str): 连接条件

        Returns:
            DbCore: 当前实例
        """
        return self.join(table, on, 'LEFT')

    def right_join(self, table, on):
        """添加RIGHT JOIN

        Args:
            table (str): 表名
            on (str): 连接条件

        Returns:
            DbCore: 当前实例
        """
        return self.join(table, on, 'RIGHT')

    def group_by(self, field):
        """添加GROUP BY

        Args:
            field (str): 字段名

        Returns:
            DbCore: 当前实例
        """
        if isinstance(field, list):
            self._group.extend(field)
        else:
            self._group.append(field)
        return self

    def having(self, field, operator=None, value=None):
        """添加HAVING条件

        Args:
            field: 字段名或条件字典
            operator: 操作符或值
            value: 值

        Returns:
            DbCore: 当前实例
        """
        if isinstance(field, dict):
            for k, v in field.items():
                self._having.append({
                    'field': k,
                    'operator': '=',
                    'value': v,
                    'logic': 'AND'
                })
        else:
            if value is None:
                value = operator
                operator = '='
            
            self._having.append({
                'field': field,
                'operator': operator,
                'value': value,
                'logic': 'AND'
            })
        
        return self

    def _build_where(self):
        """构建WHERE子句

        Returns:
            tuple: (SQL子句, 参数列表)
        """
        if not self._where:
            return '', []
        
        sql = ' WHERE '
        params = []
        first = True
        
        for condition in self._where:
            if not first:
                sql += f" {condition['logic']} "
            else:
                first = False
            
            field = condition['field']
            operator = condition['operator']
            value = condition['value']
            
            if operator.upper() in ('IN', 'NOT IN'):
                placeholders = ', '.join(['%s'] * len(value))
                sql += f"{field} {operator} ({placeholders})"
                params.extend(value)
            else:
                sql += f"{field} {operator} %s"
                params.append(value)
        
        return sql, params

    def _build_order(self):
        """构建ORDER BY子句

        Returns:
            str: SQL子句
        """
        if not self._order:
            return ''
        
        orders = []
        for order in self._order:
            orders.append(f"{order['field']} {order['direction']}")
        
        return ' ORDER BY ' + ', '.join(orders)

    def _build_limit(self):
        """构建LIMIT子句

        Returns:
            str: SQL子句
        """
        if self._limit is None:
            return ''
        
        sql = f' LIMIT {self._limit}'
        if self._offset is not None:
            sql += f' OFFSET {self._offset}'
        
        return sql

    def _build_join(self):
        """构建JOIN子句

        Returns:
            str: SQL子句
        """
        if not self._join:
            return ''
        
        sql = ''
        for join in self._join:
            sql += f" {join['type']} JOIN {join['table']} ON {join['on']}"
        
        return sql

    def _build_group(self):
        """构建GROUP BY子句

        Returns:
            str: SQL子句
        """
        if not self._group:
            return ''
        
        return ' GROUP BY ' + ', '.join(self._group)

    def _build_having(self):
        """构建HAVING子句

        Returns:
            tuple: (SQL子句, 参数列表)
        """
        if not self._having:
            return '', []
        
        sql = ' HAVING '
        params = []
        first = True
        
        for condition in self._having:
            if not first:
                sql += f" {condition['logic']} "
            else:
                first = False
            
            field = condition['field']
            operator = condition['operator']
            value = condition['value']
            
            sql += f"{field} {operator} %s"
            params.append(value)
        
        return sql, params

    def _build_select(self):
        """构建SELECT语句

        Returns:
            tuple: (SQL语句, 参数列表)
        """
        sql = f"SELECT {self._fields} FROM {self._table}"
        params = []
        
        # 添加JOIN
        sql += self._build_join()
        
        # 添加WHERE
        where_sql, where_params = self._build_where()
        sql += where_sql
        params.extend(where_params)
        
        # 添加GROUP BY
        sql += self._build_group()
        
        # 添加HAVING
        having_sql, having_params = self._build_having()
        sql += having_sql
        params.extend(having_params)
        
        # 添加ORDER BY
        sql += self._build_order()
        
        # 添加LIMIT
        sql += self._build_limit()
        
        return sql, params

    def get(self):
        """执行查询并获取结果

        Returns:
            list: 查询结果
        """
        sql, params = self._build_select()
        self._reset_query()
        return self._query(sql, params)

    def first(self):
        """获取第一条结果

        Returns:
            dict|None: 查询结果
        """
        self.limit(1)
        result = self.get()
        return result[0] if result else None

    def count(self, field='*'):
        """获取记录数

        Args:
            field (str): 计数字段

        Returns:
            int: 记录数
        """
        original_fields = self._fields
        self._fields = f"COUNT({field}) as count"
        result = self.first()
        self._fields = original_fields
        return result['count'] if result else 0

    def max(self, field):
        """获取最大值

        Args:
            field (str): 字段名

        Returns:
            mixed: 最大值
        """
        original_fields = self._fields
        self._fields = f"MAX({field}) as max_value"
        result = self.first()
        self._fields = original_fields
        return result['max_value'] if result else None

    def min(self, field):
        """获取最小值

        Args:
            field (str): 字段名

        Returns:
            mixed: 最小值
        """
        original_fields = self._fields
        self._fields = f"MIN({field}) as min_value"
        result = self.first()
        self._fields = original_fields
        return result['min_value'] if result else None

    def sum(self, field):
        """获取总和

        Args:
            field (str): 字段名

        Returns:
            mixed: 总和
        """
        original_fields = self._fields
        self._fields = f"SUM({field}) as sum_value"
        result = self.first()
        self._fields = original_fields
        return result['sum_value'] if result else None

    def avg(self, field):
        """获取平均值

        Args:
            field (str): 字段名

        Returns:
            mixed: 平均值
        """
        original_fields = self._fields
        self._fields = f"AVG({field}) as avg_value"
        result = self.first()
        self._fields = original_fields
        return result['avg_value'] if result else None

    def insert(self, data):
        """插入数据

        Args:
            data (dict): 数据

        Returns:
            int: 影响行数
        """
        return self.driver.insert(self._table, data)

    def update(self, data):
        """更新数据

        Args:
            data (dict): 数据

        Returns:
            int: 影响行数
        """
        where_sql, where_params = self._build_where()
        self._reset_query()
        return self.driver.update(self._table, data, where_sql, where_params)

    def delete(self):
        """删除数据

        Returns:
            int: 影响行数
        """
        where_sql, where_params = self._build_where()
        self._reset_query()
        return self.driver.delete(self._table, where_sql, where_params)

    def _query(self, sql, params=None):
        """执行查询

        Args:
            sql (str): SQL语句
            params (list): 参数

        Returns:
            list: 查询结果
        """
        self.last_query = self._interpolate_query(sql, params)
        self.query_count += 1
        
        start_time = time.time()
        result = self.driver.query(sql, params)
        self.query_time += time.time() - start_time
        
        return result

    def _execute(self, sql, params=None):
        """执行SQL语句

        Args:
            sql (str): SQL语句
            params (list): 参数

        Returns:
            int: 影响行数
        """
        self.last_query = self._interpolate_query(sql, params)
        self.query_count += 1
        
        start_time = time.time()
        result = self.driver.execute(sql, params)
        self.query_time += time.time() - start_time
        
        return result

    def _reset_query(self):
        """重置查询构建器"""
        self._where = []
        self._order = []
        self._limit = None
        self._offset = None
        self._join = []
        self._group = []
        self._having = []
        self._fields = '*'

    def _interpolate_query(self, sql, params):
        """插值SQL查询（用于调试）

        Args:
            sql (str): SQL语句
            params (list): 参数

        Returns:
            str: 完整SQL语句
        """
        if not params:
            return sql
        
        # 简单的SQL插值，仅用于调试
        sql_parts = sql.split('%s')
        result = ''
        
        for i, part in enumerate(sql_parts):
            result += part
            if i < len(params):
                value = params[i]
                if isinstance(value, str):
                    result += f"'{value}'"
                elif value is None:
                    result += 'NULL'
                else:
                    result += str(value)
        
        return result

    def begin_transaction(self):
        """开始事务"""
        if self.transaction_count == 0:
            self.driver.begin_transaction()
        self.transaction_count += 1
        return True

    def commit(self):
        """提交事务"""
        if self.transaction_count == 1:
            self.driver.commit()
        
        self.transaction_count = max(0, self.transaction_count - 1)
        return True

    def rollback(self):
        """回滚事务"""
        if self.transaction_count == 1:
            self.driver.rollback()
        
        self.transaction_count = max(0, self.transaction_count - 1)
        return True

    def get_last_query(self):
        """获取最后执行的SQL语句

        Returns:
            str: SQL语句
        """
        return self.last_query

    def get_query_count(self):
        """获取查询次数

        Returns:
            int: 查询次数
        """
        return self.query_count

    def get_query_time(self):
        """获取查询时间

        Returns:
            float: 查询时间（秒）
        """
        return self.query_time