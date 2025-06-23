#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
房源数据迁移脚本
将MySQL中的房源数据迁移到MongoDB
"""

import os
import sys
import time
from datetime import datetime
from decimal import Decimal

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Python租房房源数据可视化分析.settings')
import django
django.setup()

import pymysql
from mongodb_integration.models.mongo_models import (
    HouseDocument, LocationInfo, PriceInfo, 
    HouseFeatures, CrawlMetadata
)

class HouseDataMigrator:
    """房源数据迁移器"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.migrated_count = 0
        self.error_count = 0
        self.errors = []
    
    def connect_mysql(self):
        """连接MySQL数据库"""
        try:
            self.mysql_conn = pymysql.connect(
                host='localhost',
                user='root',
                password='123456',
                database='guangzhou_house',
                charset='utf8mb4'
            )
            self.mysql_cursor = self.mysql_conn.cursor()
            print("✅ MySQL连接成功")
            return True
        except Exception as e:
            print(f"❌ MySQL连接失败: {e}")
            return False
    
    def get_mysql_house_count(self):
        """获取MySQL中的房源数量"""
        try:
            self.mysql_cursor.execute("SELECT COUNT(*) FROM House")
            count = self.mysql_cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"❌ 获取MySQL房源数量失败: {e}")
            return 0
    
    def migrate_house_data(self, batch_size=1000):
        """迁移房源数据"""
        print("🚀 开始迁移房源数据...")
        
        # 获取总数量
        total_count = self.get_mysql_house_count()
        print(f"📊 MySQL中房源总数: {total_count:,} 条")
        
        if total_count == 0:
            print("❌ MySQL中没有房源数据")
            return False
        
        # 检查MongoDB中现有数据
        existing_count = HouseDocument.objects.count()
        print(f"📊 MongoDB中现有房源数: {existing_count:,} 条")
        
        if existing_count > 0:
            print("⚠️  MongoDB中已有房源数据，是否清空后重新迁移？")
            response = input("输入 'yes' 清空重新迁移，其他键跳过: ")
            if response.lower() == 'yes':
                print("🗑️  清空MongoDB房源数据...")
                HouseDocument.objects.delete()
                print("✅ 清空完成")
            else:
                print("⏭️  跳过房源数据迁移")
                return True
        
        # 分批迁移
        offset = 0
        while offset < total_count:
            try:
                # 获取一批数据
                sql = """
                SELECT id, title, type, building, city, street, area, direct,
                       price, link, tag, img
                FROM House
                ORDER BY id
                LIMIT %s OFFSET %s
                """
                
                self.mysql_cursor.execute(sql, (batch_size, offset))
                batch_data = self.mysql_cursor.fetchall()
                
                if not batch_data:
                    break
                
                # 处理这批数据
                batch_success = self.process_batch(batch_data, offset, total_count)
                
                if not batch_success:
                    print(f"⚠️  批次 {offset//batch_size + 1} 处理失败")
                
                offset += batch_size
                
                # 显示进度
                progress = min(offset, total_count)
                percentage = (progress / total_count) * 100
                print(f"📈 迁移进度: {progress:,}/{total_count:,} ({percentage:.1f}%)")
                
            except Exception as e:
                print(f"❌ 批次迁移失败: {e}")
                self.error_count += 1
                self.errors.append(f"Batch {offset//batch_size + 1}: {str(e)}")
                offset += batch_size
        
        return True
    
    def process_batch(self, batch_data, offset, total_count):
        """处理一批数据"""
        batch_success = 0
        batch_errors = 0
        
        for row in batch_data:
            try:
                # 解析MySQL数据
                (mysql_id, title, house_type, building, city, street,
                 area, direction, price, link, tag, img) = row
                
                # 数据清理和转换
                title = str(title or '').strip()
                house_type = str(house_type or '').strip()
                building = str(building or '').strip()
                city = str(city or '').strip()
                street = str(street or '').strip()
                direction = str(direction or '').strip()
                link = str(link or '').strip()
                tag = str(tag or '').strip()
                img = str(img or '').strip()
                
                # 处理数值
                try:
                    area = float(area) if area else 0.0
                    price = float(price) if price else 0.0
                except:
                    area = 0.0
                    price = 0.0
                
                # 处理房型映射
                if house_type in ['独栋', '房型']:
                    house_type = '整租'
                elif not house_type:
                    house_type = '整租'
                
                # 确保URL格式正确
                if link and not link.startswith('http'):
                    if link.startswith('/'):
                        link = f"https://gz.lianjia.com{link}"
                    else:
                        link = f"https://gz.lianjia.com/{link}"
                
                # 创建嵌套文档
                location = LocationInfo(
                    city=city,
                    street=street,
                    building=building
                )
                
                price_info = PriceInfo(
                    monthly_rent=Decimal(str(price))
                )
                
                features = HouseFeatures(
                    area=Decimal(str(area)),
                    room_type=house_type,
                    direction=direction
                )
                
                crawl_meta = CrawlMetadata(
                    spider_name='mysql_migration',
                    crawl_id=f'migration_{datetime.now().strftime("%Y%m%d")}',
                    source_url=link,
                    data_quality=85,
                    crawl_time=datetime.now()
                )
                
                # 处理标签
                tags = [t.strip() for t in tag.split(',') if t.strip()] if tag else []
                
                # 处理图片
                images = [img] if img else []
                
                # 创建MongoDB文档
                house_doc = HouseDocument(
                    title=title,
                    rental_type=house_type,
                    location=location,
                    price=price_info,
                    features=features,
                    crawl_meta=crawl_meta,
                    tags=tags,
                    images=images
                )
                
                # 保存到MongoDB
                house_doc.save()
                batch_success += 1
                self.migrated_count += 1
                
            except Exception as e:
                batch_errors += 1
                self.error_count += 1
                error_msg = f"Row {mysql_id}: {str(e)}"
                self.errors.append(error_msg)
                if len(self.errors) <= 10:  # 只记录前10个错误
                    print(f"⚠️  数据转换错误: {error_msg}")
        
        return batch_success > 0
    
    def verify_migration(self):
        """验证迁移结果"""
        print("\n🔍 验证迁移结果...")
        
        try:
            # 检查MongoDB数据
            mongo_count = HouseDocument.objects.count()
            mysql_count = self.get_mysql_house_count()
            
            print(f"📊 迁移结果对比:")
            print(f"  MySQL原始数据: {mysql_count:,} 条")
            print(f"  MongoDB迁移数据: {mongo_count:,} 条")
            print(f"  成功迁移: {self.migrated_count:,} 条")
            print(f"  迁移错误: {self.error_count:,} 条")
            
            # 数据样本验证
            if mongo_count > 0:
                sample_houses = HouseDocument.objects.limit(3)
                print(f"\n📋 数据样本验证:")
                for i, house in enumerate(sample_houses, 1):
                    print(f"  {i}. {house.title[:40]}...")
                    print(f"     位置: {house.location.city} - {house.location.street}")
                    print(f"     价格: ¥{house.price.monthly_rent} | 面积: {house.features.area}㎡")
            
            # 索引验证
            print(f"\n🔧 创建索引...")
            HouseDocument.ensure_indexes()
            print(f"✅ 索引创建完成")
            
            return True
            
        except Exception as e:
            print(f"❌ 验证失败: {e}")
            return False
    
    def generate_report(self):
        """生成迁移报告"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print("\n" + "="*60)
        print("📋 房源数据迁移报告")
        print("="*60)
        print(f"⏱️  迁移时间: {duration:.1f} 秒")
        print(f"📅 开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📅 结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"✅ 成功迁移: {self.migrated_count:,} 条")
        print(f"❌ 迁移错误: {self.error_count:,} 条")
        
        if self.error_count > 0:
            print(f"\n⚠️  错误详情 (前10条):")
            for error in self.errors[:10]:
                print(f"  - {error}")
        
        # 计算迁移速度
        if duration > 0:
            speed = self.migrated_count / duration
            print(f"🚀 迁移速度: {speed:.1f} 条/秒")
        
        print("="*60)
    
    def close_connections(self):
        """关闭数据库连接"""
        if hasattr(self, 'mysql_cursor'):
            self.mysql_cursor.close()
        if hasattr(self, 'mysql_conn'):
            self.mysql_conn.close()

def main():
    """主函数"""
    print("🎯 房源数据迁移到MongoDB")
    print("="*60)
    
    migrator = HouseDataMigrator()
    
    try:
        # 连接MySQL
        if not migrator.connect_mysql():
            return False
        
        # 迁移数据
        if not migrator.migrate_house_data():
            return False
        
        # 验证迁移
        migrator.verify_migration()
        
        # 生成报告
        migrator.generate_report()
        
        print("\n🎉 房源数据迁移完成！")
        return True
        
    except Exception as e:
        print(f"❌ 迁移过程中发生错误: {e}")
        return False
    
    finally:
        migrator.close_connections()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
