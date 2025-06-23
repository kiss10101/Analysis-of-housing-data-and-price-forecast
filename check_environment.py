#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
环境检查脚本
检查Python和Django版本以及必要的包是否已安装
"""

import sys
import platform
import socket
import os
import importlib.util
import subprocess
import traceback

def check_python_version():
    """检查Python版本"""
    print(f"Python版本: {platform.python_version()}")
    major, minor, _ = platform.python_version_tuple()

    if int(major) < 3 or (int(major) == 3 and int(minor) < 6):
        print("警告: 建议使用Python 3.6或更高版本")
        return False
    return True

def check_django():
    """检查Django是否已安装及版本"""
    try:
        if importlib.util.find_spec("django"):
            import django
            print(f"Django版本: {django.get_version()}")
            return True
        else:
            print("错误: Django未安装")
            return False
    except Exception as e:
        print(f"检查Django时出错: {e}")
        return False

def check_port(port=8127):
    """检查端口是否可用"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
        print(f"端口{port}可用")
        result = True
    except socket.error:
        print(f"警告: 端口{port}已被占用")
        result = False
    finally:
        s.close()
    return result

def check_required_packages():
    """检查必要的Python包是否已安装"""
    required_packages = [
        ("django", "Django"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("matplotlib", "matplotlib"),
        ("sklearn", "scikit-learn")  # scikit-learn的导入名是sklearn
    ]

    missing_packages = []

    for import_name, display_name in required_packages:
        if not importlib.util.find_spec(import_name):
            missing_packages.append(display_name)

    if missing_packages:
        print(f"错误: 以下必要的包未安装: {', '.join(missing_packages)}")
        return False
    else:
        print("所有必要的包已安装")
        return True

def check_manage_py():
    """检查manage.py文件是否存在"""
    # 检查当前目录
    if os.path.exists("manage.py"):
        print("找到manage.py文件")
        return True

    # 检查父目录
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.exists(os.path.join(parent_dir, "manage.py")):
        print("在父目录中找到manage.py文件")
        return True

    # 搜索子目录
    for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(__file__))):
        if "manage.py" in files:
            print(f"在{root}中找到manage.py文件")
            return True

    print("错误: 找不到manage.py文件")
    return False

def main():
    """主函数"""
    print("-" * 40)
    print("开始环境检查")
    print("-" * 40)

    all_checks_passed = True

    # 检查Python版本
    if not check_python_version():
        all_checks_passed = False

    # 检查Django
    if not check_django():
        all_checks_passed = False

    # 检查端口
    if not check_port():
        all_checks_passed = False

    # 检查必要的包
    if not check_required_packages():
        all_checks_passed = False

    # 检查manage.py文件
    if not check_manage_py():
        all_checks_passed = False

    print("-" * 40)
    if all_checks_passed:
        print("环境检查通过！")
        return 0
    else:
        print("环境检查未通过，请根据上述提示重新配置系统。")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"运行环境检查时发生错误: {e}")
        traceback.print_exc()
        sys.exit(1)