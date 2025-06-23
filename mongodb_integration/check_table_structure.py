#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查MySQL表结构
"""

import pymysql

def check_table_structure():
    """检查表结构"""
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='guangzhou_house'
        )
        cursor = conn.cursor()
        
        # 检查House表结构
        print("House表结构:")
        cursor.execute('DESCRIBE House')
        for row in cursor.fetchall():
            print(f"  {row[0]} - {row[1]}")
        
        print("\nHouse_scrapy表结构:")
        cursor.execute('DESCRIBE House_scrapy')
        for row in cursor.fetchall():
            print(f"  {row[0]} - {row[1]}")
        
        # 查看House表的样本数据
        print("\nHouse表样本数据:")
        cursor.execute('SELECT * FROM House LIMIT 2')
        columns = [desc[0] for desc in cursor.description]
        print(f"字段: {columns}")
        
        for row in cursor.fetchall():
            print(f"数据: {row}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == '__main__':
    check_table_structure()
