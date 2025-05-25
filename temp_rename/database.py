#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库示例控制器
"""

from startmvc.core.Controller import Controller
from startmvc.core.Db import Db


class Database(Controller):
    """数据库示例控制器"""

    def index(self, *args):
        """数据库示例首页"""
        # 获取数据库实例
        db = Db.connect()
        
        # 创建测试表
        self._create_test_table(db)
        
        # 插入测试数据
        self._insert_test_data(db)
        
        # 查询数据
        data = db.table('test').get()
        
        # 渲染视图
        return self.render('database/index', {
            'title': '数据库示例',
            'data': data
        })

    def query(self, *args):
        """查询示例"""
        # 获取数据库实例
        db = Db.connect()
        
        # 查询数据
        data = db.table('test').fields('id, name, age, email').where('age', '>', 20).order('id', 'desc').get()
        
        # 渲染视图
        return self.render('database/query', {
            'title': '查询示例',
            'data': data,
            'sql': db.get_last_query()
        })

    def find(self, *args):
        """查询单条记录示例"""
        # 获取数据库实例
        db = Db.connect()
        
        # 查询单条记录
        data = db.table('test').where('id', 1).first()
        
        # 渲染视图
        return self.render('database/find', {
            'title': '查询单条记录示例',
            'data': data,
            'sql': db.get_last_query()
        })

    def insert(self, *args):
        """插入示例"""
        # 获取数据库实例
        db = Db.connect()
        
        # 插入数据
        data = {
            'name': 'New User',
            'age': 30,
            'email': 'newuser@example.com',
            'created_at': db.raw('CURRENT_TIMESTAMP')
        }
        
        result = db.table('test').insert(data)
        
        # 渲染视图
        return self.render('database/insert', {
            'title': '插入示例',
            'result': result,
            'last_insert_id': db.driver.get_last_insert_id(),
            'sql': db.get_last_query()
        })

    def update(self, *args):
        """更新示例"""
        # 获取数据库实例
        db = Db.connect()
        
        # 更新数据
        data = {
            'name': 'Updated User',
            'age': 35,
            'updated_at': db.raw('CURRENT_TIMESTAMP')
        }
        
        result = db.table('test').where('id', 1).update(data)
        
        # 渲染视图
        return self.render('database/update', {
            'title': '更新示例',
            'result': result,
            'sql': db.get_last_query()
        })

    def delete(self, *args):
        """删除示例"""
        # 获取数据库实例
        db = Db.connect()
        
        # 删除数据
        result = db.table('test').where('id', '>', 3).delete()
        
        # 渲染视图
        return self.render('database/delete', {
            'title': '删除示例',
            'result': result,
            'sql': db.get_last_query()
        })

    def transaction(self, *args):
        """事务示例"""
        # 获取数据库实例
        db = Db.connect()
        
        # 开始事务
        db.begin_transaction()
        
        try:
            # 插入数据
            db.table('test').insert({
                'name': 'Transaction User 1',
                'age': 40,
                'email': 'transaction1@example.com',
                'created_at': db.raw('CURRENT_TIMESTAMP')
            })
            
            db.table('test').insert({
                'name': 'Transaction User 2',
                'age': 45,
                'email': 'transaction2@example.com',
                'created_at': db.raw('CURRENT_TIMESTAMP')
            })
            
            # 提交事务
            db.commit()
            
            success = True
            message = '事务提交成功'
        except Exception as e:
            # 回滚事务
            db.rollback()
            
            success = False
            message = f'事务回滚: {str(e)}'
        
        # 查询数据
        data = db.table('test').get()
        
        # 渲染视图
        return self.render('database/transaction', {
            'title': '事务示例',
            'success': success,
            'message': message,
            'data': data
        })

    def _create_test_table(self, db):
        """创建测试表"""
        # 检查表是否存在
        if not db.driver.table_exists('test'):
            # 创建表
            sql = """
            CREATE TABLE test (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL,
                age INTEGER NOT NULL,
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
            """
            
            db.driver.execute(sql)

    def _insert_test_data(self, db):
        """插入测试数据"""
        # 检查表是否有数据
        count = db.table('test').count()
        
        if count == 0:
            # 插入测试数据
            data = [
                {
                    'name': 'John Doe',
                    'age': 25,
                    'email': 'john@example.com'
                },
                {
                    'name': 'Jane Smith',
                    'age': 30,
                    'email': 'jane@example.com'
                },
                {
                    'name': 'Bob Johnson',
                    'age': 20,
                    'email': 'bob@example.com'
                }
            ]
            
            for item in data:
                db.table('test').insert(item)