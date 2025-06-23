#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据映射工具
MySQL <-> MongoDB 数据转换
"""

from datetime import datetime
from decimal import Decimal
import uuid

class DataMapper:
    """数据映射器"""
    
    @staticmethod
    def scrapy_item_to_mongo(item):
        """Scrapy Item -> MongoDB Document"""
        from mongodb_integration.models.mongo_models import (
            HouseDocument, LocationInfo, PriceInfo, 
            HouseFeatures, CrawlMetadata
        )
        
        # 创建位置信息
        location = LocationInfo(
            city=str(item.get('city', '')).strip(),
            street=str(item.get('street', '')).strip(),
            building=str(item.get('building', '')).strip()
        )
        
        # 创建价格信息
        price = PriceInfo(
            monthly_rent=Decimal(str(item.get('price', 0)))
        )
        
        # 创建房屋特征
        features = HouseFeatures(
            area=Decimal(str(item.get('area', 0))),
            room_type=str(item.get('type', '')).strip(),
            direction=str(item.get('direct', '')).strip()
        )
        
        # 创建爬取元数据
        crawl_meta = CrawlMetadata(
            spider_name=str(item.get('spider_name', '')),
            crawl_id=str(item.get('crawl_id', '')),
            source_url=str(item.get('link', '')),
            data_quality=int(item.get('data_quality', 0)),
            crawl_time=item.get('crawl_time', datetime.now())
        )
        
        # 处理标签
        tag_str = str(item.get('tag', '')).strip()
        tags = [tag.strip() for tag in tag_str.split(',') if tag.strip()] if tag_str else []
        
        # 处理图片
        img_url = str(item.get('img', '')).strip()
        images = [img_url] if img_url else []
        
        # 创建主文档
        house = HouseDocument(
            title=str(item.get('title', '')).strip(),
            rental_type=str(item.get('type', '')).strip(),
            location=location,
            price=price,
            features=features,
            crawl_meta=crawl_meta,
            tags=tags,
            images=images
        )
        
        return house
    
    @staticmethod
    def mongo_to_mysql_dict(mongo_doc):
        """MongoDB Document -> MySQL Dict"""
        return {
            'title': mongo_doc.title,
            'type': mongo_doc.rental_type,
            'building': mongo_doc.location.building,
            'city': mongo_doc.location.city,
            'street': mongo_doc.location.street,
            'area': float(mongo_doc.features.area),
            'direct': mongo_doc.features.direction,
            'price': float(mongo_doc.price.monthly_rent),
            'link': mongo_doc.crawl_meta.source_url,
            'tag': ','.join(mongo_doc.tags),
            'img': mongo_doc.images[0] if mongo_doc.images else '',
            'crawl_time': mongo_doc.crawl_meta.crawl_time,
            'spider_name': mongo_doc.crawl_meta.spider_name,
            'crawl_id': mongo_doc.crawl_meta.crawl_id,
            'data_quality': mongo_doc.crawl_meta.data_quality
        }
    
    @staticmethod
    def mysql_dict_to_mongo(mysql_dict):
        """MySQL Dict -> MongoDB Document"""
        from mongodb_integration.models.mongo_models import (
            HouseDocument, LocationInfo, PriceInfo, 
            HouseFeatures, CrawlMetadata
        )
        
        # 创建位置信息
        location = LocationInfo(
            city=str(mysql_dict.get('city', '')).strip(),
            street=str(mysql_dict.get('street', '')).strip(),
            building=str(mysql_dict.get('building', '')).strip()
        )
        
        # 创建价格信息
        price = PriceInfo(
            monthly_rent=Decimal(str(mysql_dict.get('price', 0)))
        )
        
        # 创建房屋特征
        features = HouseFeatures(
            area=Decimal(str(mysql_dict.get('area', 0))),
            room_type=str(mysql_dict.get('type', '')).strip(),
            direction=str(mysql_dict.get('direct', '')).strip()
        )
        
        # 创建爬取元数据
        crawl_meta = CrawlMetadata(
            spider_name=str(mysql_dict.get('spider_name', '')),
            crawl_id=str(mysql_dict.get('crawl_id', '')),
            source_url=str(mysql_dict.get('link', '')),
            data_quality=int(mysql_dict.get('data_quality', 0)),
            crawl_time=mysql_dict.get('crawl_time', datetime.now())
        )
        
        # 处理标签
        tag_str = str(mysql_dict.get('tag', '')).strip()
        tags = [tag.strip() for tag in tag_str.split(',') if tag.strip()] if tag_str else []
        
        # 处理图片
        img_url = str(mysql_dict.get('img', '')).strip()
        images = [img_url] if img_url else []
        
        # 创建主文档
        house = HouseDocument(
            title=str(mysql_dict.get('title', '')).strip(),
            rental_type=str(mysql_dict.get('type', '')).strip(),
            location=location,
            price=price,
            features=features,
            crawl_meta=crawl_meta,
            tags=tags,
            images=images
        )
        
        return house
    
    @staticmethod
    def validate_data(data_dict):
        """验证数据完整性"""
        errors = []
        warnings = []
        
        # 必填字段检查
        required_fields = ['title', 'city', 'price']
        for field in required_fields:
            if not data_dict.get(field):
                errors.append(f"缺少必填字段: {field}")
        
        # 数据类型检查
        try:
            price = float(data_dict.get('price', 0))
            if price <= 0:
                warnings.append("价格为0或负数")
        except (ValueError, TypeError):
            errors.append("价格格式错误")
        
        try:
            area = float(data_dict.get('area', 0))
            if area <= 0:
                warnings.append("面积为0或负数")
        except (ValueError, TypeError):
            errors.append("面积格式错误")
        
        # 数据质量评分
        quality_score = 100
        quality_score -= len(errors) * 20
        quality_score -= len(warnings) * 10
        quality_score = max(0, quality_score)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'quality_score': quality_score
        }

class DataSynchronizer:
    """数据同步器"""
    
    def __init__(self, mysql_connection, mongo_connection):
        self.mysql_conn = mysql_connection
        self.mongo_conn = mongo_connection
    
    def sync_mysql_to_mongo(self, batch_size=100):
        """MySQL -> MongoDB 数据同步"""
        try:
            cursor = self.mysql_conn.cursor()
            
            # 获取MySQL数据总数
            cursor.execute("SELECT COUNT(*) FROM House_scrapy")
            total_count = cursor.fetchone()[0]
            
            print(f"开始同步 {total_count} 条数据从MySQL到MongoDB")
            
            # 分批处理
            offset = 0
            synced_count = 0
            
            while offset < total_count:
                # 获取一批数据
                cursor.execute("""
                    SELECT title, type, building, city, street, area, direct, price, 
                           link, tag, img, crawl_time, spider_name, crawl_id, data_quality
                    FROM House_scrapy 
                    LIMIT %s OFFSET %s
                """, (batch_size, offset))
                
                rows = cursor.fetchall()
                
                for row in rows:
                    try:
                        # 转换为字典
                        mysql_dict = {
                            'title': row[0],
                            'type': row[1],
                            'building': row[2],
                            'city': row[3],
                            'street': row[4],
                            'area': row[5],
                            'direct': row[6],
                            'price': row[7],
                            'link': row[8],
                            'tag': row[9],
                            'img': row[10],
                            'crawl_time': row[11],
                            'spider_name': row[12],
                            'crawl_id': row[13],
                            'data_quality': row[14]
                        }
                        
                        # 转换为MongoDB文档
                        mongo_doc = DataMapper.mysql_dict_to_mongo(mysql_dict)
                        
                        # 保存到MongoDB
                        mongo_doc.save()
                        synced_count += 1
                        
                    except Exception as e:
                        print(f"同步单条数据失败: {e}")
                
                offset += batch_size
                print(f"已同步 {synced_count}/{total_count} 条数据")
            
            cursor.close()
            print(f"同步完成，共同步 {synced_count} 条数据")
            return synced_count
            
        except Exception as e:
            print(f"数据同步失败: {e}")
            return 0
    
    def sync_mongo_to_mysql(self, table_name="House_scrapy_from_mongo"):
        """MongoDB -> MySQL 数据同步"""
        try:
            from mongodb_integration.models.mongo_models import HouseDocument
            
            # 获取MongoDB数据
            mongo_docs = HouseDocument.objects.all()
            total_count = mongo_docs.count()
            
            print(f"开始同步 {total_count} 条数据从MongoDB到MySQL")
            
            cursor = self.mysql_conn.cursor()
            
            # 创建目标表（如果不存在）
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255),
                type VARCHAR(100),
                building VARCHAR(255),
                city VARCHAR(100),
                street VARCHAR(100),
                area DECIMAL(10,2),
                direct VARCHAR(50),
                price DECIMAL(10,2),
                link TEXT,
                tag VARCHAR(255),
                img TEXT,
                crawl_time DATETIME,
                spider_name VARCHAR(50),
                crawl_id VARCHAR(100),
                data_quality INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
            cursor.execute(create_table_sql)
            
            synced_count = 0
            
            for doc in mongo_docs:
                try:
                    # 转换为MySQL字典
                    mysql_dict = DataMapper.mongo_to_mysql_dict(doc)
                    
                    # 插入MySQL
                    insert_sql = f"""
                    INSERT INTO {table_name} (
                        title, type, building, city, street, area, direct, price,
                        link, tag, img, crawl_time, spider_name, crawl_id, data_quality
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(insert_sql, (
                        mysql_dict['title'],
                        mysql_dict['type'],
                        mysql_dict['building'],
                        mysql_dict['city'],
                        mysql_dict['street'],
                        mysql_dict['area'],
                        mysql_dict['direct'],
                        mysql_dict['price'],
                        mysql_dict['link'],
                        mysql_dict['tag'],
                        mysql_dict['img'],
                        mysql_dict['crawl_time'],
                        mysql_dict['spider_name'],
                        mysql_dict['crawl_id'],
                        mysql_dict['data_quality']
                    ))
                    
                    synced_count += 1
                    
                except Exception as e:
                    print(f"同步单条数据失败: {e}")
            
            self.mysql_conn.commit()
            cursor.close()
            
            print(f"同步完成，共同步 {synced_count} 条数据到表 {table_name}")
            return synced_count
            
        except Exception as e:
            print(f"数据同步失败: {e}")
            return 0
