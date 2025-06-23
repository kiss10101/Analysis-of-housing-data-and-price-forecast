#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB存储管道
支持MongoDB数据存储和双写机制
"""

import sys
import os
from datetime import datetime

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, grandparent_dir)

from itemadapter import ItemAdapter
import mongoengine
from mongodb_integration.models.data_mapper import DataMapper


class MongoDBPipeline:
    """MongoDB存储管道"""
    
    def __init__(self, mongo_db='house_data', mongo_host='127.0.0.1', mongo_port=27017):
        self.mongo_db = mongo_db
        self.mongo_host = mongo_host
        self.mongo_port = mongo_port
        self.connection = None
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_db=crawler.settings.get("MONGO_DATABASE", "house_data"),
            mongo_host=crawler.settings.get("MONGO_HOST", "127.0.0.1"),
            mongo_port=crawler.settings.get("MONGO_PORT", 27017),
        )
    
    def open_spider(self, spider):
        """爬虫开始时建立MongoDB连接"""
        try:
            # 断开现有连接
            mongoengine.disconnect()
            
            # 建立新连接
            self.connection = mongoengine.connect(
                db=self.mongo_db,
                host=self.mongo_host,
                port=self.mongo_port,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=30000
            )
            
            spider.logger.info(f"MongoDB连接成功: {self.mongo_host}:{self.mongo_port}/{self.mongo_db}")
            
        except Exception as e:
            spider.logger.error(f"MongoDB连接失败: {e}")
            
    def close_spider(self, spider):
        """爬虫结束时关闭MongoDB连接"""
        if self.connection:
            mongoengine.disconnect()
            spider.logger.info("MongoDB连接已关闭")
    
    def process_item(self, item, spider):
        """处理数据项"""
        try:
            adapter = ItemAdapter(item)
            
            # 使用数据映射器转换为MongoDB文档
            mongo_doc = DataMapper.scrapy_item_to_mongo(dict(adapter))
            
            # 保存到MongoDB
            mongo_doc.save()
            
            spider.logger.debug(f"MongoDB保存成功: {mongo_doc.title}")
            
            return item
            
        except Exception as e:
            spider.logger.error(f"MongoDB保存失败: {e}")
            return item


class DualWritePipeline:
    """双写管道 - 同时写入MySQL和MongoDB"""
    
    def __init__(self, mysql_settings, mongo_settings):
        self.mysql_settings = mysql_settings
        self.mongo_settings = mongo_settings
        self.mysql_connection = None
        self.mongo_connection = None
        self.mysql_cursor = None
        
    @classmethod
    def from_crawler(cls, crawler):
        mysql_settings = {
            'host': crawler.settings.get("MYSQL_HOST", "localhost"),
            'port': crawler.settings.get("MYSQL_PORT", 3306),
            'user': crawler.settings.get("MYSQL_USER", "root"),
            'password': crawler.settings.get("MYSQL_PASSWORD", "123456"),
            'database': crawler.settings.get("MYSQL_DATABASE", "guangzhou_house")
        }
        
        mongo_settings = {
            'database': crawler.settings.get("MONGO_DATABASE", "house_data"),
            'host': crawler.settings.get("MONGO_HOST", "127.0.0.1"),
            'port': crawler.settings.get("MONGO_PORT", 27017)
        }
        
        return cls(mysql_settings, mongo_settings)
    
    def open_spider(self, spider):
        """爬虫开始时建立双重连接"""
        # 建立MySQL连接
        try:
            import pymysql
            self.mysql_connection = pymysql.connect(
                host=self.mysql_settings['host'],
                port=self.mysql_settings['port'],
                user=self.mysql_settings['user'],
                password=self.mysql_settings['password'],
                database=self.mysql_settings['database'],
                charset='utf8mb4',
                autocommit=False
            )
            self.mysql_cursor = self.mysql_connection.cursor()
            spider.logger.info(f"MySQL连接成功: {self.mysql_settings['host']}")
            
            # 创建备份表
            self.create_backup_table(spider)
            
        except Exception as e:
            spider.logger.error(f"MySQL连接失败: {e}")
        
        # 建立MongoDB连接
        try:
            mongoengine.disconnect()
            self.mongo_connection = mongoengine.connect(
                db=self.mongo_settings['database'],
                host=self.mongo_settings['host'],
                port=self.mongo_settings['port'],
                serverSelectionTimeoutMS=5000
            )
            spider.logger.info(f"MongoDB连接成功: {self.mongo_settings['host']}")
            
        except Exception as e:
            spider.logger.error(f"MongoDB连接失败: {e}")
    
    def close_spider(self, spider):
        """爬虫结束时关闭双重连接"""
        if self.mysql_cursor:
            self.mysql_cursor.close()
        if self.mysql_connection:
            self.mysql_connection.close()
            spider.logger.info("MySQL连接已关闭")
            
        if self.mongo_connection:
            mongoengine.disconnect()
            spider.logger.info("MongoDB连接已关闭")
    
    def create_backup_table(self, spider):
        """创建MySQL备份表"""
        try:
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS House_dual_write (
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
                mongo_id VARCHAR(100),
                write_status VARCHAR(50) DEFAULT 'success',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
            self.mysql_cursor.execute(create_table_sql)
            self.mysql_connection.commit()
            spider.logger.info("双写备份表 House_dual_write 创建成功")
        except Exception as e:
            spider.logger.error(f"创建双写备份表失败: {e}")
    
    def process_item(self, item, spider):
        """双写处理数据项"""
        adapter = ItemAdapter(item)
        mysql_success = False
        mongo_success = False
        mongo_id = None
        
        # 写入MongoDB
        try:
            # 使用数据适配器确保数据格式正确
            item_dict = dict(adapter)

            # 应用数据适配（如果需要）
            if hasattr(item_dict.get('type', ''), 'strip'):
                # 对于新爬取的数据，应用基本的数据清理
                item_dict['type'] = item_dict.get('type', '').strip()
                item_dict['link'] = item_dict.get('link', '').strip()

                # 确保URL格式正确
                if item_dict['link'] and not item_dict['link'].startswith('http'):
                    if item_dict['link'].startswith('/'):
                        item_dict['link'] = f"https://gz.lianjia.com{item_dict['link']}"
                    else:
                        item_dict['link'] = f"https://gz.lianjia.com/{item_dict['link']}"

            mongo_doc = DataMapper.scrapy_item_to_mongo(item_dict)
            mongo_doc.save()
            mongo_id = str(mongo_doc.id)
            mongo_success = True
            spider.logger.debug(f"MongoDB写入成功: {mongo_doc.title}")
        except Exception as e:
            spider.logger.error(f"MongoDB写入失败: {e}")
        
        # 写入MySQL
        try:
            insert_sql = """
            INSERT INTO House_dual_write (
                title, type, building, city, street, area, direct, price, 
                link, tag, img, crawl_time, spider_name, crawl_id, data_quality, mongo_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            data = (
                adapter.get('title', ''),
                adapter.get('type', ''),
                adapter.get('building', ''),
                adapter.get('city', ''),
                adapter.get('street', ''),
                adapter.get('area', 0),
                adapter.get('direct', ''),
                adapter.get('price', 0),
                adapter.get('link', ''),
                adapter.get('tag', ''),
                adapter.get('img', ''),
                adapter.get('crawl_time', datetime.now()),
                adapter.get('spider_name', ''),
                adapter.get('crawl_id', ''),
                adapter.get('data_quality', 0),
                mongo_id
            )
            
            self.mysql_cursor.execute(insert_sql, data)
            self.mysql_connection.commit()
            mysql_success = True
            spider.logger.debug(f"MySQL写入成功: {adapter.get('title', 'Unknown')}")
            
        except Exception as e:
            spider.logger.error(f"MySQL写入失败: {e}")
            if self.mysql_connection:
                self.mysql_connection.rollback()
        
        # 记录双写状态
        write_status = "success"
        if not mysql_success and not mongo_success:
            write_status = "both_failed"
        elif not mysql_success:
            write_status = "mysql_failed"
        elif not mongo_success:
            write_status = "mongo_failed"
        
        # 更新写入状态
        if mysql_success:
            try:
                update_sql = "UPDATE House_dual_write SET write_status = %s WHERE mongo_id = %s"
                self.mysql_cursor.execute(update_sql, (write_status, mongo_id))
                self.mysql_connection.commit()
            except Exception as e:
                spider.logger.error(f"更新写入状态失败: {e}")
        
        spider.logger.info(f"双写完成 - MySQL: {'✅' if mysql_success else '❌'}, "
                          f"MongoDB: {'✅' if mongo_success else '❌'}")
        
        return item


class DataConsistencyPipeline:
    """数据一致性检查管道"""
    
    def __init__(self):
        self.processed_count = 0
        self.mysql_success_count = 0
        self.mongo_success_count = 0
        self.both_success_count = 0
        
    def process_item(self, item, spider):
        """检查数据一致性"""
        self.processed_count += 1
        
        # 这里可以添加数据一致性检查逻辑
        # 比如验证MySQL和MongoDB中的数据是否一致
        
        return item
    
    def close_spider(self, spider):
        """爬虫结束时输出统计信息"""
        spider.logger.info("=" * 50)
        spider.logger.info("双写统计信息")
        spider.logger.info("=" * 50)
        spider.logger.info(f"总处理数据: {self.processed_count}")
        spider.logger.info(f"双写成功率: {self.both_success_count}/{self.processed_count}")
        
        if self.processed_count > 0:
            success_rate = (self.both_success_count / self.processed_count) * 100
            spider.logger.info(f"成功率: {success_rate:.2f}%")
