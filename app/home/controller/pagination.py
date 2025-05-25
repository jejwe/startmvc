#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分页示例控制器
"""

from startmvc.core.Controller import Controller
from startmvc.core.Pagination import Pagination as PaginationCore
from startmvc.core.Request import Request


class Pagination(Controller):
    """分页示例控制器"""

    def index(self, *args):
        """分页示例首页"""
        # 获取当前页码
        page = int(Request.get('page', 1))
        
        # 创建测试数据
        data = self._create_test_data()
        
        # 创建分页实例
        per_page = 10
        pagination = PaginationCore.paginate(data, per_page, page)
        
        # 渲染视图
        return self.render('pagination/index', {
            'title': '分页示例',
            'items': pagination['items'],
            'pagination': pagination['pagination'],
            'total': len(data),
            'per_page': per_page,
            'current_page': page
        })

    def custom(self, *args):
        """自定义分页示例"""
        # 获取当前页码
        page = int(Request.get('page', 1))
        
        # 创建测试数据
        data = self._create_test_data()
        
        # 创建分页实例
        per_page = 5
        pagination = PaginationCore.paginate(data, per_page, page)
        
        # 渲染视图
        return self.render('pagination/custom', {
            'title': '自定义分页示例',
            'items': pagination['items'],
            'pagination': pagination['pagination'],
            'total': len(data),
            'per_page': per_page,
            'current_page': page
        })

    def simple(self, *args):
        """简单分页示例"""
        # 获取当前页码
        page = int(Request.get('page', 1))
        
        # 创建测试数据
        data = self._create_test_data()
        
        # 创建分页实例
        per_page = 8
        pagination = PaginationCore.paginate(data, per_page, page)
        
        # 渲染视图
        return self.render('pagination/simple', {
            'title': '简单分页示例',
            'items': pagination['items'],
            'pagination': pagination['pagination'],
            'total': len(data),
            'per_page': per_page,
            'current_page': page
        })

    def _create_test_data(self):
        """创建测试数据"""
        data = []
        
        for i in range(1, 101):
            data.append({
                'id': i,
                'title': f'测试标题 {i}',
                'content': f'这是测试内容 {i}，用于演示分页功能。',
                'created_at': '2023-01-01 12:00:00'
            })
        
        return data