#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MongoDB集成测试脚本
测试Django与MongoDB的集成方案
"""

import os
import sys
import json
import time
from datetime import datetime
import pymongo
from pymongo import MongoClient
import pandas as pd


class MongoDBIntegrationTest:
    def __init__(self):
        self.mongo_uri = "mongodb://localhost:27017/"
        self.db_name = "house_validation"
        self.collection_name = "houses_test"
        self.client = None
        self.db = None
        self.collection = None
        self.test_results = {
            'test_time': datetime.now().isoformat(),
            'connection_test': {},
            'crud_test': {},
            'performance_test': {},
            'django_integration': {}
        }
        
    def test_connection(self):
        """测试MongoDB连接"""
        print("🔍 测试MongoDB连接...")
        
        try:
            start_time = time.time()
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            
            # 测试连接
            self.client.admin.command('ping')
            
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            
            connection_time = time.time() - start_time
            
            self.test_results['connection_test'] = {
                'success': True,
                'connection_time': connection_time,
                'server_info': self.client.server_info()['version']
            }
            
            print(f"✅ MongoDB连接成功 (耗时: {connection_time:.3f}秒)")
            return True
            
        except Exception as e:
            self.test_results['connection_test'] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ MongoDB连接失败: {e}")
            return False
    
    def test_crud_operations(self):
        """测试CRUD操作"""
        print("🔍 测试MongoDB CRUD操作...")
        
        if not self.collection:
            print("❌ 未连接到MongoDB")
            return False
        
        try:
            # 清空测试集合
            self.collection.delete_many({})
            
            # 测试数据
            test_data = [
                {
                    'title': '测试房源1',
                    'type': '整租',
                    'building': '测试小区A',
                    'city': '天河',
                    'street': '测试街道',
                    'area': 80.5,
                    'direct': '南',
                    'price': 3500.0,
                    'location': {'lat': 23.1291, 'lng': 113.2644},
                    'facilities': ['地铁', '商场', '学校'],
                    'crawl_time': datetime.now().isoformat()
                },
                {
                    'title': '测试房源2',
                    'type': '合租',
                    'building': '测试小区B',
                    'city': '海珠',
                    'street': '测试路',
                    'area': 60.0,
                    'direct': '北',
                    'price': 2800.0,
                    'location': {'lat': 23.1051, 'lng': 113.3240},
                    'facilities': ['公园', '医院'],
                    'crawl_time': datetime.now().isoformat()
                }
            ]
            
            # 插入测试
            start_time = time.time()
            insert_result = self.collection.insert_many(test_data)
            insert_time = time.time() - start_time
            
            # 查询测试
            start_time = time.time()
            find_result = list(self.collection.find({}))
            query_time = time.time() - start_time
            
            # 更新测试
            start_time = time.time()
            update_result = self.collection.update_one(
                {'title': '测试房源1'},
                {'$set': {'price': 3600.0}}
            )
            update_time = time.time() - start_time
            
            # 聚合查询测试
            start_time = time.time()
            pipeline = [
                {'$group': {
                    '_id': '$city',
                    'avg_price': {'$avg': '$price'},
                    'count': {'$sum': 1}
                }}
            ]
            agg_result = list(self.collection.aggregate(pipeline))
            agg_time = time.time() - start_time
            
            # 删除测试
            start_time = time.time()
            delete_result = self.collection.delete_one({'title': '测试房源2'})
            delete_time = time.time() - start_time
            
            self.test_results['crud_test'] = {
                'success': True,
                'insert_count': len(insert_result.inserted_ids),
                'insert_time': insert_time,
                'query_count': len(find_result),
                'query_time': query_time,
                'update_count': update_result.modified_count,
                'update_time': update_time,
                'aggregation_time': agg_time,
                'aggregation_result': agg_result,
                'delete_count': delete_result.deleted_count,
                'delete_time': delete_time
            }
            
            print(f"✅ CRUD操作测试完成")
            return True
            
        except Exception as e:
            self.test_results['crud_test'] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ CRUD操作测试失败: {e}")
            return False
    
    def test_performance(self, record_count=1000):
        """测试性能"""
        print(f"🔍 测试MongoDB性能 ({record_count}条记录)...")
        
        if not self.collection:
            print("❌ 未连接到MongoDB")
            return False
        
        try:
            # 清空集合
            self.collection.delete_many({})
            
            # 生成测试数据
            test_data = []
            for i in range(record_count):
                test_data.append({
                    'title': f'房源{i}',
                    'type': '整租' if i % 2 == 0 else '合租',
                    'city': ['天河', '海珠', '越秀', '荔湾'][i % 4],
                    'price': 2000 + (i % 100) * 50,
                    'area': 50 + (i % 50) * 2,
                    'crawl_time': datetime.now().isoformat()
                })
            
            # 批量插入测试
            start_time = time.time()
            self.collection.insert_many(test_data)
            insert_time = time.time() - start_time
            
            # 查询性能测试
            start_time = time.time()
            count = self.collection.count_documents({})
            count_time = time.time() - start_time
            
            # 条件查询测试
            start_time = time.time()
            filtered = list(self.collection.find({'price': {'$gte': 3000}}))
            filter_time = time.time() - start_time
            
            # 聚合性能测试
            start_time = time.time()
            pipeline = [
                {'$group': {
                    '_id': '$city',
                    'avg_price': {'$avg': '$price'},
                    'max_price': {'$max': '$price'},
                    'min_price': {'$min': '$price'},
                    'count': {'$sum': 1}
                }},
                {'$sort': {'avg_price': -1}}
            ]
            agg_result = list(self.collection.aggregate(pipeline))
            agg_time = time.time() - start_time
            
            self.test_results['performance_test'] = {
                'success': True,
                'record_count': record_count,
                'insert_time': insert_time,
                'insert_rate': record_count / insert_time,
                'count_time': count_time,
                'filter_time': filter_time,
                'filter_count': len(filtered),
                'aggregation_time': agg_time,
                'aggregation_result': agg_result
            }
            
            print(f"✅ 性能测试完成 (插入速度: {record_count/insert_time:.0f} 条/秒)")
            return True
            
        except Exception as e:
            self.test_results['performance_test'] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ 性能测试失败: {e}")
            return False
    
    def test_django_integration(self):
        """测试Django集成方案"""
        print("🔍 测试Django-MongoDB集成...")
        
        try:
            # 测试mongoengine
            try:
                import mongoengine
                from mongoengine import Document, StringField, FloatField, DateTimeField
                
                # 连接MongoDB
                mongoengine.connect(self.db_name, host=self.mongo_uri)
                
                # 定义模型
                class HouseModel(Document):
                    title = StringField(max_length=200, required=True)
                    city = StringField(max_length=100)
                    price = FloatField()
                    crawl_time = DateTimeField()
                    
                    meta = {'collection': 'houses_mongoengine_test'}
                
                # 测试模型操作
                house = HouseModel(
                    title='Django测试房源',
                    city='天河',
                    price=3000.0,
                    crawl_time=datetime.now()
                )
                house.save()
                
                # 查询测试
                houses = HouseModel.objects(city='天河')
                
                self.test_results['django_integration']['mongoengine'] = {
                    'success': True,
                    'model_created': True,
                    'save_success': True,
                    'query_count': len(houses)
                }
                
                print("✅ MongoEngine集成测试成功")
                
            except ImportError:
                self.test_results['django_integration']['mongoengine'] = {
                    'success': False,
                    'error': 'MongoEngine not installed'
                }
                print("⚠️ MongoEngine未安装")
            
            # 测试djongo
            try:
                import djongo
                self.test_results['django_integration']['djongo'] = {
                    'success': True,
                    'installed': True
                }
                print("✅ Djongo可用")
                
            except ImportError:
                self.test_results['django_integration']['djongo'] = {
                    'success': False,
                    'error': 'Djongo not installed'
                }
                print("⚠️ Djongo未安装")
            
            return True
            
        except Exception as e:
            self.test_results['django_integration'] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ Django集成测试失败: {e}")
            return False
    
    def generate_report(self):
        """生成测试报告"""
        report_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        os.makedirs(report_dir, exist_ok=True)
        
        # JSON报告
        json_file = os.path.join(report_dir, 'mongodb_integration_test.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        # Markdown报告
        md_file = os.path.join(report_dir, 'mongodb_integration_test.md')
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_markdown_report())
        
        print(f"📄 MongoDB测试报告已生成: {md_file}")
    
    def generate_markdown_report(self):
        """生成Markdown报告"""
        conn = self.test_results.get('connection_test', {})
        crud = self.test_results.get('crud_test', {})
        perf = self.test_results.get('performance_test', {})
        django = self.test_results.get('django_integration', {})
        
        report = f"""# MongoDB集成测试报告

