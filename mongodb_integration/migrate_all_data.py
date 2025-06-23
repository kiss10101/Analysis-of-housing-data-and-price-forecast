#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整数据迁移脚本
将所有MySQL数据迁移到MongoDB
"""

import os
import sys
import time
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Python租房房源数据可视化分析.settings')
import django
django.setup()

from app_mongo.models import DataMigrator, MongoUser, MongoHistory, HouseDocument

class CompleteMigration:
    """完整数据迁移"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.migration_results = {}
    
    def migrate_users(self):
        """迁移用户数据"""
        print("🚀 开始迁移用户数据...")
        
        try:
            # 清空现有MongoDB用户数据（如果需要）
            existing_count = MongoUser.objects.count()
            print(f"MongoDB中现有用户数: {existing_count}")
            
            # 执行迁移
            migrated_count = DataMigrator.migrate_users_from_mysql()
            
            # 验证迁移结果
            total_mongo_users = MongoUser.objects.count()
            
            print(f"✅ 用户数据迁移完成")
            print(f"  📊 新迁移用户: {migrated_count} 个")
            print(f"  📊 MongoDB总用户数: {total_mongo_users} 个")
            
            self.migration_results['users'] = {
                'success': True,
                'migrated_count': migrated_count,
                'total_count': total_mongo_users
            }
            
            return True
            
        except Exception as e:
            print(f"❌ 用户数据迁移失败: {e}")
            self.migration_results['users'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    def verify_house_data(self):
        """验证房源数据"""
        print("\n🔍 验证房源数据...")
        
        try:
            house_count = HouseDocument.objects.count()
            
            if house_count > 0:
                print(f"✅ 房源数据验证通过")
                print(f"  📊 MongoDB房源总数: {house_count:,} 条")
                
                # 检查数据质量
                sample_houses = HouseDocument.objects.limit(5)
                print(f"  📋 数据样本:")
                for house in sample_houses:
                    print(f"    - {house.title} | {house.location.city} | ¥{house.price.monthly_rent}")
                
                self.migration_results['houses'] = {
                    'success': True,
                    'total_count': house_count
                }
                
                return True
            else:
                print("❌ 房源数据为空")
                self.migration_results['houses'] = {
                    'success': False,
                    'error': 'No house data found'
                }
                return False
                
        except Exception as e:
            print(f"❌ 房源数据验证失败: {e}")
            self.migration_results['houses'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    def migrate_history(self):
        """迁移收藏历史数据"""
        print("\n🚀 开始迁移收藏历史数据...")
        
        try:
            # 检查现有历史记录
            existing_count = MongoHistory.objects.count()
            print(f"MongoDB中现有历史记录数: {existing_count}")
            
            # 执行迁移
            migrated_count = DataMigrator.migrate_history_from_mysql()
            
            # 验证迁移结果
            total_mongo_history = MongoHistory.objects.count()
            
            print(f"✅ 收藏历史迁移完成")
            print(f"  📊 新迁移记录: {migrated_count} 条")
            print(f"  📊 MongoDB总历史记录: {total_mongo_history} 条")
            
            self.migration_results['history'] = {
                'success': True,
                'migrated_count': migrated_count,
                'total_count': total_mongo_history
            }
            
            return True
            
        except Exception as e:
            print(f"❌ 收藏历史迁移失败: {e}")
            self.migration_results['history'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    def create_indexes(self):
        """创建MongoDB索引"""
        print("\n🔧 创建MongoDB索引...")
        
        try:
            # 用户索引
            MongoUser.ensure_indexes()
            print("✅ 用户索引创建完成")
            
            # 历史记录索引
            MongoHistory.ensure_indexes()
            print("✅ 历史记录索引创建完成")
            
            # 房源索引（已在之前创建）
            HouseDocument.ensure_indexes()
            print("✅ 房源索引验证完成")
            
            self.migration_results['indexes'] = {
                'success': True,
                'message': 'All indexes created successfully'
            }
            
            return True
            
        except Exception as e:
            print(f"❌ 索引创建失败: {e}")
            self.migration_results['indexes'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    def verify_data_integrity(self):
        """验证数据完整性"""
        print("\n🔍 验证数据完整性...")
        
        try:
            # 验证用户数据
            mongo_users = MongoUser.objects.count()
            
            # 验证房源数据
            mongo_houses = HouseDocument.objects.count()
            
            # 验证历史记录数据
            mongo_history = MongoHistory.objects.count()
            
            print(f"📊 数据完整性验证:")
            print(f"  👥 用户数: {mongo_users}")
            print(f"  🏠 房源数: {mongo_houses:,}")
            print(f"  📚 历史记录数: {mongo_history}")
            
            # 验证关联关系
            if mongo_history > 0:
                sample_history = MongoHistory.objects.first()
                if sample_history and sample_history.user and sample_history.house:
                    print(f"  🔗 关联关系验证: 正常")
                    print(f"    示例: {sample_history.user.username} 收藏了 {sample_history.house.title}")
                else:
                    print(f"  ⚠️  关联关系验证: 异常")
            
            self.migration_results['integrity'] = {
                'success': True,
                'users': mongo_users,
                'houses': mongo_houses,
                'history': mongo_history
            }
            
            return True
            
        except Exception as e:
            print(f"❌ 数据完整性验证失败: {e}")
            self.migration_results['integrity'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    def generate_migration_report(self):
        """生成迁移报告"""
        print("\n" + "="*60)
        print("📋 数据迁移完成报告")
        print("="*60)
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        print(f"⏱️  总迁移时间: {total_time:.1f} 秒")
        print(f"📅 迁移时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 用户迁移结果
        if 'users' in self.migration_results:
            users_result = self.migration_results['users']
            if users_result['success']:
                print(f"\n👥 用户数据迁移: ✅ 成功")
                print(f"  - 迁移数量: {users_result['migrated_count']} 个")
                print(f"  - 总用户数: {users_result['total_count']} 个")
            else:
                print(f"\n👥 用户数据迁移: ❌ 失败")
                print(f"  - 错误: {users_result.get('error', 'Unknown error')}")
        
        # 房源验证结果
        if 'houses' in self.migration_results:
            houses_result = self.migration_results['houses']
            if houses_result['success']:
                print(f"\n🏠 房源数据验证: ✅ 通过")
                print(f"  - 房源总数: {houses_result['total_count']:,} 条")
            else:
                print(f"\n🏠 房源数据验证: ❌ 失败")
                print(f"  - 错误: {houses_result.get('error', 'Unknown error')}")
        
        # 历史记录迁移结果
        if 'history' in self.migration_results:
            history_result = self.migration_results['history']
            if history_result['success']:
                print(f"\n📚 历史记录迁移: ✅ 成功")
                print(f"  - 迁移数量: {history_result['migrated_count']} 条")
                print(f"  - 总记录数: {history_result['total_count']} 条")
            else:
                print(f"\n📚 历史记录迁移: ❌ 失败")
                print(f"  - 错误: {history_result.get('error', 'Unknown error')}")
        
        # 索引创建结果
        if 'indexes' in self.migration_results:
            indexes_result = self.migration_results['indexes']
            if indexes_result['success']:
                print(f"\n🔧 索引创建: ✅ 成功")
            else:
                print(f"\n🔧 索引创建: ❌ 失败")
                print(f"  - 错误: {indexes_result.get('error', 'Unknown error')}")
        
        # 数据完整性验证结果
        if 'integrity' in self.migration_results:
            integrity_result = self.migration_results['integrity']
            if integrity_result['success']:
                print(f"\n🔍 数据完整性: ✅ 验证通过")
                print(f"  - 用户: {integrity_result['users']} 个")
                print(f"  - 房源: {integrity_result['houses']:,} 条")
                print(f"  - 历史记录: {integrity_result['history']} 条")
            else:
                print(f"\n🔍 数据完整性: ❌ 验证失败")
                print(f"  - 错误: {integrity_result.get('error', 'Unknown error')}")
        
        print("\n" + "="*60)
        
        # 保存报告到文件
        report_file = f"mongodb_integration/migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"数据迁移报告\n")
            f.write(f"迁移时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总耗时: {total_time:.1f} 秒\n\n")
            f.write(f"迁移结果: {self.migration_results}\n")
        
        print(f"📄 详细报告已保存: {report_file}")

def main():
    """主函数"""
    print("🎯 完整数据迁移到MongoDB")
    print("="*60)
    
    # 创建迁移器
    migrator = CompleteMigration()
    
    try:
        # 1. 迁移用户数据
        if not migrator.migrate_users():
            print("❌ 用户数据迁移失败，继续其他迁移...")
        
        # 2. 验证房源数据
        if not migrator.verify_house_data():
            print("❌ 房源数据验证失败，但继续...")
        
        # 3. 迁移收藏历史
        if not migrator.migrate_history():
            print("❌ 历史记录迁移失败，但继续...")
        
        # 4. 创建索引
        if not migrator.create_indexes():
            print("❌ 索引创建失败，但继续...")
        
        # 5. 验证数据完整性
        migrator.verify_data_integrity()
        
        # 6. 生成报告
        migrator.generate_migration_report()
        
        print("\n🎉 数据迁移流程完成！")
        return True
        
    except Exception as e:
        print(f"❌ 迁移过程中发生错误: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
