#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB数据模型定义
房源数据分析系统 - 第二阶段
"""

from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime
import uuid

class LocationInfo(EmbeddedDocument):
    """地理位置信息（嵌套文档）"""
    # 基础位置信息
    city = fields.StringField(max_length=100, required=True)  # 城市区域
    street = fields.StringField(max_length=200)               # 街道
    building = fields.StringField(max_length=200)             # 建筑名称
    
    # 详细地址信息
    full_address = fields.StringField(max_length=500)         # 完整地址
    district = fields.StringField(max_length=100)             # 行政区
    subway_info = fields.ListField(fields.StringField())      # 地铁信息
    
    # 地理坐标（为未来地理查询预留）
    coordinates = fields.PointField()                         # GeoJSON点坐标
    
    # 周边设施
    nearby_facilities = fields.ListField(fields.StringField()) # 周边设施

class PriceInfo(EmbeddedDocument):
    """价格信息（嵌套文档）"""
    # 基础价格
    monthly_rent = fields.DecimalField(min_value=0, precision=2, required=True)  # 月租金
    deposit = fields.DecimalField(min_value=0, precision=2)                      # 押金
    service_fee = fields.DecimalField(min_value=0, precision=2)                  # 服务费
    
    # 价格详情
    price_per_sqm = fields.DecimalField(min_value=0, precision=2)                # 每平米价格
    utilities_included = fields.BooleanField(default=False)                     # 是否包含水电
    internet_included = fields.BooleanField(default=False)                      # 是否包含网络
    
    # 价格历史（为价格趋势分析预留）
    price_history = fields.ListField(fields.EmbeddedDocumentField('PriceRecord'))

class PriceRecord(EmbeddedDocument):
    """价格记录（用于价格历史）"""
    price = fields.DecimalField(min_value=0, precision=2, required=True)
    recorded_at = fields.DateTimeField(default=datetime.now)
    source = fields.StringField(max_length=100)

class HouseFeatures(EmbeddedDocument):
    """房屋特征信息（嵌套文档）"""
    # 基础特征
    area = fields.DecimalField(min_value=0, precision=2, required=True)  # 面积
    room_type = fields.StringField(max_length=50, required=True)         # 房型（如：1室1厅）
    direction = fields.StringField(max_length=50)                       # 朝向
    floor_info = fields.StringField(max_length=100)                     # 楼层信息
    
    # 详细特征
    decoration = fields.StringField(max_length=100)                     # 装修情况
    furniture = fields.ListField(fields.StringField())                  # 家具列表
    appliances = fields.ListField(fields.StringField())                 # 家电列表
    
    # 房屋条件
    has_elevator = fields.BooleanField()                                # 是否有电梯
    has_balcony = fields.BooleanField()                                 # 是否有阳台
    has_parking = fields.BooleanField()                                 # 是否有停车位
    pet_allowed = fields.BooleanField()                                 # 是否允许宠物

class ContactInfo(EmbeddedDocument):
    """联系信息（嵌套文档）"""
    contact_person = fields.StringField(max_length=100)                 # 联系人
    phone = fields.StringField(max_length=50)                          # 电话
    wechat = fields.StringField(max_length=100)                        # 微信
    agency = fields.StringField(max_length=200)                        # 中介公司
    agent_name = fields.StringField(max_length=100)                    # 经纪人姓名

class CrawlMetadata(EmbeddedDocument):
    """爬取元数据（嵌套文档）"""
    spider_name = fields.StringField(max_length=100, required=True)     # 爬虫名称
    crawl_id = fields.StringField(max_length=100, required=True)        # 爬取批次ID
    crawl_time = fields.DateTimeField(default=datetime.now, required=True) # 爬取时间
    source_url = fields.URLField(required=True)                        # 数据源URL
    data_quality = fields.IntField(min_value=0, max_value=100, default=0) # 数据质量评分
    
    # 爬取状态
    is_active = fields.BooleanField(default=True)                      # 是否有效
    last_updated = fields.DateTimeField(default=datetime.now)          # 最后更新时间
    update_count = fields.IntField(default=1)                          # 更新次数

class HouseDocument(Document):
    """房源文档模型（主文档）"""
    
    # 基础标识信息
    title = fields.StringField(max_length=300, required=True)           # 房源标题
    house_id = fields.StringField(max_length=100, unique=True)          # 房源唯一ID
    rental_type = fields.StringField(max_length=50, required=True,      # 租赁类型
                                    choices=['整租', '合租', '单间'])
    
    # 嵌套文档
    location = fields.EmbeddedDocumentField(LocationInfo, required=True) # 位置信息
    price = fields.EmbeddedDocumentField(PriceInfo, required=True)       # 价格信息
    features = fields.EmbeddedDocumentField(HouseFeatures, required=True) # 房屋特征
    contact = fields.EmbeddedDocumentField(ContactInfo)                  # 联系信息
    crawl_meta = fields.EmbeddedDocumentField(CrawlMetadata, required=True) # 爬取元数据
    
    # 媒体信息
    images = fields.ListField(fields.URLField())                        # 图片链接列表
    virtual_tour = fields.URLField()                                    # 虚拟看房链接
    
    # 标签和分类
    tags = fields.ListField(fields.StringField(max_length=50))          # 标签列表
    category = fields.StringField(max_length=100)                       # 分类
    
    # 状态信息
    status = fields.StringField(max_length=50, default='available',     # 房源状态
                               choices=['available', 'rented', 'offline'])
    
    # 时间戳
    created_at = fields.DateTimeField(default=datetime.now)             # 创建时间
    updated_at = fields.DateTimeField(default=datetime.now)             # 更新时间
    
    # 索引定义
    meta = {
        'collection': 'houses',
        'indexes': [
            'house_id',
            'rental_type',
            'location.city',
            'price.monthly_rent',
            'features.area',
            'status',
            'created_at',
            ('location.city', 'price.monthly_rent'),  # 复合索引
            ('location.city', 'features.area'),       # 复合索引
            ('rental_type', 'status'),                # 复合索引
            {
                'fields': ['location.coordinates'],
                'cls': False,
                'sparse': True
            },  # 地理位置索引
        ],
        'ordering': ['-created_at']  # 默认按创建时间倒序
    }
    
    def __str__(self):
        return f"{self.title} - {self.location.city} - ¥{self.price.monthly_rent}"
    
    def save(self, *args, **kwargs):
        """重写保存方法，自动更新时间戳"""
        self.updated_at = datetime.now()
        if not self.house_id:
            self.house_id = str(uuid.uuid4())
        return super().save(*args, **kwargs)
    
    @classmethod
    def from_scrapy_item(cls, item):
        """从Scrapy Item创建MongoDB文档"""
        # 创建嵌套文档
        location = LocationInfo(
            city=item.get('city', ''),
            street=item.get('street', ''),
            building=item.get('building', '')
        )
        
        price = PriceInfo(
            monthly_rent=float(item.get('price', 0))
        )
        
        features = HouseFeatures(
            area=float(item.get('area', 0)),
            room_type=item.get('type', ''),
            direction=item.get('direct', '')
        )
        
        crawl_meta = CrawlMetadata(
            spider_name=item.get('spider_name', ''),
            crawl_id=item.get('crawl_id', ''),
            source_url=item.get('link', ''),
            data_quality=item.get('data_quality', 0)
        )
        
        # 创建主文档
        house = cls(
            title=item.get('title', ''),
            rental_type=item.get('type', ''),
            location=location,
            price=price,
            features=features,
            crawl_meta=crawl_meta,
            tags=item.get('tag', '').split(',') if item.get('tag') else [],
            images=[item.get('img')] if item.get('img') else []
        )
        
        return house
    
    def to_mysql_dict(self):
        """转换为MySQL兼容的字典格式"""
        return {
            'title': self.title,
            'type': self.rental_type,
            'building': self.location.building,
            'city': self.location.city,
            'street': self.location.street,
            'area': float(self.features.area),
            'direct': self.features.direction,
            'price': float(self.price.monthly_rent),
            'link': self.crawl_meta.source_url,
            'tag': ','.join(self.tags),
            'img': self.images[0] if self.images else '',
            'crawl_time': self.crawl_meta.crawl_time,
            'spider_name': self.crawl_meta.spider_name,
            'crawl_id': self.crawl_meta.crawl_id,
            'data_quality': self.crawl_meta.data_quality
        }
