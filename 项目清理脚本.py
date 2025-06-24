#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
项目清理脚本
清理无关进程和临时文件，减少硬件开销
保护重要文件，不删除.docx文件
"""

import os
import glob
import shutil
from datetime import datetime

def clean_project():
    """执行项目清理"""
    print("🧹 开始项目清理...")
    print("=" * 60)
    
    # 清理统计
    cleaned_files = []
    protected_files = []
    
    # 1. 清理Python缓存文件
    print("1. 清理Python缓存文件...")
    cache_patterns = [
        '**/__pycache__',
        '**/*.pyc',
        '**/*.pyo',
        '**/*.pyd'
    ]
    
    for pattern in cache_patterns:
        for path in glob.glob(pattern, recursive=True):
            if os.path.exists(path):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                        print(f"  删除缓存目录: {path}")
                    else:
                        os.remove(path)
                        print(f"  删除缓存文件: {path}")
                    cleaned_files.append(path)
                except Exception as e:
                    print(f"  ⚠️  无法删除 {path}: {e}")
    
    # 2. 清理临时测试文件
    print("\n2. 清理临时测试文件...")
    temp_patterns = [
        'test_*.py',
        '*_test.py',
        'temp_*.py',
        '*.tmp',
        '*.temp'
    ]
    
    # 保护重要的测试文件
    protected_test_files = [
        'test_complete_frontend.py',
        'test_mongo_complete.py',
        'test_frontend_access.py'
    ]
    
    for pattern in temp_patterns:
        for file_path in glob.glob(pattern):
            if os.path.basename(file_path) not in protected_test_files:
                try:
                    os.remove(file_path)
                    print(f"  删除临时文件: {file_path}")
                    cleaned_files.append(file_path)
                except Exception as e:
                    print(f"  ⚠️  无法删除 {file_path}: {e}")
            else:
                protected_files.append(file_path)
                print(f"  保护重要文件: {file_path}")
    
    # 3. 清理日志文件（保留最新的）
    print("\n3. 清理旧日志文件...")
    log_patterns = [
        '*.log',
        'logs/*.log'
    ]
    
    # 保护重要日志文件
    protected_logs = [
        'django.log',
        'scrapy_spider.log'
    ]
    
    for pattern in log_patterns:
        for log_file in glob.glob(pattern):
            if os.path.basename(log_file) not in protected_logs:
                # 检查文件大小，删除大于10MB的日志文件
                try:
                    if os.path.getsize(log_file) > 10 * 1024 * 1024:  # 10MB
                        os.remove(log_file)
                        print(f"  删除大日志文件: {log_file}")
                        cleaned_files.append(log_file)
                    else:
                        protected_files.append(log_file)
                except Exception as e:
                    print(f"  ⚠️  无法处理 {log_file}: {e}")
    
    # 4. 清理重复的文档文件（保护.docx文件）
    print("\n4. 检查重复文档文件...")
    
    # 查找可能的重复文件
    duplicate_patterns = [
        '*_backup.*',
        '*_copy.*',
        '*_old.*',
        '*.bak'
    ]
    
    for pattern in duplicate_patterns:
        for file_path in glob.glob(pattern):
            # 绝对不删除.docx文件
            if not file_path.endswith('.docx'):
                try:
                    os.remove(file_path)
                    print(f"  删除重复文件: {file_path}")
                    cleaned_files.append(file_path)
                except Exception as e:
                    print(f"  ⚠️  无法删除 {file_path}: {e}")
            else:
                protected_files.append(file_path)
                print(f"  🔒 保护.docx文件: {file_path}")
    
    # 5. 清理空目录
    print("\n5. 清理空目录...")
    for root, dirs, files in os.walk('.', topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):  # 空目录
                    os.rmdir(dir_path)
                    print(f"  删除空目录: {dir_path}")
                    cleaned_files.append(dir_path)
            except Exception as e:
                pass  # 忽略无法删除的目录
    
    # 6. 优化媒体文件
    print("\n6. 检查媒体文件...")
    media_dir = 'media'
    if os.path.exists(media_dir):
        for root, dirs, files in os.walk(media_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # 检查大文件（>5MB）
                    if os.path.getsize(file_path) > 5 * 1024 * 1024:
                        print(f"  发现大媒体文件: {file_path} ({os.path.getsize(file_path)/1024/1024:.1f}MB)")
                        # 不自动删除，只报告
                except Exception as e:
                    pass
    
    # 7. 生成清理报告
    print("\n" + "=" * 60)
    print("🎉 项目清理完成！")
    print(f"📊 清理统计:")
    print(f"  - 已清理文件: {len(cleaned_files)}个")
    print(f"  - 保护文件: {len(protected_files)}个")
    
    # 生成详细清理报告
    report_content = f"""# 项目清理报告

## 清理时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 清理统计
- **已清理文件**: {len(cleaned_files)}个
- **保护文件**: {len(protected_files)}个

## 已清理的文件列表
"""
    
    for file in cleaned_files:
        report_content += f"- {file}\n"
    
    report_content += f"""
## 受保护的文件列表
"""
    
    for file in protected_files:
        report_content += f"- {file}\n"
    
    report_content += f"""
## 清理原则
1. ✅ 清理Python缓存文件(__pycache__, *.pyc)
2. ✅ 清理临时测试文件
3. ✅ 清理大日志文件(>10MB)
4. ✅ 清理重复备份文件
5. ✅ 清理空目录
6. 🔒 **绝对保护.docx文件**
7. 🔒 保护重要的测试和日志文件

## 硬件开销优化
- 减少磁盘占用空间
- 清理内存缓存文件
- 优化文件系统性能
- 保持项目结构整洁

---
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # 保存清理报告
    with open('项目清理报告_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n📋 详细清理报告已保存")
    print("\n🔒 重要提醒: 所有.docx文件已受到保护，未被删除")
    
    return len(cleaned_files), len(protected_files)

if __name__ == '__main__':
    try:
        cleaned_count, protected_count = clean_project()
        print(f"\n✅ 清理完成: 清理了{cleaned_count}个文件，保护了{protected_count}个重要文件")
    except Exception as e:
        print(f"\n❌ 清理过程中出现错误: {e}")
        print("请检查文件权限或手动清理")
