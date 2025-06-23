# 数据管道定义
# 包含数据清洗、验证、存储等功能

import pymysql
import logging
from datetime import datetime
from itemadapter import ItemAdapter


class ValidationPipeline:
    """数据验证管道"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # 验证必填字段
        required_fields = ['title', 'price', 'city']
        for field in required_fields:
            if not adapter.get(field):
                spider.logger.warning(f"缺少必填字段 {field}: {dict(adapter)}")
                
        # 数据清洗和标准化
        self.clean_data(adapter, spider)
        
        return item
        
    def clean_data(self, adapter, spider):
        """数据清洗"""
        try:
            # 价格数据清洗
            if adapter.get('price'):
                try:
                    adapter['price'] = float(adapter['price'])
                except:
                    adapter['price'] = 0.0
                    
            # 面积数据清洗
            if adapter.get('area'):
                try:
                    adapter['area'] = float(adapter['area'])
                except:
                    adapter['area'] = 0.0
                    
            # 文本字段清洗
            text_fields = ['title', 'type', 'building', 'city', 'street', 'direct', 'tag']
            for field in text_fields:
                if adapter.get(field):
                    adapter[field] = str(adapter[field]).strip()
                    
        except Exception as e:
            spider.logger.error(f"数据清洗失败: {e}")


class DuplicatesPipeline:
    """去重管道"""
    
    def __init__(self):
        self.seen_items = set()
        
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # 生成唯一标识 (基于标题+价格+城市)
        item_id = f"{adapter.get('title', '')}_{adapter.get('price', 0)}_{adapter.get('city', '')}"
        
        if item_id in self.seen_items:
            spider.logger.info(f"发现重复数据: {item_id}")
            return None
        else:
            self.seen_items.add(item_id)
            return item


class MySQLPipeline:
    """MySQL存储管道 - 兼容现有表结构"""
    
    def __init__(self, mysql_host, mysql_port, mysql_user, mysql_password, mysql_db):
        self.mysql_host = mysql_host
        self.mysql_port = mysql_port
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.mysql_db = mysql_db
        self.connection = None
        self.cursor = None
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_host=crawler.settings.get("MYSQL_HOST", "localhost"),
            mysql_port=crawler.settings.get("MYSQL_PORT", 3306),
            mysql_user=crawler.settings.get("MYSQL_USER", "root"),
            mysql_password=crawler.settings.get("MYSQL_PASSWORD", "123456"),
            mysql_db=crawler.settings.get("MYSQL_DATABASE", "guangzhou_house")
        )
        
    def open_spider(self, spider):
        """爬虫开始时建立数据库连接"""
        try:
            self.connection = pymysql.connect(
                host=self.mysql_host,
                port=self.mysql_port,
                user=self.mysql_user,
                password=self.mysql_password,
                database=self.mysql_db,
                charset='utf8mb4',
                autocommit=False
            )
            self.cursor = self.connection.cursor()
            spider.logger.info(f"MySQL连接成功: {self.mysql_host}:{self.mysql_port}/{self.mysql_db}")
            
            # 创建备份表 (如果不存在)
            self.create_backup_table(spider)
            
        except Exception as e:
            spider.logger.error(f"MySQL连接失败: {e}")
            
    def close_spider(self, spider):
        """爬虫结束时关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        spider.logger.info("MySQL连接已关闭")
        
    def create_backup_table(self, spider):
        """创建备份表用于存储Scrapy爬取的数据"""
        try:
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS House_scrapy (
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
            self.cursor.execute(create_table_sql)
            self.connection.commit()
            spider.logger.info("备份表 House_scrapy 创建成功")
        except Exception as e:
            spider.logger.error(f"创建备份表失败: {e}")
            
    def process_item(self, item, spider):
        """处理数据项"""
        try:
            adapter = ItemAdapter(item)
            
            # 插入到备份表
            insert_sql = """
            INSERT INTO House_scrapy (
                title, type, building, city, street, area, direct, price, 
                link, tag, img, crawl_time, spider_name, crawl_id, data_quality
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                adapter.get('crawl_time', datetime.now().isoformat()),
                adapter.get('spider_name', ''),
                adapter.get('crawl_id', ''),
                adapter.get('data_quality', 0)
            )
            
            self.cursor.execute(insert_sql, data)
            self.connection.commit()
            
            spider.logger.debug(f"数据已保存到MySQL: {adapter.get('title', 'Unknown')}")
            
            return item
            
        except Exception as e:
            spider.logger.error(f"保存到MySQL失败: {e}")
            if self.connection:
                self.connection.rollback()
            return item


class StatisticsPipeline:
    """统计管道"""
    
    def __init__(self):
        self.item_count = 0
        self.error_count = 0
        
    def process_item(self, item, spider):
        self.item_count += 1
        
        # 每100条记录输出一次统计
        if self.item_count % 100 == 0:
            spider.logger.info(f"已处理 {self.item_count} 条数据，错误 {self.error_count} 条")
            
        return item
        
    def close_spider(self, spider):
        spider.logger.info(f"爬取完成 - 总计: {self.item_count} 条数据，错误: {self.error_count} 条")
