#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据迁移测试脚本
测试MySQL到MongoDB的数据迁移方案
"""

import os
import sys
import json
import time
from datetime import datetime
import pymysql
import pymongo
from pymongo import MongoClient
import pandas as pd
from tqdm import tqdm


class DataMigrationTest:
    def __init__(self):
        # MySQL配置
        self.mysql_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '123456',
            'database': 'guangzhou_house',
            'charset': 'utf8mb4'
        }
        
        # MongoDB配置
        self.mongo_uri = "mongodb://localhost:27017/"
        self.mongo_db = "house_migration_test"
        self.mongo_collection = "houses_migrated"
        
        self.mysql_conn = None
        self.mongo_client = None
        self.mongo_db_obj = None
        self.mongo_collection_obj = None
        
        self.test_results = {
            'test_time': datetime.now().isoformat(),
            'mysql_connection': {},
            'mongodb_connection': {},
            'data_extraction': {},
            'data_transformation': {},
            'data_loading': {},
            'validation': {},
            'performance': {}
        }
    
    def connect_mysql(self):
        """连接MySQL"""
        print("🔍 连接MySQL数据库...")
        
        try:
            start_time = time.time()
            self.mysql_conn = pymysql.connect(**self.mysql_config)
            connection_time = time.time() - start_time
            
            # 测试查询
            cursor = self.mysql_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM house")
            count = cursor.fetchone()[0]
            cursor.close()
            
            self.test_results['mysql_connection'] = {
                'success': True,
                'connection_time': connection_time,
                'total_records': count
            }
            
            print(f"✅ MySQL连接成功 (总记录数: {count})")
            return True
            
        except Exception as e:
            self.test_results['mysql_connection'] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ MySQL连接失败: {e}")
            return False
    
    def connect_mongodb(self):
        """连接MongoDB"""
        print("🔍 连接MongoDB数据库...")
        
        try:
            start_time = time.time()
            self.mongo_client = MongoClient(self.mongo_uri)
            self.mongo_db_obj = self.mongo_client[self.mongo_db]
            self.mongo_collection_obj = self.mongo_db_obj[self.mongo_collection]
            
            # 测试连接
            self.mongo_client.admin.command('ping')
            connection_time = time.time() - start_time
            
            # 清空测试集合
            self.mongo_collection_obj.delete_many({})
            
            self.test_results['mongodb_connection'] = {
                'success': True,
                'connection_time': connection_time
            }
            
            print(f"✅ MongoDB连接成功")
            return True
            
        except Exception as e:
            self.test_results['mongodb_connection'] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ MongoDB连接失败: {e}")
            return False
    
    def extract_data(self, limit=None):
        """从MySQL提取数据"""
        print("🔍 从MySQL提取数据...")
        
        if not self.mysql_conn:
            print("❌ MySQL未连接")
            return None
        
        try:
            start_time = time.time()
            
            # 构建查询
            query = "SELECT * FROM house"
            if limit:
                query += f" LIMIT {limit}"
            
            # 使用pandas读取数据
            df = pd.read_sql(query, self.mysql_conn)
            
            extraction_time = time.time() - start_time
            
            self.test_results['data_extraction'] = {
                'success': True,
                'extraction_time': extraction_time,
                'record_count': len(df),
                'columns': list(df.columns)
            }
            
            print(f"✅ 数据提取完成 ({len(df)}条记录, {extraction_time:.2f}秒)")
            return df
            
        except Exception as e:
            self.test_results['data_extraction'] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ 数据提取失败: {e}")
            return None
    
    def transform_data(self, df):
        """数据转换"""
        print("🔍 转换数据格式...")
        
        if df is None:
            return None
        
        try:
            start_time = time.time()
            
            # 数据转换逻辑
            transformed_data = []
            
            for _, row in df.iterrows():
                # 基本字段映射
                doc = {
                    'title': row.get('title', ''),
                    'type': row.get('type', ''),
                    'building': row.get('building', ''),
                    'city': row.get('city', ''),
                    'street': row.get('street', ''),
                    'area': float(row.get('area', 0)) if row.get('area') else 0.0,
                    'direct': row.get('direct', ''),
                    'price': float(row.get('price', 0)) if row.get('price') else 0.0,
                    'link': row.get('link', ''),
                    'tag': row.get('tag', ''),
                    'img': row.get('img', ''),
                }
                
                # 扩展字段（MongoDB优势）
                doc.update({
                    'location': {
                        'lat': 0.0,  # 可以通过地址解析获取
                        'lng': 0.0
                    },
                    'facilities': [],  # 可以从描述中提取
                    'description': f"{doc['type']} {doc['title']} {doc['building']}",
                    'contact_info': {},
                    'migration_time': datetime.now().isoformat(),
                    'source': 'mysql_migration',
                    'original_id': int(row.get('id', 0)) if row.get('id') else None
                })
                
                # 数据清洗
                if doc['price'] > 0 and doc['area'] > 0:
                    doc['price_per_sqm'] = doc['price'] / doc['area']
                else:
                    doc['price_per_sqm'] = 0.0
                
                # 分类标签
                if doc['price'] < 2000:
                    doc['price_category'] = 'low'
                elif doc['price'] < 5000:
                    doc['price_category'] = 'medium'
                else:
                    doc['price_category'] = 'high'
                
                transformed_data.append(doc)
            
            transformation_time = time.time() - start_time
            
            self.test_results['data_transformation'] = {
                'success': True,
                'transformation_time': transformation_time,
                'record_count': len(transformed_data),
                'sample_document': transformed_data[0] if transformed_data else {}
            }
            
            print(f"✅ 数据转换完成 ({len(transformed_data)}条记录, {transformation_time:.2f}秒)")
            return transformed_data
            
        except Exception as e:
            self.test_results['data_transformation'] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ 数据转换失败: {e}")
            return None
    
    def load_data(self, data, batch_size=1000):
        """加载数据到MongoDB"""
        print("🔍 加载数据到MongoDB...")
        
        if not data or not self.mongo_collection_obj:
            print("❌ 数据或MongoDB连接无效")
            return False
        
        try:
            start_time = time.time()
            
            # 批量插入
            total_inserted = 0
            
            for i in tqdm(range(0, len(data), batch_size), desc="插入数据"):
                batch = data[i:i + batch_size]
                result = self.mongo_collection_obj.insert_many(batch)
                total_inserted += len(result.inserted_ids)
            
            loading_time = time.time() - start_time
            
            self.test_results['data_loading'] = {
                'success': True,
                'loading_time': loading_time,
                'total_inserted': total_inserted,
                'insertion_rate': total_inserted / loading_time if loading_time > 0 else 0,
                'batch_size': batch_size
            }
            
            print(f"✅ 数据加载完成 ({total_inserted}条记录, {loading_time:.2f}秒)")
            return True
            
        except Exception as e:
            self.test_results['data_loading'] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ 数据加载失败: {e}")
            return False
    
    def validate_migration(self):
        """验证迁移结果"""
        print("🔍 验证迁移结果...")
        
        try:
            # 统计MongoDB中的记录数
            mongo_count = self.mongo_collection_obj.count_documents({})
            
            # 统计MySQL中的记录数
            cursor = self.mysql_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM house")
            mysql_count = cursor.fetchone()[0]
            cursor.close()
            
            # 数据一致性检查
            sample_docs = list(self.mongo_collection_obj.find().limit(5))
            
            # 聚合查询测试
            pipeline = [
                {'$group': {
                    '_id': '$city',
                    'avg_price': {'$avg': '$price'},
                    'count': {'$sum': 1}
                }},
                {'$sort': {'avg_price': -1}}
            ]
            agg_result = list(self.mongo_collection_obj.aggregate(pipeline))
            
            self.test_results['validation'] = {
                'success': True,
                'mysql_count': mysql_count,
                'mongodb_count': mongo_count,
                'data_consistency': mongo_count == mysql_count,
                'sample_documents': len(sample_docs),
                'aggregation_test': len(agg_result) > 0,
                'aggregation_result': agg_result[:3]  # 前3个结果
            }
            
            print(f"✅ 迁移验证完成 (MySQL: {mysql_count}, MongoDB: {mongo_count})")
            return True
            
        except Exception as e:
            self.test_results['validation'] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ 迁移验证失败: {e}")
            return False
    
    def performance_comparison(self):
        """性能对比测试"""
        print("🔍 进行性能对比测试...")
        
        try:
            # MySQL查询性能
            start_time = time.time()
            cursor = self.mysql_conn.cursor()
            cursor.execute("SELECT city, AVG(price) as avg_price FROM house GROUP BY city ORDER BY avg_price DESC")
            mysql_results = cursor.fetchall()
            cursor.close()
            mysql_time = time.time() - start_time
            
            # MongoDB查询性能
            start_time = time.time()
            pipeline = [
                {'$group': {
                    '_id': '$city',
                    'avg_price': {'$avg': '$price'}
                }},
                {'$sort': {'avg_price': -1}}
            ]
            mongo_results = list(self.mongo_collection_obj.aggregate(pipeline))
            mongo_time = time.time() - start_time
            
            self.test_results['performance'] = {
                'mysql_query_time': mysql_time,
                'mongodb_query_time': mongo_time,
                'performance_ratio': mysql_time / mongo_time if mongo_time > 0 else 0,
                'mysql_result_count': len(mysql_results),
                'mongodb_result_count': len(mongo_results)
            }
            
            print(f"✅ 性能对比完成 (MySQL: {mysql_time:.3f}s, MongoDB: {mongo_time:.3f}s)")
            return True
            
        except Exception as e:
            self.test_results['performance'] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ 性能对比失败: {e}")
            return False
    
    def generate_report(self):
        """生成迁移测试报告"""
        report_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        os.makedirs(report_dir, exist_ok=True)
        
        # JSON报告
        json_file = os.path.join(report_dir, 'data_migration_test.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        # Markdown报告
        md_file = os.path.join(report_dir, 'data_migration_test.md')
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_markdown_report())
        
        print(f"📄 数据迁移测试报告已生成: {md_file}")
    
    def generate_markdown_report(self):
        """生成Markdown报告"""
        extract = self.test_results.get('data_extraction', {})
        transform = self.test_results.get('data_transformation', {})
        load = self.test_results.get('data_loading', {})
        validate = self.test_results.get('validation', {})
        perf = self.test_results.get('performance', {})
        
        report = f"""# 数据迁移测试报告

