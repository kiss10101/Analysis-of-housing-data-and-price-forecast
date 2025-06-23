# 房源数据项定义
# 与现有MySQL表结构完全兼容

import scrapy


class HouseItem(scrapy.Item):
    """房源数据项 - 兼容现有MySQL表结构"""
    
    # 基本信息字段 (与现有House表字段对应)
    title = scrapy.Field()          # 房源名称
    type = scrapy.Field()           # 房源类型（整租/合租）
    building = scrapy.Field()       # 房源地址/建筑
    city = scrapy.Field()           # 行政区
    street = scrapy.Field()         # 街道
    area = scrapy.Field()           # 房源面积
    direct = scrapy.Field()         # 朝向
    price = scrapy.Field()          # 价格
    link = scrapy.Field()           # 详情链接
    tag = scrapy.Field()            # 标签
    img = scrapy.Field()            # 图片链接
    
    # 扩展字段 (为未来MongoDB升级预留)
    crawl_time = scrapy.Field()     # 爬取时间
    spider_name = scrapy.Field()    # 爬虫名称
    source_url = scrapy.Field()     # 数据源URL
    
    # 元数据
    crawl_id = scrapy.Field()       # 爬取批次ID
    data_quality = scrapy.Field()   # 数据质量评分
