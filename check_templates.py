#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查所有MongoDB模板文件中的default过滤器语法
"""

import os
import re

def check_templates():
    """检查模板文件"""
    print("🔍 检查MongoDB模板文件中的default过滤器语法")
    print("=" * 60)
    
    template_dir = "templates/mongo"
    
    # 查找所有HTML文件
    html_files = []
    for file in os.listdir(template_dir):
        if file.endswith('.html'):
            html_files.append(os.path.join(template_dir, file))
    
    print(f"找到 {len(html_files)} 个模板文件")
    print()
    
    # 检查每个文件
    issues_found = 0
    
    for file_path in html_files:
        print(f"📄 检查文件: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # 查找可能有问题的default过滤器
            for line_num, line in enumerate(lines, 1):
                # 查找转义的单引号语法
                if r"default:\'" in line:
                    print(f"  ❌ 第{line_num}行: 发现转义单引号语法")
                    print(f"     {line.strip()}")
                    issues_found += 1
                
                # 查找其他可能的问题
                if "default:" in line and ("\\'" in line or "\\\\" in line):
                    print(f"  ⚠️ 第{line_num}行: 可能的语法问题")
                    print(f"     {line.strip()}")
                    issues_found += 1
            
            if "default:" not in content:
                print("  ✅ 未使用default过滤器")
            elif issues_found == 0:
                print("  ✅ default过滤器语法正常")
                
        except Exception as e:
            print(f"  ❌ 读取文件失败: {e}")
        
        print()
    
    print("=" * 60)
    if issues_found > 0:
        print(f"❌ 发现 {issues_found} 个语法问题需要修复")
    else:
        print("✅ 所有模板文件语法正常")

if __name__ == '__main__':
    check_templates()
