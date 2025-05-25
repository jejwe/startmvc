#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

import math
import cherrypy

class Pagination:
    """
    分页类
    用于数据分页
    """
    
    def __init__(self, total, page_size=10, current_page=1, url=None, query_string=None):
        """
        构造函数
        
        Args:
            total: 总记录数
            page_size: 每页记录数
            current_page: 当前页码
            url: 分页URL
            query_string: 查询字符串
        """
        # 总记录数
        self.total = max(0, int(total))
        
        # 每页记录数
        self.page_size = max(1, int(page_size))
        
        # 总页数
        self.total_pages = max(1, math.ceil(self.total / self.page_size))
        
        # 当前页码
        self.current_page = max(1, min(int(current_page), self.total_pages))
        
        # 分页URL
        self.url = url or cherrypy.request.path_info
        
        # 查询字符串
        self.query_string = query_string or {}
        
        # 显示的页码数量
        self.num_links = 5
        
        # 是否显示首页和尾页
        self.show_first_last = True
        
        # 是否显示上一页和下一页
        self.show_prev_next = True
        
        # 是否显示总记录数
        self.show_total = True
        
        # 是否显示每页记录数选择器
        self.show_page_size = True
        
        # 每页记录数选项
        self.page_size_options = [10, 20, 50, 100]
        
        # 分页参数名
        self.page_param = 'page'
        
        # 每页记录数参数名
        self.page_size_param = 'page_size'
        
        # 首页文本
        self.first_text = '首页'
        
        # 上一页文本
        self.prev_text = '上一页'
        
        # 下一页文本
        self.next_text = '下一页'
        
        # 尾页文本
        self.last_text = '尾页'
        
        # 总记录数文本
        self.total_text = '共 {total} 条记录'
        
        # 每页记录数文本
        self.page_size_text = '每页 {page_size} 条'
        
        # 当前页码文本
        self.current_page_text = '第 {current_page} 页 / 共 {total_pages} 页'
        
        # 分页链接模板
        self.link_template = '<a href="{url}" class="{class_name}">{text}</a>'
        
        # 当前页码模板
        self.current_template = '<span class="current">{text}</span>'
        
        # 禁用链接模板
        self.disabled_template = '<span class="disabled">{text}</span>'
        
        # 分页容器模板
        self.container_template = '<div class="pagination">{links}</div>'
        
        # 每页记录数选择器模板
        self.page_size_template = '<select class="page-size" onchange="window.location.href=this.value">{options}</select>'
        
        # 每页记录数选项模板
        self.page_size_option_template = '<option value="{url}" {selected}>{text}</option>'
    
    def get_offset(self):
        """
        获取偏移量
        
        Returns:
            int: 偏移量
        """
        return (self.current_page - 1) * self.page_size
    
    def get_limit(self):
        """
        获取限制数
        
        Returns:
            int: 限制数
        """
        return self.page_size
    
    def has_previous(self):
        """
        是否有上一页
        
        Returns:
            bool: 是否有上一页
        """
        return self.current_page > 1
    
    def has_next(self):
        """
        是否有下一页
        
        Returns:
            bool: 是否有下一页
        """
        return self.current_page < self.total_pages
    
    def previous_page(self):
        """
        上一页页码
        
        Returns:
            int: 上一页页码
        """
        return max(1, self.current_page - 1)
    
    def next_page(self):
        """
        下一页页码
        
        Returns:
            int: 下一页页码
        """
        return min(self.total_pages, self.current_page + 1)
    
    def get_page_range(self):
        """
        获取页码范围
        
        Returns:
            list: 页码范围
        """
        # 计算页码范围
        start = max(1, self.current_page - self.num_links // 2)
        end = min(self.total_pages, start + self.num_links - 1)
        
        # 如果页码范围不足，则调整起始页码
        if end - start + 1 < self.num_links:
            start = max(1, end - self.num_links + 1)
        
        return list(range(start, end + 1))
    
    def get_page_url(self, page, page_size=None):
        """
        获取页码URL
        
        Args:
            page: 页码
            page_size: 每页记录数
            
        Returns:
            str: 页码URL
        """
        # 复制查询字符串
        query = self.query_string.copy()
        
        # 设置页码参数
        query[self.page_param] = page
        
        # 设置每页记录数参数
        if page_size:
            query[self.page_size_param] = page_size
        elif self.page_size_param in query:
            query[self.page_size_param] = self.page_size
        
        # 构建查询字符串
        query_str = '&'.join([f"{k}={v}" for k, v in query.items()])
        
        # 返回URL
        if query_str:
            return f"{self.url}?{query_str}"
        else:
            return self.url
    
    def render(self):
        """
        渲染分页
        
        Returns:
            str: 分页HTML
        """
        # 如果总页数为1，则不显示分页
        if self.total_pages <= 1 and not self.show_total and not self.show_page_size:
            return ''
        
        # 分页链接
        links = []
        
        # 显示总记录数
        if self.show_total:
            links.append(self.disabled_template.format(
                text=self.total_text.format(total=self.total)
            ))
        
        # 显示当前页码
        links.append(self.disabled_template.format(
            text=self.current_page_text.format(
                current_page=self.current_page,
                total_pages=self.total_pages
            )
        ))
        
        # 显示首页
        if self.show_first_last and self.current_page > 1:
            links.append(self.link_template.format(
                url=self.get_page_url(1),
                class_name='first',
                text=self.first_text
            ))
        
        # 显示上一页
        if self.show_prev_next and self.has_previous():
            links.append(self.link_template.format(
                url=self.get_page_url(self.previous_page()),
                class_name='prev',
                text=self.prev_text
            ))
        
        # 显示页码
        for page in self.get_page_range():
            if page == self.current_page:
                links.append(self.current_template.format(
                    text=page
                ))
            else:
                links.append(self.link_template.format(
                    url=self.get_page_url(page),
                    class_name='page',
                    text=page
                ))
        
        # 显示下一页
        if self.show_prev_next and self.has_next():
            links.append(self.link_template.format(
                url=self.get_page_url(self.next_page()),
                class_name='next',
                text=self.next_text
            ))
        
        # 显示尾页
        if self.show_first_last and self.current_page < self.total_pages:
            links.append(self.link_template.format(
                url=self.get_page_url(self.total_pages),
                class_name='last',
                text=self.last_text
            ))
        
        # 显示每页记录数选择器
        if self.show_page_size:
            # 每页记录数选项
            options = []
            
            # 遍历每页记录数选项
            for page_size in self.page_size_options:
                # 是否选中
                selected = 'selected' if page_size == self.page_size else ''
                
                # 添加选项
                options.append(self.page_size_option_template.format(
                    url=self.get_page_url(1, page_size),
                    selected=selected,
                    text=self.page_size_text.format(page_size=page_size)
                ))
            
            # 添加每页记录数选择器
            links.append(self.page_size_template.format(
                options=''.join(options)
            ))
        
        # 返回分页HTML
        return self.container_template.format(
            links=''.join(links)
        )
    
    def __str__(self):
        """
        字符串表示
        
        Returns:
            str: 分页HTML
        """
        return self.render()
    
    def to_dict(self):
        """
        转换为字典
        
        Returns:
            dict: 分页信息
        """
        return {
            'total': self.total,
            'page_size': self.page_size,
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'has_previous': self.has_previous(),
            'has_next': self.has_next(),
            'previous_page': self.previous_page(),
            'next_page': self.next_page(),
            'page_range': self.get_page_range(),
            'offset': self.get_offset(),
            'limit': self.get_limit()
        }