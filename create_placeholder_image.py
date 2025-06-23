#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建占位图片文件
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_placeholder_image():
    """创建占位图片"""
    
    # 创建media目录（如果不存在）
    media_dir = "media"
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
    
    # 创建一个简单的占位图片
    width, height = 200, 150
    image = Image.new('RGB', (width, height), color='#f0f0f0')
    draw = ImageDraw.Draw(image)
    
    # 绘制边框
    draw.rectangle([0, 0, width-1, height-1], outline='#cccccc', width=2)
    
    # 添加文字
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        # 如果没有找到字体，使用默认字体
        font = ImageFont.load_default()
    
    text = "Placeholder Image"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    
    draw.text((text_x, text_y), text, fill='#666666', font=font)
    
    # 保存图片
    image_path = os.path.join(media_dir, "8gSGjmP9Ugowbgd.png")
    image.save(image_path, "PNG")
    
    print(f"✅ 占位图片已创建: {image_path}")
    return image_path

def create_default_avatar():
    """创建默认头像"""
    
    # 创建用户头像目录
    avatar_dir = os.path.join("media", "user", "avatar")
    if not os.path.exists(avatar_dir):
        os.makedirs(avatar_dir)
    
    # 创建默认头像
    size = 100
    image = Image.new('RGB', (size, size), color='#4CAF50')
    draw = ImageDraw.Draw(image)
    
    # 绘制圆形头像
    draw.ellipse([10, 10, size-10, size-10], fill='#81C784', outline='#2E7D32', width=3)
    
    # 添加用户图标（简单的圆形和矩形）
    # 头部
    draw.ellipse([35, 25, 65, 55], fill='#FFFFFF')
    # 身体
    draw.rectangle([30, 50, 70, 85], fill='#FFFFFF')
    
    # 保存默认头像
    avatar_path = os.path.join(avatar_dir, "default.png")
    image.save(avatar_path, "PNG")
    
    print(f"✅ 默认头像已创建: {avatar_path}")
    return avatar_path

if __name__ == "__main__":
    print("🖼️  创建占位图片文件...")
    
    try:
        # 创建占位图片
        placeholder_path = create_placeholder_image()
        
        # 创建默认头像
        avatar_path = create_default_avatar()
        
        print("\n✅ 所有占位图片创建完成！")
        print(f"占位图片: {placeholder_path}")
        print(f"默认头像: {avatar_path}")
        
    except ImportError:
        print("❌ 需要安装Pillow库: pip install Pillow")
    except Exception as e:
        print(f"❌ 创建图片时出错: {e}")