## 测试时间
{self.test_results['test_time']}

## 迁移流程

### 数据提取 (MySQL)
- **状态**: {'✅ 成功' if extract.get('success') else '❌ 失败'}
- **提取时间**: {extract.get('extraction_time', 0):.2f} 秒
- **记录数量**: {extract.get('record_count', 0)} 条

### 数据转换
- **状态**: {'✅ 成功' if transform.get('success') else '❌ 失败'}
- **转换时间**: {transform.get('transformation_time', 0):.2f} 秒
- **处理记录**: {transform.get('record_count', 0)} 条

### 数据加载 (MongoDB)
- **状态**: {'✅ 成功' if load.get('success') else '❌ 失败'}
- **加载时间**: {load.get('loading_time', 0):.2f} 秒
- **插入速度**: {load.get('insertion_rate', 0):.0f} 条/秒

## 验证结果
- **数据一致性**: {'✅ 一致' if validate.get('data_consistency') else '❌ 不一致'}
- **MySQL记录数**: {validate.get('mysql_count', 0)}
- **MongoDB记录数**: {validate.get('mongodb_count', 0)}

## 性能对比
- **MySQL查询时间**: {perf.get('mysql_query_time', 0):.3f} 秒
- **MongoDB查询时间**: {perf.get('mongodb_query_time', 0):.3f} 秒
- **性能比率**: {perf.get('performance_ratio', 0):.2f}x