## 测试时间
{self.test_results['test_time']}

## 连接测试
- **状态**: {'✅ 成功' if conn.get('success') else '❌ 失败'}
- **连接时间**: {conn.get('connection_time', 0):.3f} 秒
- **MongoDB版本**: {conn.get('server_info', 'N/A')}

## CRUD操作测试
- **状态**: {'✅ 成功' if crud.get('success') else '❌ 失败'}
- **插入性能**: {crud.get('insert_time', 0):.3f} 秒
- **查询性能**: {crud.get('query_time', 0):.3f} 秒
- **更新性能**: {crud.get('update_time', 0):.3f} 秒
- **聚合查询**: {crud.get('aggregation_time', 0):.3f} 秒

## 性能测试
- **状态**: {'✅ 成功' if perf.get('success') else '❌ 失败'}
- **测试记录数**: {perf.get('record_count', 0)} 条
- **插入速度**: {perf.get('insert_rate', 0):.0f} 条/秒
- **查询性能**: {perf.get('filter_time', 0):.3f} 秒

## Django集成
- **MongoEngine**: {'✅ 可用' if django.get('mongoengine', {}).get('success') else '❌ 不可用'}
- **Djongo**: {'✅ 可用' if django.get('djongo', {}).get('success') else '❌ 不可用'}

## 结论
{'MongoDB集成测试通过，建议进行架构升级' if all([conn.get('success'), crud.get('success'), perf.get('success')]) else '需要解决MongoDB集成问题'}
"""
        return report
    
    def run_full_test(self):
        """运行完整测试"""
        print("🚀 开始MongoDB集成测试...")
        
        if not self.test_connection():
            print("❌ 连接测试失败，跳过后续测试")
            self.generate_report()
            return False
        
        self.test_crud_operations()
        self.test_performance(1000)
        self.test_django_integration()
        
        self.generate_report()
        print("✅ MongoDB集成测试完成!")
        
        if self.client:
            self.client.close()
        
        return True


if __name__ == "__main__":
    test = MongoDBIntegrationTest()
    test.run_full_test()
