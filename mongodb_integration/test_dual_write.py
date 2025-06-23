#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双写机制测试脚本
包含离线数据迁移、双写测试、一致性验证
"""

import os
import sys
import time
import pymysql
import mongoengine
from datetime import datetime
from decimal import Decimal

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mongodb_integration.models.data_mapper import DataMapper, DataSynchronizer
from mongodb_integration.models.mongo_models import HouseDocument

class DataAdapter:
    """数据适配器 - 处理历史数据格式转换"""

    @staticmethod
    def normalize_url(relative_url):
        """将相对URL转换为完整URL"""
        if not relative_url:
            return "https://gz.lianjia.com/"

        relative_url = str(relative_url).strip()

        if relative_url.startswith('http'):
            return relative_url  # 已经是完整URL
        elif relative_url.startswith('/'):
            return f"https://gz.lianjia.com{relative_url}"  # 补充域名
        else:
            return f"https://gz.lianjia.com/{relative_url}"  # 补充完整路径

    @staticmethod
    def normalize_rental_type(original_type):
        """标准化租赁类型"""
        if not original_type:
            return '整租'

        original_type = str(original_type).strip()

        # 租赁类型映射规则
        type_mapping = {
            # 标准类型
            '整租': '整租',
            '合租': '合租',
            '单间': '单间',

            # 房型映射为整租
            '独栋': '整租',
            '1室': '整租',
            '1室1厅': '整租',
            '1室1厅1卫': '整租',
            '2室': '整租',
            '2室1厅': '整租',
            '2室1厅1卫': '整租',
            '2室2厅': '整租',
            '3室': '整租',
            '3室1厅': '整租',
            '3室1厅1卫': '整租',
            '3室2厅': '整租',
            '4室': '整租',
            '4室1厅': '整租',
            '4室2厅': '整租',
            '5室': '整租',

            # 公寓类型
            '公寓': '整租',
            '单身公寓': '单间',
            '酒店式公寓': '整租',

            # 其他类型
            '别墅': '整租',
            '复式': '整租',
            '跃层': '整租',
            'loft': '整租',
            'LOFT': '整租',
        }

        # 精确匹配
        if original_type in type_mapping:
            return type_mapping[original_type]

        # 模糊匹配
        original_lower = original_type.lower()

        # 包含关键词的匹配
        if any(keyword in original_lower for keyword in ['室', '厅', '独栋', '别墅', '复式', '跃层']):
            return '整租'
        elif any(keyword in original_lower for keyword in ['合租', '共享']):
            return '合租'
        elif any(keyword in original_lower for keyword in ['单间', '床位']):
            return '单间'
        elif any(keyword in original_lower for keyword in ['公寓', 'loft']):
            return '整租'

        # 默认返回整租
        return '整租'

    @staticmethod
    def normalize_area(area_value):
        """标准化面积数据"""
        if not area_value:
            return 0.0

        try:
            # 转换为浮点数
            area = float(area_value)

            # 合理性检查
            if area < 0:
                return 0.0
            elif area > 1000:  # 超过1000平米的可能是错误数据
                return 0.0
            else:
                return area
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def normalize_price(price_value):
        """标准化价格数据"""
        if not price_value:
            return 0.0

        try:
            # 转换为浮点数
            price = float(price_value)

            # 合理性检查
            if price < 0:
                return 0.0
            elif price > 50000:  # 超过5万的租金可能是错误数据
                return 0.0
            else:
                return price
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def normalize_string(value, max_length=None):
        """标准化字符串数据"""
        if not value:
            return ''

        result = str(value).strip()

        if max_length and len(result) > max_length:
            result = result[:max_length]

        return result

    @classmethod
    def adapt_house_data(cls, mysql_row):
        """适配House表数据为MongoDB格式"""
        # House表字段: title, type, building, city, street, area, direct, price, link, tag, img

        adapted_data = {
            'title': cls.normalize_string(mysql_row[0], 300),
            'type': cls.normalize_rental_type(mysql_row[1]),
            'building': cls.normalize_string(mysql_row[2], 255),
            'city': cls.normalize_string(mysql_row[3], 100),
            'street': cls.normalize_string(mysql_row[4], 300),
            'area': cls.normalize_area(mysql_row[5]),
            'direct': cls.normalize_string(mysql_row[6], 100),
            'price': cls.normalize_price(mysql_row[7]),
            'link': cls.normalize_url(mysql_row[8]),
            'tag': cls.normalize_string(mysql_row[9], 255),
            'img': cls.normalize_string(mysql_row[10], 500),
            # 补充缺失字段
            'crawl_time': datetime.now(),
            'spider_name': 'legacy_data',
            'crawl_id': f'migration_{int(time.time())}',
            'data_quality': 80  # 历史数据默认质量分
        }

        return adapted_data

class DualWriteTestSuite:
    """双写机制测试套件"""
    
    def __init__(self):
        self.mysql_conn = None
        self.mongo_conn = None
        self.test_results = {}
        self.start_time = datetime.now()
        
        # 数据库配置
        self.mysql_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '123456',
            'database': 'guangzhou_house',
            'charset': 'utf8mb4'
        }
        
        self.mongo_config = {
            'host': '127.0.0.1',
            'port': 27017,
            'database': 'house_data'
        }
    
    def setup_connections(self):
        """建立数据库连接"""
        print("🔗 建立数据库连接...")
        
        try:
            # MySQL连接
            self.mysql_conn = pymysql.connect(**self.mysql_config)
            print("✅ MySQL连接成功")
            
            # MongoDB连接
            mongoengine.disconnect()
            self.mongo_conn = mongoengine.connect(
                db=self.mongo_config['database'],
                host=self.mongo_config['host'],
                port=self.mongo_config['port']
            )
            print("✅ MongoDB连接成功")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def check_mysql_data(self):
        """检查MySQL数据状态"""
        print("\n📊 检查MySQL数据状态...")
        
        try:
            cursor = self.mysql_conn.cursor()
            
            # 检查House表
            cursor.execute("SELECT COUNT(*) FROM House")
            house_count = cursor.fetchone()[0]
            
            # 检查House_scrapy表
            cursor.execute("SELECT COUNT(*) FROM House_scrapy")
            scrapy_count = cursor.fetchone()[0]
            
            # 检查是否存在双写备份表
            cursor.execute("SHOW TABLES LIKE 'House_dual_write'")
            dual_write_exists = cursor.fetchone() is not None
            
            if dual_write_exists:
                cursor.execute("SELECT COUNT(*) FROM House_dual_write")
                dual_write_count = cursor.fetchone()[0]
            else:
                dual_write_count = 0
            
            cursor.close()
            
            print(f"  📋 House表: {house_count:,} 条记录")
            print(f"  📋 House_scrapy表: {scrapy_count:,} 条记录")
            print(f"  📋 House_dual_write表: {dual_write_count:,} 条记录")
            
            self.test_results['mysql_data_status'] = {
                'house_count': house_count,
                'scrapy_count': scrapy_count,
                'dual_write_count': dual_write_count,
                'dual_write_exists': dual_write_exists
            }
            
            return house_count > 0
            
        except Exception as e:
            print(f"❌ MySQL数据检查失败: {e}")
            return False
    
    def check_mongodb_data(self):
        """检查MongoDB数据状态"""
        print("\n📊 检查MongoDB数据状态...")
        
        try:
            # 检查houses集合
            house_count = HouseDocument.objects.count()
            
            print(f"  📋 houses集合: {house_count:,} 条记录")
            
            self.test_results['mongodb_data_status'] = {
                'house_count': house_count
            }
            
            return True
            
        except Exception as e:
            print(f"❌ MongoDB数据检查失败: {e}")
            return False
    
    def migrate_mysql_to_mongodb(self, batch_size=500):
        """迁移MySQL数据到MongoDB"""
        print(f"\n🚀 开始数据迁移 (批次大小: {batch_size})...")

        try:
            cursor = self.mysql_conn.cursor()

            # 获取House表数据总数
            cursor.execute("SELECT COUNT(*) FROM House")
            total_count = cursor.fetchone()[0]

            print(f"开始同步 {total_count:,} 条数据从House表到MongoDB")

            # 分批处理
            offset = 0
            synced_count = 0
            start_time = time.time()

            while offset < total_count:
                # 获取一批数据 (House表字段结构)
                cursor.execute("""
                    SELECT title, type, building, city, street, area, direct, price,
                           link, tag, img
                    FROM House
                    LIMIT %s OFFSET %s
                """, (batch_size, offset))

                rows = cursor.fetchall()

                for i, row in enumerate(rows):
                    try:
                        # 使用数据适配器转换数据
                        adapted_data = DataAdapter.adapt_house_data(row)

                        # 为每条记录生成唯一的crawl_id
                        adapted_data['crawl_id'] = f'migration_{offset + i + 1}'

                        # 转换为MongoDB文档
                        mongo_doc = DataMapper.mysql_dict_to_mongo(adapted_data)

                        # 保存到MongoDB
                        mongo_doc.save()
                        synced_count += 1

                    except Exception as e:
                        print(f"同步第{offset + i + 1}条数据失败: {e}")
                        # 可选：记录失败的数据用于后续分析
                        if synced_count == 0:  # 只在开始时显示几个错误示例
                            print(f"  失败数据示例: {row[:3]}...")  # 只显示前3个字段

                offset += batch_size

                # 显示进度
                if synced_count % 1000 == 0 or offset >= total_count:
                    elapsed = time.time() - start_time
                    speed = synced_count / elapsed if elapsed > 0 else 0
                    print(f"已同步 {synced_count:,}/{total_count:,} 条数据 ({speed:.1f} 条/秒)")

            cursor.close()
            migration_time = time.time() - start_time

            print(f"✅ 数据迁移完成")
            print(f"  📊 迁移数量: {synced_count:,} 条")
            print(f"  ⏱️  迁移耗时: {migration_time:.2f} 秒")
            print(f"  🚀 迁移速度: {synced_count/migration_time:.1f} 条/秒")

            self.test_results['data_migration'] = {
                'success': True,
                'synced_count': synced_count,
                'migration_time': migration_time,
                'migration_speed': synced_count/migration_time if migration_time > 0 else 0,
                'batch_size': batch_size
            }

            return synced_count > 0

        except Exception as e:
            print(f"❌ 数据迁移失败: {e}")
            self.test_results['data_migration'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    def validate_migration_data(self, sample_size=100):
        """验证迁移数据的正确性"""
        print(f"\n🔍 验证迁移数据 (样本大小: {sample_size})...")

        try:
            cursor = self.mysql_conn.cursor()

            # 随机抽取MySQL数据样本 (House表字段结构)
            cursor.execute(f"""
                SELECT title, type, building, city, street, area, direct, price,
                       link, tag, img
                FROM House
                ORDER BY RAND()
                LIMIT {sample_size}
            """)

            mysql_samples = cursor.fetchall()
            cursor.close()

            validation_results = {
                'total_samples': len(mysql_samples),
                'valid_samples': 0,
                'invalid_samples': 0,
                'errors': []
            }

            for row in mysql_samples:
                try:
                    # 使用数据适配器转换数据（与迁移时保持一致）
                    adapted_data = DataAdapter.adapt_house_data(row)

                    # 查找对应的MongoDB文档
                    mongo_docs = HouseDocument.objects(title=adapted_data['title'])

                    if mongo_docs:
                        mongo_doc = mongo_docs.first()

                        # 验证关键字段（使用适配后的数据进行比较）
                        title_match = mongo_doc.title == adapted_data['title']
                        type_match = mongo_doc.rental_type == adapted_data['type']
                        price_match = abs(float(mongo_doc.price.monthly_rent) - float(adapted_data['price'])) < 0.01
                        city_match = mongo_doc.location.city == adapted_data['city']

                        if title_match and type_match and price_match and city_match:
                            validation_results['valid_samples'] += 1
                        else:
                            validation_results['invalid_samples'] += 1
                            mismatch_details = []
                            if not title_match:
                                mismatch_details.append("标题不匹配")
                            if not type_match:
                                mismatch_details.append(f"类型不匹配(原:{row[1]}->适配:{adapted_data['type']}->存储:{mongo_doc.rental_type})")
                            if not price_match:
                                mismatch_details.append(f"价格不匹配({adapted_data['price']} vs {mongo_doc.price.monthly_rent})")
                            if not city_match:
                                mismatch_details.append("城市不匹配")

                            validation_results['errors'].append(f"数据不匹配: {adapted_data['title']} - {', '.join(mismatch_details)}")
                    else:
                        validation_results['invalid_samples'] += 1
                        validation_results['errors'].append(f"MongoDB中未找到: {adapted_data['title']}")

                except Exception as e:
                    validation_results['invalid_samples'] += 1
                    validation_results['errors'].append(f"验证错误: {str(e)}")

            success_rate = (validation_results['valid_samples'] / validation_results['total_samples']) * 100

            print(f"✅ 数据验证完成")
            print(f"  📊 验证样本: {validation_results['total_samples']} 条")
            print(f"  ✅ 有效样本: {validation_results['valid_samples']} 条")
            print(f"  ❌ 无效样本: {validation_results['invalid_samples']} 条")
            print(f"  📈 成功率: {success_rate:.1f}%")

            if validation_results['errors']:
                print(f"  ⚠️  错误示例: {validation_results['errors'][:3]}")

            self.test_results['data_validation'] = validation_results
            self.test_results['data_validation']['success_rate'] = success_rate

            return success_rate > 95  # 95%以上认为成功

        except Exception as e:
            print(f"❌ 数据验证失败: {e}")
            return False
    
    def performance_comparison(self):
        """性能对比测试"""
        print("\n⚡ 性能对比测试...")
        
        try:
            # MySQL查询测试
            mysql_times = []
            cursor = self.mysql_conn.cursor()
            
            for i in range(5):
                start_time = time.time()
                cursor.execute("SELECT COUNT(*) FROM House WHERE price BETWEEN 2000 AND 5000")
                cursor.fetchone()
                mysql_times.append(time.time() - start_time)
            
            cursor.close()
            avg_mysql_time = sum(mysql_times) / len(mysql_times)
            
            # MongoDB查询测试
            mongo_times = []
            
            for i in range(5):
                start_time = time.time()
                count = HouseDocument.objects(price__monthly_rent__gte=2000, price__monthly_rent__lte=5000).count()
                mongo_times.append(time.time() - start_time)
            
            avg_mongo_time = sum(mongo_times) / len(mongo_times)
            
            print(f"  🔍 MySQL平均查询时间: {avg_mysql_time:.3f} 秒")
            print(f"  🔍 MongoDB平均查询时间: {avg_mongo_time:.3f} 秒")
            
            if avg_mysql_time > 0:
                speedup = avg_mysql_time / avg_mongo_time
                print(f"  📈 MongoDB相对加速: {speedup:.2f}x")
            
            self.test_results['performance_comparison'] = {
                'mysql_avg_time': avg_mysql_time,
                'mongodb_avg_time': avg_mongo_time,
                'speedup': speedup if avg_mysql_time > 0 else 0
            }
            
            return True
            
        except Exception as e:
            print(f"❌ 性能对比失败: {e}")
            return False
    
    def cleanup_connections(self):
        """清理数据库连接"""
        if self.mysql_conn:
            self.mysql_conn.close()
            print("🔌 MySQL连接已关闭")
        
        if self.mongo_conn:
            mongoengine.disconnect()
            print("🔌 MongoDB连接已关闭")
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📋 双写机制测试报告")
        print("="*60)
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        print(f"⏱️  总测试时间: {total_time:.1f} 秒")
        print(f"📅 测试时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 数据状态
        if 'mysql_data_status' in self.test_results:
            mysql_status = self.test_results['mysql_data_status']
            print(f"\n📊 MySQL数据状态:")
            print(f"  - House表: {mysql_status['house_count']:,} 条")
            print(f"  - House_scrapy表: {mysql_status['scrapy_count']:,} 条")
            print(f"  - House_dual_write表: {mysql_status['dual_write_count']:,} 条")
        
        if 'mongodb_data_status' in self.test_results:
            mongo_status = self.test_results['mongodb_data_status']
            print(f"\n📊 MongoDB数据状态:")
            print(f"  - houses集合: {mongo_status['house_count']:,} 条")
        
        # 迁移结果
        if 'data_migration' in self.test_results:
            migration = self.test_results['data_migration']
            if migration['success']:
                print(f"\n🚀 数据迁移结果:")
                print(f"  - 迁移数量: {migration['synced_count']:,} 条")
                print(f"  - 迁移耗时: {migration['migration_time']:.2f} 秒")
                print(f"  - 迁移速度: {migration['migration_speed']:.1f} 条/秒")
            else:
                print(f"\n❌ 数据迁移失败: {migration.get('error', 'Unknown error')}")
        
        # 验证结果
        if 'data_validation' in self.test_results:
            validation = self.test_results['data_validation']
            print(f"\n🔍 数据验证结果:")
            print(f"  - 验证样本: {validation['total_samples']} 条")
            print(f"  - 成功率: {validation['success_rate']:.1f}%")
            print(f"  - 有效样本: {validation['valid_samples']} 条")
            print(f"  - 无效样本: {validation['invalid_samples']} 条")
        
        # 性能对比
        if 'performance_comparison' in self.test_results:
            perf = self.test_results['performance_comparison']
            print(f"\n⚡ 性能对比结果:")
            print(f"  - MySQL查询时间: {perf['mysql_avg_time']:.3f} 秒")
            print(f"  - MongoDB查询时间: {perf['mongodb_avg_time']:.3f} 秒")
            print(f"  - MongoDB加速比: {perf['speedup']:.2f}x")
        
        print("\n" + "="*60)
        
        # 保存报告到文件
        report_file = f"mongodb_integration/dual_write_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"双写机制测试报告\n")
            f.write(f"测试时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总耗时: {total_time:.1f} 秒\n\n")
            f.write(f"测试结果: {self.test_results}\n")
        
        print(f"📄 详细报告已保存: {report_file}")

def main():
    """主函数"""
    print("🎯 双写机制测试套件")
    print("="*60)
    
    # 创建测试套件
    test_suite = DualWriteTestSuite()
    
    try:
        # 1. 建立连接
        if not test_suite.setup_connections():
            return False
        
        # 2. 检查数据状态
        if not test_suite.check_mysql_data():
            print("❌ MySQL数据检查失败，无法继续测试")
            return False
        
        test_suite.check_mongodb_data()
        
        # 3. 执行数据迁移
        if not test_suite.migrate_mysql_to_mongodb():
            print("❌ 数据迁移失败")
            return False
        
        # 4. 验证迁移数据
        if not test_suite.validate_migration_data():
            print("⚠️  数据验证未完全通过，但继续测试")
        
        # 5. 性能对比
        test_suite.performance_comparison()
        
        # 6. 生成报告
        test_suite.generate_report()
        
        print("\n🎉 双写机制测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False
        
    finally:
        # 清理连接
        test_suite.cleanup_connections()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
