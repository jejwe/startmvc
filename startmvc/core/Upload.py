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
import uuid
import shutil
import imghdr
import cherrypy
from PIL import Image

class Upload:
    """
    上传类
    用于处理文件上传
    """
    
    def __init__(self):
        """
        构造函数
        """
        # 上传配置
        self.config = {}
        
        # 上传目录
        self.upload_dir = os.path.join(os.getcwd(), 'static', 'uploads')
        
        # 允许的文件类型
        self.allowed_types = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'zip', 'rar', '7z']
        
        # 最大文件大小（字节）
        self.max_size = 10 * 1024 * 1024  # 10MB
        
        # 是否自动创建目录
        self.auto_create_dir = True
        
        # 是否生成唯一文件名
        self.unique_name = True
        
        # 错误信息
        self.error = ''
    
    def set_config(self, config):
        """
        设置上传配置
        
        Args:
            config: 上传配置
        """
        self.config = config
        
        # 如果配置了上传目录，则使用配置的目录
        if 'path' in config:
            self.upload_dir = config['path']
        
        # 如果配置了允许的文件类型，则使用配置的类型
        if 'allowed_types' in config:
            self.allowed_types = config['allowed_types']
        
        # 如果配置了最大文件大小，则使用配置的大小
        if 'max_size' in config:
            self.max_size = config['max_size']
        
        # 如果配置了是否自动创建目录，则使用配置的值
        if 'auto_create_dir' in config:
            self.auto_create_dir = config['auto_create_dir']
        
        # 如果配置了是否生成唯一文件名，则使用配置的值
        if 'unique_name' in config:
            self.unique_name = config['unique_name']
    
    def upload(self, file_field, sub_dir=None):
        """
        上传文件
        
        Args:
            file_field: 文件字段名
            sub_dir: 子目录
            
        Returns:
            dict: 上传结果
        """
        # 清空错误信息
        self.error = ''
        
        # 获取上传文件
        upload_file = cherrypy.request.params.get(file_field)
        
        # 如果文件不存在，则返回错误
        if not upload_file:
            self.error = f'文件字段 {file_field} 不存在'
            return {'error': self.error}
        
        # 如果文件为空，则返回错误
        if not upload_file.filename:
            self.error = '没有选择文件'
            return {'error': self.error}
        
        # 获取文件信息
        file_name = os.path.basename(upload_file.filename)
        file_ext = os.path.splitext(file_name)[1].lower().lstrip('.')
        
        # 验证文件类型
        if file_ext not in self.allowed_types:
            self.error = f'不允许上传 {file_ext} 类型的文件'
            return {'error': self.error}
        
        # 验证文件大小
        upload_file.file.seek(0, os.SEEK_END)
        file_size = upload_file.file.tell()
        upload_file.file.seek(0)
        
        if file_size > self.max_size:
            self.error = f'文件大小超过限制，最大允许 {self.max_size / 1024 / 1024:.2f}MB'
            return {'error': self.error}
        
        # 确定上传目录
        upload_path = self.upload_dir
        if sub_dir:
            upload_path = os.path.join(upload_path, sub_dir)
        
        # 如果目录不存在且允许自动创建目录，则创建目录
        if not os.path.exists(upload_path):
            if self.auto_create_dir:
                os.makedirs(upload_path, exist_ok=True)
            else:
                self.error = f'上传目录 {upload_path} 不存在'
                return {'error': self.error}
        
        # 生成文件名
        if self.unique_name:
            new_file_name = f"{uuid.uuid4().hex}.{file_ext}"
        else:
            new_file_name = file_name
        
        # 文件保存路径
        file_path = os.path.join(upload_path, new_file_name)
        
        # 保存文件
        try:
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(upload_file.file, f)
        except Exception as e:
            self.error = f'保存文件失败：{str(e)}'
            return {'error': self.error}
        
        # 返回上传结果
        result = {
            'success': True,
            'file_name': new_file_name,
            'original_name': file_name,
            'file_path': file_path,
            'file_size': file_size,
            'file_type': file_ext
        }
        
        # 如果是图片，则获取图片信息
        if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
            try:
                with Image.open(file_path) as img:
                    result['width'] = img.width
                    result['height'] = img.height
                    result['image_type'] = img.format.lower()
            except Exception:
                pass
        
        return result
    
    def upload_multiple(self, file_field, sub_dir=None):
        """
        上传多个文件
        
        Args:
            file_field: 文件字段名
            sub_dir: 子目录
            
        Returns:
            list: 上传结果列表
        """
        # 清空错误信息
        self.error = ''
        
        # 获取上传文件
        upload_files = cherrypy.request.params.get(file_field)
        
        # 如果文件不存在，则返回错误
        if not upload_files:
            self.error = f'文件字段 {file_field} 不存在'
            return {'error': self.error}
        
        # 如果不是列表，则转换为列表
        if not isinstance(upload_files, list):
            upload_files = [upload_files]
        
        # 上传结果
        results = []
        
        # 遍历上传文件
        for upload_file in upload_files:
            # 如果文件为空，则跳过
            if not upload_file.filename:
                continue
            
            # 获取文件信息
            file_name = os.path.basename(upload_file.filename)
            file_ext = os.path.splitext(file_name)[1].lower().lstrip('.')
            
            # 验证文件类型
            if file_ext not in self.allowed_types:
                results.append({
                    'success': False,
                    'error': f'不允许上传 {file_ext} 类型的文件',
                    'original_name': file_name
                })
                continue
            
            # 验证文件大小
            upload_file.file.seek(0, os.SEEK_END)
            file_size = upload_file.file.tell()
            upload_file.file.seek(0)
            
            if file_size > self.max_size:
                results.append({
                    'success': False,
                    'error': f'文件大小超过限制，最大允许 {self.max_size / 1024 / 1024:.2f}MB',
                    'original_name': file_name
                })
                continue
            
            # 确定上传目录
            upload_path = self.upload_dir
            if sub_dir:
                upload_path = os.path.join(upload_path, sub_dir)
            
            # 如果目录不存在且允许自动创建目录，则创建目录
            if not os.path.exists(upload_path):
                if self.auto_create_dir:
                    os.makedirs(upload_path, exist_ok=True)
                else:
                    results.append({
                        'success': False,
                        'error': f'上传目录 {upload_path} 不存在',
                        'original_name': file_name
                    })
                    continue
            
            # 生成文件名
            if self.unique_name:
                new_file_name = f"{uuid.uuid4().hex}.{file_ext}"
            else:
                new_file_name = file_name
            
            # 文件保存路径
            file_path = os.path.join(upload_path, new_file_name)
            
            # 保存文件
            try:
                with open(file_path, 'wb') as f:
                    shutil.copyfileobj(upload_file.file, f)
            except Exception as e:
                results.append({
                    'success': False,
                    'error': f'保存文件失败：{str(e)}',
                    'original_name': file_name
                })
                continue
            
            # 上传结果
            result = {
                'success': True,
                'file_name': new_file_name,
                'original_name': file_name,
                'file_path': file_path,
                'file_size': file_size,
                'file_type': file_ext
            }
            
            # 如果是图片，则获取图片信息
            if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                try:
                    with Image.open(file_path) as img:
                        result['width'] = img.width
                        result['height'] = img.height
                        result['image_type'] = img.format.lower()
                except Exception:
                    pass
            
            # 添加到结果列表
            results.append(result)
        
        return results
    
    def delete(self, file_name, sub_dir=None):
        """
        删除文件
        
        Args:
            file_name: 文件名
            sub_dir: 子目录
            
        Returns:
            bool: 是否成功
        """
        # 清空错误信息
        self.error = ''
        
        # 确定文件路径
        file_path = self.upload_dir
        if sub_dir:
            file_path = os.path.join(file_path, sub_dir)
        file_path = os.path.join(file_path, file_name)
        
        # 如果文件不存在，则返回错误
        if not os.path.exists(file_path):
            self.error = f'文件 {file_path} 不存在'
            return False
        
        # 删除文件
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            self.error = f'删除文件失败：{str(e)}'
            return False
    
    def get_error(self):
        """
        获取错误信息
        
        Returns:
            str: 错误信息
        """
        return self.error
    
    def is_image(self, file_path):
        """
        检查文件是否为图片
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否为图片
        """
        return imghdr.what(file_path) is not None
    
    def resize_image(self, file_path, width=None, height=None, quality=85, output_path=None):
        """
        调整图片大小
        
        Args:
            file_path: 文件路径
            width: 宽度
            height: 高度
            quality: 质量
            output_path: 输出路径
            
        Returns:
            bool: 是否成功
        """
        # 如果文件不存在，则返回错误
        if not os.path.exists(file_path):
            self.error = f'文件 {file_path} 不存在'
            return False
        
        # 如果不是图片，则返回错误
        if not self.is_image(file_path):
            self.error = f'文件 {file_path} 不是图片'
            return False
        
        # 如果未指定输出路径，则覆盖原文件
        if not output_path:
            output_path = file_path
        
        try:
            # 打开图片
            with Image.open(file_path) as img:
                # 获取原始尺寸
                orig_width, orig_height = img.size
                
                # 如果未指定宽度和高度，则返回错误
                if not width and not height:
                    self.error = '必须指定宽度或高度'
                    return False
                
                # 如果只指定了宽度，则按比例计算高度
                if width and not height:
                    height = int(orig_height * width / orig_width)
                
                # 如果只指定了高度，则按比例计算宽度
                if height and not width:
                    width = int(orig_width * height / orig_height)
                
                # 调整图片大小
                resized_img = img.resize((width, height), Image.LANCZOS)
                
                # 保存图片
                resized_img.save(output_path, quality=quality)
                
                return True
        except Exception as e:
            self.error = f'调整图片大小失败：{str(e)}'
            return False
    
    def crop_image(self, file_path, x, y, width, height, output_path=None):
        """
        裁剪图片
        
        Args:
            file_path: 文件路径
            x: 左上角X坐标
            y: 左上角Y坐标
            width: 宽度
            height: 高度
            output_path: 输出路径
            
        Returns:
            bool: 是否成功
        """
        # 如果文件不存在，则返回错误
        if not os.path.exists(file_path):
            self.error = f'文件 {file_path} 不存在'
            return False
        
        # 如果不是图片，则返回错误
        if not self.is_image(file_path):
            self.error = f'文件 {file_path} 不是图片'
            return False
        
        # 如果未指定输出路径，则覆盖原文件
        if not output_path:
            output_path = file_path
        
        try:
            # 打开图片
            with Image.open(file_path) as img:
                # 裁剪图片
                cropped_img = img.crop((x, y, x + width, y + height))
                
                # 保存图片
                cropped_img.save(output_path)
                
                return True
        except Exception as e:
            self.error = f'裁剪图片失败：{str(e)}'
            return False
    
    def watermark(self, file_path, watermark_path, position='center', opacity=50, output_path=None):
        """
        添加水印
        
        Args:
            file_path: 文件路径
            watermark_path: 水印图片路径
            position: 水印位置
            opacity: 水印透明度
            output_path: 输出路径
            
        Returns:
            bool: 是否成功
        """
        # 如果文件不存在，则返回错误
        if not os.path.exists(file_path):
            self.error = f'文件 {file_path} 不存在'
            return False
        
        # 如果水印文件不存在，则返回错误
        if not os.path.exists(watermark_path):
            self.error = f'水印文件 {watermark_path} 不存在'
            return False
        
        # 如果不是图片，则返回错误
        if not self.is_image(file_path):
            self.error = f'文件 {file_path} 不是图片'
            return False
        
        # 如果水印不是图片，则返回错误
        if not self.is_image(watermark_path):
            self.error = f'水印文件 {watermark_path} 不是图片'
            return False
        
        # 如果未指定输出路径，则覆盖原文件
        if not output_path:
            output_path = file_path
        
        try:
            # 打开图片
            with Image.open(file_path) as img:
                # 打开水印图片
                with Image.open(watermark_path) as watermark:
                    # 调整水印透明度
                    if watermark.mode != 'RGBA':
                        watermark = watermark.convert('RGBA')
                    
                    # 创建透明图层
                    alpha = Image.new('RGBA', watermark.size, (0, 0, 0, 0))
                    
                    # 设置透明度
                    alpha_value = int(255 * opacity / 100)
                    
                    # 合并图层
                    watermark = Image.blend(alpha, watermark, alpha_value / 255)
                    
                    # 计算水印位置
                    if position == 'top-left':
                        position = (0, 0)
                    elif position == 'top-right':
                        position = (img.width - watermark.width, 0)
                    elif position == 'bottom-left':
                        position = (0, img.height - watermark.height)
                    elif position == 'bottom-right':
                        position = (img.width - watermark.width, img.height - watermark.height)
                    else:  # center
                        position = ((img.width - watermark.width) // 2, (img.height - watermark.height) // 2)
                    
                    # 如果图片不是RGBA模式，则转换
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    # 创建新图片
                    new_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
                    
                    # 粘贴原图
                    new_img.paste(img, (0, 0))
                    
                    # 粘贴水印
                    new_img.paste(watermark, position, watermark)
                    
                    # 保存图片
                    new_img.save(output_path)
                    
                    return True
        except Exception as e:
            self.error = f'添加水印失败：{str(e)}'
            return False