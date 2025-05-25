#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StartMVC超轻量级Python开发框架

@author    Shao Bing QQ858292510 (Python port by OpenHands)
@copyright Copyright (c) 2020-2025
@license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
@link      http://startmvc.com
"""

import os
import yaml
import json
import importlib
from dotenv import load_dotenv

class Config:
    """
    配置类
    用于管理配置
    """
    
    def __init__(self):
        """
        构造函数
        """
        # 配置数据
        self.data = {}
        
        # 加载环境变量
        load_dotenv()
    
    def load(self, file_path):
        """
        加载配置文件
        
        Args:
            file_path: 配置文件路径
            
        Returns:
            Config: 配置对象
        """
        # 如果文件不存在，则返回
        if not os.path.exists(file_path):
            return self
        
        # 获取文件扩展名
        ext = os.path.splitext(file_path)[1].lower()
        
        # 根据文件扩展名加载配置
        if ext == '.py':
            self._load_python(file_path)
        elif ext == '.json':
            self._load_json(file_path)
        elif ext in ['.yaml', '.yml']:
            self._load_yaml(file_path)
        
        return self
    
    def load_dir(self, dir_path):
        """
        加载配置目录
        
        Args:
            dir_path: 配置目录路径
            
        Returns:
            Config: 配置对象
        """
        # 如果目录不存在，则返回
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            return self
        
        # 遍历目录
        for file_name in os.listdir(dir_path):
            # 获取文件路径
            file_path = os.path.join(dir_path, file_name)
            
            # 如果是文件，则加载配置
            if os.path.isfile(file_path):
                # 获取文件扩展名
                ext = os.path.splitext(file_name)[1].lower()
                
                # 如果是配置文件，则加载
                if ext in ['.py', '.json', '.yaml', '.yml']:
                    self.load(file_path)
        
        return self
    
    def get(self, key, default=None):
        """
        获取配置
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            mixed: 配置值
        """
        # 如果键包含点号，则按层级获取
        if '.' in key:
            # 分割键
            keys = key.split('.')
            
            # 获取配置值
            value = self.data
            
            # 遍历键
            for k in keys:
                # 如果键不存在，则返回默认值
                if not isinstance(value, dict) or k not in value:
                    return default
                
                # 获取下一级配置值
                value = value[k]
            
            return value
        
        # 如果键不存在，则返回默认值
        if key not in self.data:
            return default
        
        # 返回配置值
        return self.data[key]
    
    def set(self, key, value):
        """
        设置配置
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            Config: 配置对象
        """
        # 如果键包含点号，则按层级设置
        if '.' in key:
            # 分割键
            keys = key.split('.')
            
            # 获取配置值
            config = self.data
            
            # 遍历键
            for i, k in enumerate(keys):
                # 如果是最后一个键，则设置值
                if i == len(keys) - 1:
                    config[k] = value
                    break
                
                # 如果键不存在，则创建空字典
                if k not in config:
                    config[k] = {}
                
                # 如果值不是字典，则创建空字典
                if not isinstance(config[k], dict):
                    config[k] = {}
                
                # 获取下一级配置值
                config = config[k]
        else:
            # 设置配置值
            self.data[key] = value
        
        return self
    
    def has(self, key):
        """
        检查配置是否存在
        
        Args:
            key: 配置键
            
        Returns:
            bool: 是否存在
        """
        # 如果键包含点号，则按层级检查
        if '.' in key:
            # 分割键
            keys = key.split('.')
            
            # 获取配置值
            value = self.data
            
            # 遍历键
            for k in keys:
                # 如果键不存在，则返回False
                if not isinstance(value, dict) or k not in value:
                    return False
                
                # 获取下一级配置值
                value = value[k]
            
            return True
        
        # 检查键是否存在
        return key in self.data
    
    def delete(self, key):
        """
        删除配置
        
        Args:
            key: 配置键
            
        Returns:
            Config: 配置对象
        """
        # 如果键包含点号，则按层级删除
        if '.' in key:
            # 分割键
            keys = key.split('.')
            
            # 获取配置值
            value = self.data
            
            # 遍历键
            for i, k in enumerate(keys):
                # 如果键不存在，则返回
                if not isinstance(value, dict) or k not in value:
                    return self
                
                # 如果是最后一个键，则删除
                if i == len(keys) - 1:
                    del value[k]
                    return self
                
                # 获取下一级配置值
                value = value[k]
        else:
            # 如果键存在，则删除
            if key in self.data:
                del self.data[key]
        
        return self
    
    def all(self):
        """
        获取所有配置
        
        Returns:
            dict: 所有配置
        """
        return self.data
    
    def merge(self, config):
        """
        合并配置
        
        Args:
            config: 配置对象或字典
            
        Returns:
            Config: 配置对象
        """
        # 如果是配置对象，则获取配置数据
        if isinstance(config, Config):
            config = config.all()
        
        # 如果不是字典，则返回
        if not isinstance(config, dict):
            return self
        
        # 合并配置
        self._merge_dict(self.data, config)
        
        return self
    
    def _merge_dict(self, target, source):
        """
        合并字典
        
        Args:
            target: 目标字典
            source: 源字典
        """
        # 遍历源字典
        for key, value in source.items():
            # 如果键不存在，则直接设置
            if key not in target:
                target[key] = value
                continue
            
            # 如果值是字典，则递归合并
            if isinstance(value, dict) and isinstance(target[key], dict):
                self._merge_dict(target[key], value)
            else:
                # 否则直接覆盖
                target[key] = value
    
    def _load_python(self, file_path):
        """
        加载Python配置文件
        
        Args:
            file_path: 配置文件路径
        """
        try:
            # 获取模块名
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # 获取模块目录
            module_dir = os.path.dirname(file_path)
            
            # 将模块目录添加到系统路径
            import sys
            sys.path.insert(0, module_dir)
            
            # 导入模块
            module = importlib.import_module(module_name)
            
            # 从模块中获取配置
            for key in dir(module):
                # 跳过私有属性
                if key.startswith('_'):
                    continue
                
                # 获取属性值
                value = getattr(module, key)
                
                # 如果是配置，则添加到配置数据
                if isinstance(value, (dict, list, str, int, float, bool, type(None))):
                    self.data[key] = value
            
            # 如果模块中有config变量，则合并到配置数据
            if hasattr(module, 'config') and isinstance(module.config, dict):
                self._merge_dict(self.data, module.config)
            
            # 从系统路径中移除模块目录
            sys.path.remove(module_dir)
        except Exception as e:
            print(f"加载Python配置文件失败：{str(e)}")
    
    def _load_json(self, file_path):
        """
        加载JSON配置文件
        
        Args:
            file_path: 配置文件路径
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                # 解析JSON
                config = json.load(f)
                
                # 合并配置
                self._merge_dict(self.data, config)
        except Exception as e:
            print(f"加载JSON配置文件失败：{str(e)}")
    
    def _load_yaml(self, file_path):
        """
        加载YAML配置文件
        
        Args:
            file_path: 配置文件路径
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                # 解析YAML
                config = yaml.safe_load(f)
                
                # 合并配置
                self._merge_dict(self.data, config)
        except Exception as e:
            print(f"加载YAML配置文件失败：{str(e)}")
    
    def __getitem__(self, key):
        """
        获取配置
        
        Args:
            key: 配置键
            
        Returns:
            mixed: 配置值
        """
        return self.get(key)
    
    def __setitem__(self, key, value):
        """
        设置配置
        
        Args:
            key: 配置键
            value: 配置值
        """
        self.set(key, value)
    
    def __contains__(self, key):
        """
        检查配置是否存在
        
        Args:
            key: 配置键
            
        Returns:
            bool: 是否存在
        """
        return self.has(key)
    
    def __delitem__(self, key):
        """
        删除配置
        
        Args:
            key: 配置键
        """
        self.delete(key)