#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建favicon.ico文件
"""

from PIL import Image, ImageDraw

def create_favicon():
    """创建简单的favicon.ico文件"""
    
    # 创建32x32的图像
    size = 32
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # 绘制一个简单的房子图标
    # 房子主体
    draw.rectangle([8, 16, 24, 28], fill='#4CAF50', outline='#2E7D32', width=1)
    
    # 屋顶
    draw.polygon([(6, 16), (16, 8), (26, 16)], fill='#FF5722', outline='#D84315', width=1)
    
    # 门
    draw.rectangle([12, 20, 16, 28], fill='#8D6E63', outline='#5D4037', width=1)
    
    # 窗户
    draw.rectangle([18, 18, 22, 22], fill='#2196F3', outline='#1976D2', width=1)
    
    # 保存为ICO格式
    image.save('static/favicon.ico', format='ICO', sizes=[(32, 32)])
    print("✅ favicon.ico 已创建: static/favicon.ico")
    
    # 同时在根目录创建一个副本
    image.save('favicon.ico', format='ICO', sizes=[(32, 32)])
    print("✅ favicon.ico 已创建: favicon.ico")

if __name__ == "__main__":
    print("🎨 创建favicon.ico文件...")
    try:
        create_favicon()
        print("🎉 favicon.ico创建完成！")
    except ImportError:
        print("❌ 需要安装Pillow库: pip install Pillow")
    except Exception as e:
        print(f"❌ 创建favicon.ico时出错: {e}")
