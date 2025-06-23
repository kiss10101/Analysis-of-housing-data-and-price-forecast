# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HouseItem(scrapy.Item):
    """房源数据项"""
    # 基本信息
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

    # 扩展信息（MongoDB优势体现）
    location = scrapy.Field()       # 地理位置坐标
    facilities = scrapy.Field()     # 设施列表
    description = scrapy.Field()    # 详细描述
    contact_info = scrapy.Field()   # 联系信息
    crawl_time = scrapy.Field()     # 爬取时间
    source_url = scrapy.Field()     # 数据源URL

    # 元数据
    spider_name = scrapy.Field()    # 爬虫名称
    crawl_id = scrapy.Field()       # 爬取批次ID
