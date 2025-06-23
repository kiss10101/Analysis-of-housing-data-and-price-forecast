#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复MongoDB模板文件中的图片路径问题
"""

import os
import re
import glob

def fix_template_file(file_path):
    """修复单个模板文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复各种图片路径问题
        patterns = [
            # 修复缺少引号的src属性
            (r'src=/media/\{\{\s*([^}]+)\s*\}\}', r'src="/media/{{ \1|default:\'user/avatar/default.png\' }}"'),
            # 修复已有引号但缺少默认值的
            (r'src="/media/\{\{\s*([^}|]+)\s*\}\}"', r'src="/media/{{ \1|default:\'user/avatar/default.png\' }}"'),
            # 修复已有引号但缺少默认值的（带safe过滤器）
            (r'src="/media/\{\{\s*([^}|]+)\s*\|\s*safe\s*\}\}"', r'src="/media/{{ \1|default:\'user/avatar/default.png\' }}"'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # 如果内容有变化，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 修复了文件: {file_path}")
            return True
        else:
            print(f"ℹ️  文件无需修复: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 修复文件失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    print("🔧 批量修复MongoDB模板文件中的图片路径问题")
    print("=" * 60)
    
    # 查找所有MongoDB模板文件
    mongo_templates = glob.glob("templates/mongo/*.html")
    
    if not mongo_templates:
        print("❌ 未找到MongoDB模板文件")
        return
    
    print(f"📁 找到 {len(mongo_templates)} 个MongoDB模板文件")
    print()
    
    fixed_count = 0
    total_count = len(mongo_templates)
    
    for template_file in mongo_templates:
        if fix_template_file(template_file):
            fixed_count += 1
    
    print()
    print("=" * 60)
    print(f"📊 修复结果: {fixed_count}/{total_count} 个文件已修复")
    
    if fixed_count > 0:
        print("🎉 图片路径问题修复完成！")
        print("💡 建议重启Django服务器以应用更改")
    else:
        print("✅ 所有文件都已正确配置")

if __name__ == "__main__":
    main()
