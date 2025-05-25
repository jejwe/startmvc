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

class Test(Model):
    """测试模型"""
    
    # 表名
    table = 'test'
    
    def get_data(self):
        """获取测试数据"""
        # 模拟数据，实际应用中应该从数据库获取
        return {
            'id': 3,
            'name': 'Test Data',
            'description': 'This is a test data from TestModel'
        }