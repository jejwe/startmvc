#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

# 分页配置
config = {
    # 页码参数名
    'page_param': 'page',
    
    # 每页记录数参数名
    'page_size_param': 'page_size',
    
    # 默认每页记录数
    'page_size': 10,
    
    # 显示的页码数量
    'num_links': 5,
    
    # 是否显示首页和尾页
    'show_first_last': True,
    
    # 是否显示上一页和下一页
    'show_prev_next': True,
    
    # 是否显示总记录数
    'show_total': True,
    
    # 是否显示每页记录数选择器
    'show_page_size': True,
    
    # 每页记录数选项
    'page_size_options': [10, 20, 50, 100],
    
    # 首页文本
    'first_text': '首页',
    
    # 上一页文本
    'prev_text': '上一页',
    
    # 下一页文本
    'next_text': '下一页',
    
    # 尾页文本
    'last_text': '尾页',
    
    # 总记录数文本
    'total_text': '共 {total} 条记录',
    
    # 每页记录数文本
    'page_size_text': '每页 {page_size} 条',
    
    # 当前页码文本
    'current_page_text': '第 {current_page} 页 / 共 {total_pages} 页',
    
    # 分页链接模板
    'link_template': '<a href="{url}" class="{class_name}">{text}</a>',
    
    # 当前页码模板
    'current_template': '<span class="current">{text}</span>',
    
    # 禁用链接模板
    'disabled_template': '<span class="disabled">{text}</span>',
    
    # 分页容器模板
    'container_template': '<div class="pagination">{links}</div>',
    
    # 每页记录数选择器模板
    'page_size_template': '<select class="page-size" onchange="window.location.href=this.value">{options}</select>',
    
    # 每页记录数选项模板
    'page_size_option_template': '<option value="{url}" {selected}>{text}</option>',
}