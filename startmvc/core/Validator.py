#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

import re
import os
import datetime
from functools import wraps

class Validator:
    """
    验证器类
    用于验证数据
    """
    
    def __init__(self):
        """
        构造函数
        """
        # 验证规则
        self.rules = {}
        
        # 验证消息
        self.messages = {}
        
        # 验证数据
        self.data = {}
        
        # 验证错误
        self.errors = {}
        
        # 验证字段别名
        self.aliases = {}
        
        # 验证场景
        self.scene = None
        
        # 场景规则
        self.scene_rules = {}
    
    def set_rules(self, rules):
        """
        设置验证规则
        
        Args:
            rules: 验证规则
            
        Returns:
            Validator: 验证器对象
        """
        self.rules = rules
        return self
    
    def set_messages(self, messages):
        """
        设置验证消息
        
        Args:
            messages: 验证消息
            
        Returns:
            Validator: 验证器对象
        """
        self.messages = messages
        return self
    
    def set_aliases(self, aliases):
        """
        设置字段别名
        
        Args:
            aliases: 字段别名
            
        Returns:
            Validator: 验证器对象
        """
        self.aliases = aliases
        return self
    
    def set_scene(self, scene):
        """
        设置验证场景
        
        Args:
            scene: 验证场景
            
        Returns:
            Validator: 验证器对象
        """
        self.scene = scene
        return self
    
    def set_scene_rules(self, scene_rules):
        """
        设置场景规则
        
        Args:
            scene_rules: 场景规则
            
        Returns:
            Validator: 验证器对象
        """
        self.scene_rules = scene_rules
        return self
    
    def validate(self, data):
        """
        验证数据
        
        Args:
            data: 验证数据
            
        Returns:
            bool: 是否验证通过
        """
        # 设置验证数据
        self.data = data
        
        # 清空验证错误
        self.errors = {}
        
        # 获取验证规则
        rules = self._get_scene_rules()
        
        # 验证数据
        for field, rule in rules.items():
            # 如果字段不存在，则跳过
            if field not in data and 'required' not in rule:
                continue
            
            # 获取字段值
            value = data.get(field, None)
            
            # 验证字段
            self._validate_field(field, value, rule)
        
        # 返回验证结果
        return len(self.errors) == 0
    
    def get_errors(self):
        """
        获取验证错误
        
        Returns:
            dict: 验证错误
        """
        return self.errors
    
    def get_first_error(self):
        """
        获取第一个验证错误
        
        Returns:
            str: 验证错误
        """
        if self.errors:
            for field, errors in self.errors.items():
                if errors:
                    return errors[0]
        return ''
    
    def _get_scene_rules(self):
        """
        获取场景规则
        
        Returns:
            dict: 场景规则
        """
        # 如果未设置场景，则返回所有规则
        if not self.scene:
            return self.rules
        
        # 如果场景不存在，则返回空规则
        if self.scene not in self.scene_rules:
            return {}
        
        # 获取场景字段
        scene_fields = self.scene_rules[self.scene]
        
        # 场景规则
        scene_rules = {}
        
        # 遍历所有规则
        for field, rule in self.rules.items():
            # 如果字段在场景中，则添加规则
            if field in scene_fields:
                scene_rules[field] = rule
        
        return scene_rules
    
    def _validate_field(self, field, value, rule):
        """
        验证字段
        
        Args:
            field: 字段名
            value: 字段值
            rule: 验证规则
        """
        # 如果规则是字符串，则转换为列表
        if isinstance(rule, str):
            rule = rule.split('|')
        
        # 遍历规则
        for r in rule:
            # 如果规则是字符串，则解析规则
            if isinstance(r, str):
                # 解析规则
                rule_name, rule_params = self._parse_rule(r)
            else:
                # 如果规则是字典，则获取规则名和参数
                rule_name = r.get('rule')
                rule_params = r.get('params', [])
            
            # 获取验证方法
            validate_method = getattr(self, f'validate_{rule_name}', None)
            
            # 如果验证方法不存在，则跳过
            if not validate_method:
                continue
            
            # 验证字段
            result = validate_method(field, value, rule_params)
            
            # 如果验证失败，则添加错误
            if not result:
                self._add_error(field, rule_name, rule_params)
                break
    
    def _parse_rule(self, rule):
        """
        解析规则
        
        Args:
            rule: 规则字符串
            
        Returns:
            tuple: (规则名, 规则参数)
        """
        # 如果规则包含参数
        if ':' in rule:
            # 分割规则名和参数
            rule_name, params_str = rule.split(':', 1)
            
            # 解析参数
            params = params_str.split(',')
            
            return rule_name, params
        
        # 如果规则不包含参数
        return rule, []
    
    def _add_error(self, field, rule, params):
        """
        添加验证错误
        
        Args:
            field: 字段名
            rule: 规则名
            params: 规则参数
        """
        # 获取字段别名
        field_name = self.aliases.get(field, field)
        
        # 获取错误消息
        message = self._get_error_message(field, rule, params)
        
        # 替换消息中的占位符
        message = message.replace('{field}', field_name)
        
        # 替换参数占位符
        for i, param in enumerate(params):
            message = message.replace(f'{{{i}}}', str(param))
        
        # 添加错误
        if field not in self.errors:
            self.errors[field] = []
        
        self.errors[field].append(message)
    
    def _get_error_message(self, field, rule, params):
        """
        获取错误消息
        
        Args:
            field: 字段名
            rule: 规则名
            params: 规则参数
            
        Returns:
            str: 错误消息
        """
        # 尝试获取字段特定的错误消息
        message = self.messages.get(f'{field}.{rule}')
        
        # 如果字段特定的错误消息不存在，则尝试获取规则特定的错误消息
        if not message:
            message = self.messages.get(rule)
        
        # 如果规则特定的错误消息不存在，则使用默认错误消息
        if not message:
            message = self._get_default_message(rule, params)
        
        return message
    
    def _get_default_message(self, rule, params):
        """
        获取默认错误消息
        
        Args:
            rule: 规则名
            params: 规则参数
            
        Returns:
            str: 默认错误消息
        """
        # 默认错误消息
        default_messages = {
            'required': '{field}不能为空',
            'email': '{field}必须是有效的电子邮件地址',
            'url': '{field}必须是有效的URL',
            'ip': '{field}必须是有效的IP地址',
            'number': '{field}必须是数字',
            'integer': '{field}必须是整数',
            'float': '{field}必须是浮点数',
            'boolean': '{field}必须是布尔值',
            'array': '{field}必须是数组',
            'date': '{field}必须是有效的日期',
            'time': '{field}必须是有效的时间',
            'datetime': '{field}必须是有效的日期时间',
            'alpha': '{field}只能包含字母',
            'alpha_num': '{field}只能包含字母和数字',
            'alpha_dash': '{field}只能包含字母、数字、破折号和下划线',
            'regex': '{field}格式不正确',
            'min': '{field}不能小于{0}',
            'max': '{field}不能大于{0}',
            'between': '{field}必须在{0}和{1}之间',
            'min_length': '{field}长度不能小于{0}',
            'max_length': '{field}长度不能大于{0}',
            'length': '{field}长度必须为{0}',
            'length_between': '{field}长度必须在{0}和{1}之间',
            'in': '{field}必须在指定的值中',
            'not_in': '{field}不能在指定的值中',
            'unique': '{field}已存在',
            'exists': '{field}不存在',
            'confirmed': '{field}两次输入不一致',
            'accepted': '{field}必须接受',
            'file': '{field}必须是文件',
            'image': '{field}必须是图片',
            'mimes': '{field}必须是指定的文件类型',
            'mime_types': '{field}必须是指定的文件类型',
            'dimensions': '{field}图片尺寸不正确',
            'size': '{field}大小不能超过{0}',
            'uploaded': '{field}上传失败',
            'distinct': '{field}包含重复的值',
            'timezone': '{field}必须是有效的时区',
            'json': '{field}必须是有效的JSON字符串',
            'phone': '{field}必须是有效的电话号码',
            'idcard': '{field}必须是有效的身份证号码',
            'password': '{field}必须包含大小写字母和数字',
            'same': '{field}必须与{0}相同',
            'different': '{field}不能与{0}相同',
            'gt': '{field}必须大于{0}',
            'gte': '{field}必须大于等于{0}',
            'lt': '{field}必须小于{0}',
            'lte': '{field}必须小于等于{0}',
            'after': '{field}必须在{0}之后',
            'after_or_equal': '{field}必须在{0}之后或等于{0}',
            'before': '{field}必须在{0}之前',
            'before_or_equal': '{field}必须在{0}之前或等于{0}',
        }
        
        # 返回默认错误消息
        return default_messages.get(rule, '{field}验证失败')
    
    # 验证方法
    
    def validate_required(self, field, value, params):
        """
        验证必填
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if value is None:
            return False
        
        if isinstance(value, str) and value.strip() == '':
            return False
        
        return True
    
    def validate_email(self, field, value, params):
        """
        验证电子邮件
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))
    
    def validate_url(self, field, value, params):
        """
        验证URL
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        pattern = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, value))
    
    def validate_ip(self, field, value, params):
        """
        验证IP地址
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        # IPv4
        ipv4_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
        ipv4_match = re.match(ipv4_pattern, value)
        if ipv4_match:
            for i in range(1, 5):
                if int(ipv4_match.group(i)) > 255:
                    return False
            return True
        
        # IPv6
        ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        return bool(re.match(ipv6_pattern, value))
    
    def validate_number(self, field, value, params):
        """
        验证数字
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def validate_integer(self, field, value, params):
        """
        验证整数
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def validate_float(self, field, value, params):
        """
        验证浮点数
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        try:
            float(value)
            return isinstance(float(value), float)
        except (ValueError, TypeError):
            return False
    
    def validate_boolean(self, field, value, params):
        """
        验证布尔值
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        return value in [True, False, 0, 1, '0', '1', 'true', 'false', 'True', 'False']
    
    def validate_array(self, field, value, params):
        """
        验证数组
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        return isinstance(value, (list, tuple))
    
    def validate_date(self, field, value, params):
        """
        验证日期
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        try:
            if isinstance(value, str):
                datetime.datetime.strptime(value, '%Y-%m-%d')
            elif isinstance(value, datetime.date):
                pass
            else:
                return False
            return True
        except ValueError:
            return False
    
    def validate_time(self, field, value, params):
        """
        验证时间
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        try:
            if isinstance(value, str):
                datetime.datetime.strptime(value, '%H:%M:%S')
            elif isinstance(value, datetime.time):
                pass
            else:
                return False
            return True
        except ValueError:
            return False
    
    def validate_datetime(self, field, value, params):
        """
        验证日期时间
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        try:
            if isinstance(value, str):
                datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            elif isinstance(value, datetime.datetime):
                pass
            else:
                return False
            return True
        except ValueError:
            return False
    
    def validate_alpha(self, field, value, params):
        """
        验证字母
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        return bool(re.match(r'^[a-zA-Z]+$', str(value)))
    
    def validate_alpha_num(self, field, value, params):
        """
        验证字母和数字
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        return bool(re.match(r'^[a-zA-Z0-9]+$', str(value)))
    
    def validate_alpha_dash(self, field, value, params):
        """
        验证字母、数字、破折号和下划线
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', str(value)))
    
    def validate_regex(self, field, value, params):
        """
        验证正则表达式
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        if not params:
            return False
        
        pattern = params[0]
        return bool(re.match(pattern, str(value)))
    
    def validate_min(self, field, value, params):
        """
        验证最小值
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        if not params:
            return False
        
        min_value = float(params[0])
        
        try:
            return float(value) >= min_value
        except (ValueError, TypeError):
            return False
    
    def validate_max(self, field, value, params):
        """
        验证最大值
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        if not params:
            return False
        
        max_value = float(params[0])
        
        try:
            return float(value) <= max_value
        except (ValueError, TypeError):
            return False
    
    def validate_between(self, field, value, params):
        """
        验证值在范围内
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        if len(params) < 2:
            return False
        
        min_value = float(params[0])
        max_value = float(params[1])
        
        try:
            return min_value <= float(value) <= max_value
        except (ValueError, TypeError):
            return False
    
    def validate_min_length(self, field, value, params):
        """
        验证最小长度
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        if not params:
            return False
        
        min_length = int(params[0])
        
        return len(str(value)) >= min_length
    
    def validate_max_length(self, field, value, params):
        """
        验证最大长度
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        if not params:
            return False
        
        max_length = int(params[0])
        
        return len(str(value)) <= max_length
    
    def validate_length(self, field, value, params):
        """
        验证长度
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        if not params:
            return False
        
        length = int(params[0])
        
        return len(str(value)) == length
    
    def validate_length_between(self, field, value, params):
        """
        验证长度在范围内
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        if len(params) < 2:
            return False
        
        min_length = int(params[0])
        max_length = int(params[1])
        
        return min_length <= len(str(value)) <= max_length
    
    def validate_in(self, field, value, params):
        """
        验证值在列表中
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        if not params:
            return False
        
        return str(value) in params
    
    def validate_not_in(self, field, value, params):
        """
        验证值不在列表中
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        if not params:
            return False
        
        return str(value) not in params
    
    def validate_confirmed(self, field, value, params):
        """
        验证确认字段
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        # 确认字段名
        confirmed_field = f'{field}_confirmation'
        
        # 如果确认字段不存在，则验证失败
        if confirmed_field not in self.data:
            return False
        
        # 获取确认字段值
        confirmed_value = self.data.get(confirmed_field)
        
        # 验证两个字段值是否相同
        return value == confirmed_value
    
    def validate_same(self, field, value, params):
        """
        验证两个字段值相同
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        if not params:
            return False
        
        # 比较字段名
        other_field = params[0]
        
        # 如果比较字段不存在，则验证失败
        if other_field not in self.data:
            return False
        
        # 获取比较字段值
        other_value = self.data.get(other_field)
        
        # 验证两个字段值是否相同
        return value == other_value
    
    def validate_different(self, field, value, params):
        """
        验证两个字段值不同
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        if not params:
            return False
        
        # 比较字段名
        other_field = params[0]
        
        # 如果比较字段不存在，则验证通过
        if other_field not in self.data:
            return True
        
        # 获取比较字段值
        other_value = self.data.get(other_field)
        
        # 验证两个字段值是否不同
        return value != other_value
    
    def validate_accepted(self, field, value, params):
        """
        验证接受
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        return value in [True, 1, '1', 'yes', 'on', 'true', 'True']
    
    def validate_file(self, field, value, params):
        """
        验证文件
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        # 如果是字符串，则验证文件是否存在
        if isinstance(value, str):
            return os.path.isfile(value)
        
        # 如果是文件对象，则验证是否有文件名
        if hasattr(value, 'filename'):
            return bool(value.filename)
        
        return False
    
    def validate_image(self, field, value, params):
        """
        验证图片
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        # 图片扩展名
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        
        # 如果是字符串，则验证文件扩展名
        if isinstance(value, str):
            # 验证文件是否存在
            if not os.path.isfile(value):
                return False
            
            # 获取文件扩展名
            ext = os.path.splitext(value)[1].lower().lstrip('.')
            
            # 验证文件扩展名
            return ext in image_extensions
        
        # 如果是文件对象，则验证文件扩展名
        if hasattr(value, 'filename'):
            # 获取文件扩展名
            ext = os.path.splitext(value.filename)[1].lower().lstrip('.')
            
            # 验证文件扩展名
            return ext in image_extensions
        
        return False
    
    def validate_mimes(self, field, value, params):
        """
        验证文件MIME类型
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        if not params:
            return False
        
        # 如果是字符串，则验证文件扩展名
        if isinstance(value, str):
            # 验证文件是否存在
            if not os.path.isfile(value):
                return False
            
            # 获取文件扩展名
            ext = os.path.splitext(value)[1].lower().lstrip('.')
            
            # 验证文件扩展名
            return ext in params
        
        # 如果是文件对象，则验证文件扩展名
        if hasattr(value, 'filename'):
            # 获取文件扩展名
            ext = os.path.splitext(value.filename)[1].lower().lstrip('.')
            
            # 验证文件扩展名
            return ext in params
        
        return False
    
    def validate_size(self, field, value, params):
        """
        验证文件大小
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        if not params:
            return False
        
        # 最大文件大小（字节）
        max_size = int(params[0])
        
        # 如果是字符串，则验证文件大小
        if isinstance(value, str):
            # 验证文件是否存在
            if not os.path.isfile(value):
                return False
            
            # 获取文件大小
            file_size = os.path.getsize(value)
            
            # 验证文件大小
            return file_size <= max_size
        
        # 如果是文件对象，则验证文件大小
        if hasattr(value, 'file'):
            # 获取文件大小
            value.file.seek(0, os.SEEK_END)
            file_size = value.file.tell()
            value.file.seek(0)
            
            # 验证文件大小
            return file_size <= max_size
        
        return False
    
    def validate_phone(self, field, value, params):
        """
        验证电话号码
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        # 电话号码正则表达式
        pattern = r'^1[3-9]\d{9}$'
        
        return bool(re.match(pattern, str(value)))
    
    def validate_idcard(self, field, value, params):
        """
        验证身份证号码
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        # 身份证号码正则表达式
        pattern = r'^\d{17}[\dXx]$'
        
        # 验证格式
        if not re.match(pattern, str(value)):
            return False
        
        # 验证校验码
        factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        checksums = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        
        # 计算校验码
        checksum = 0
        for i in range(17):
            checksum += int(value[i]) * factors[i]
        
        # 验证校验码
        return value[17].upper() == checksums[checksum % 11]
    
    def validate_password(self, field, value, params):
        """
        验证密码
        
        Args:
            field: 字段名
            value: 字段值
            params: 规则参数
            
        Returns:
            bool: 是否验证通过
        """
        if not value:
            return True
        
        # 密码必须包含大小写字母和数字
        return (
            re.search(r'[A-Z]', str(value)) and
            re.search(r'[a-z]', str(value)) and
            re.search(r'[0-9]', str(value))
        )


def validate(rules=None, messages=None, aliases=None):
    """
    验证装饰器
    用于验证控制器方法的参数
    
    Args:
        rules: 验证规则
        messages: 验证消息
        aliases: 字段别名
        
    Returns:
        function: 装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # 创建验证器
            validator = Validator()
            
            # 设置验证规则
            if rules:
                validator.set_rules(rules)
            
            # 设置验证消息
            if messages:
                validator.set_messages(messages)
            
            # 设置字段别名
            if aliases:
                validator.set_aliases(aliases)
            
            # 获取请求数据
            data = {}
            
            # 合并GET参数
            if hasattr(self, 'request') and hasattr(self.request, 'params'):
                data.update(self.request.params)
            
            # 合并POST参数
            if hasattr(self, 'request') and hasattr(self.request, 'form'):
                data.update(self.request.form)
            
            # 合并JSON参数
            if hasattr(self, 'request') and hasattr(self.request, 'json'):
                data.update(self.request.json)
            
            # 验证数据
            if not validator.validate(data):
                # 获取验证错误
                errors = validator.get_errors()
                
                # 如果控制器有处理验证错误的方法，则调用
                if hasattr(self, 'validation_failed'):
                    return self.validation_failed(errors)
                
                # 否则返回第一个错误
                return {'error': validator.get_first_error(), 'errors': errors}
            
            # 验证通过，调用原方法
            return func(self, *args, **kwargs)
        return wrapper
    return decorator