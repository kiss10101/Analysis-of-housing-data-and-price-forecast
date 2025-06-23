# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import logging
from itemadapter import ItemAdapter
from datetime import datetime


class MongoPipeline:
    """MongoDB存储管道"""

    def __init__(self, mongo_uri, mongo_db, collection_name):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.collection_name = collection_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI", "mongodb://localhost:27017/"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "house_data"),
            collection_name=crawler.settings.get("MONGO_COLLECTION", "houses")
        )

    def open_spider(self, spider):
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db]
            self.collection = self.db[self.collection_name]
            spider.logger.info(f"MongoDB连接成功: {self.mongo_uri}")
        except Exception as e:
            spider.logger.error(f"MongoDB连接失败: {e}")

    def close_spider(self, spider):
        if hasattr(self, 'client'):
            self.client.close()

    def process_item(self, item, spider):
        try:
            # 转换为字典
            item_dict = ItemAdapter(item).asdict()

            # 添加处理时间
            item_dict['processed_time'] = datetime.now().isoformat()

            # 插入MongoDB
            result = self.collection.insert_one(item_dict)
            spider.logger.info(f"数据已保存到MongoDB: {result.inserted_id}")

            return item
        except Exception as e:
            spider.logger.error(f"保存到MongoDB失败: {e}")
            return item


class MySQLPipeline:
    """MySQL存储管道（用于性能对比）"""

    def __init__(self, mysql_host, mysql_port, mysql_user, mysql_password, mysql_db):
        self.mysql_host = mysql_host
        self.mysql_port = mysql_port
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.mysql_db = mysql_db

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
        try:
            import pymysql
            self.connection = pymysql.connect(
                host=self.mysql_host,
                port=self.mysql_port,
                user=self.mysql_user,
                password=self.mysql_password,
                database=self.mysql_db,
                charset='utf8mb4'
            )
            self.cursor = self.connection.cursor()
            spider.logger.info("MySQL连接成功")
        except Exception as e:
            spider.logger.error(f"MySQL连接失败: {e}")

    def close_spider(self, spider):
        if hasattr(self, 'connection'):
            self.connection.close()

    def process_item(self, item, spider):
        try:
            # 插入MySQL（使用现有表结构）
            insert_query = """
            INSERT INTO house_test (title, type, building, city, street, area, direct, price, link, tag, img, crawl_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            data = (
                item.get('title', ''),
                item.get('type', ''),
                item.get('building', ''),
                item.get('city', ''),
                item.get('street', ''),
                item.get('area', 0),
                item.get('direct', ''),
                item.get('price', 0),
                item.get('link', ''),
                item.get('tag', ''),
                item.get('img', ''),
                item.get('crawl_time', datetime.now().isoformat())
            )

            self.cursor.execute(insert_query, data)
            self.connection.commit()
            spider.logger.info("数据已保存到MySQL")

            return item
        except Exception as e:
            spider.logger.error(f"保存到MySQL失败: {e}")
            return item


class ValidationPipeline:
    """数据验证管道"""

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # 验证必填字段
        required_fields = ['title', 'price', 'city']
        for field in required_fields:
            if not adapter.get(field):
                spider.logger.warning(f"缺少必填字段: {field}")

        # 数据清洗
        if adapter.get('price'):
            try:
                adapter['price'] = float(adapter['price'])
            except:
                adapter['price'] = 0.0

        if adapter.get('area'):
            try:
                adapter['area'] = float(adapter['area'])
            except:
                adapter['area'] = 0.0

        return item