## 结论
{'数据迁移测试成功，可以进行实际迁移' if all([extract.get('success'), transform.get('success'), load.get('success'), validate.get('success')]) else '需要解决迁移过程中的问题'}

## 建议
1. 使用批量插入提高迁移效率
2. 建立数据验证机制确保一致性
3. 考虑增量迁移策略
4. 建立回滚方案
"""
        return report
    
    def run_full_test(self, limit=1000):
        """运行完整迁移测试"""
        print("🚀 开始数据迁移测试...")
        
        # 连接数据库
        if not self.connect_mysql() or not self.connect_mongodb():
            print("❌ 数据库连接失败")
            return False
        
        # 提取数据
        df = self.extract_data(limit)
        if df is None:
            print("❌ 数据提取失败")
            return False
        
        # 转换数据
        transformed_data = self.transform_data(df)
        if transformed_data is None:
            print("❌ 数据转换失败")
            return False
        
        # 加载数据
        if not self.load_data(transformed_data):
            print("❌ 数据加载失败")
            return False
        
        # 验证迁移
        self.validate_migration()
        
        # 性能对比
        self.performance_comparison()
        
        # 生成报告
        self.generate_report()
        
        # 清理连接
        if self.mysql_conn:
            self.mysql_conn.close()
        if self.mongo_client:
            self.mongo_client.close()
        
        print("✅ 数据迁移测试完成!")
        return True


if __name__ == "__main__":
    test = DataMigrationTest()
    test.run_full_test(limit=500)  # 测试500条记录
