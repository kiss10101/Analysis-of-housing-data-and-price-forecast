import scrapy
import time
import uuid
from datetime import datetime
from house_spider.items import HouseItem


class LianjiaSpider(scrapy.Spider):
    name = 'lianjia'
    allowed_domains = ['gz.lianjia.com']
    start_urls = [
        'https://gz.lianjia.com/zufang/pg1/#contentList',
        'https://gz.lianjia.com/zufang/pg2/#contentList',
        'https://gz.lianjia.com/zufang/pg3/#contentList',
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,  # 下载延迟
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,  # 随机延迟
        'CONCURRENT_REQUESTS': 1,  # 并发请求数
        'ROBOTSTXT_OBEY': False,  # 忽略robots.txt
    }
    
    def __init__(self):
        self.crawl_id = str(uuid.uuid4())
        
    def parse(self, response):
        """解析房源列表页"""
        # 房源名称
        names = response.xpath('//*[@id="content"]/div[1]/div[1]/div/div/p[1]/a/text()').getall()
        # 详情链接
        hrefs = response.xpath('//*[@id="content"]/div[1]/div[1]/div/div/p[1]/a/@href').getall()
        # 标签
        tags = response.xpath('//*[@id="content"]/div[1]/div[1]/div/div/p[3]/i[1]/text()').getall()
        # 所在区
        districts = response.xpath('//*[@id="content"]/div[1]/div[1]/div/div/p[2]/a[1]/text()').getall()
        # 所在路
        streets = response.xpath('//*[@id="content"]/div[1]/div[1]/div/div/p[2]/a[2]/text()').getall()
        # 房屋面积
        floor_spaces = response.xpath('//*[@id="content"]/div[1]/div[1]/div/div/p[2]/text()[5]').getall()
        # 朝向
        orientations = response.xpath('//*[@id="content"]/div[1]/div[1]/div/div/p[2]/text()[6]').getall()
        # 房型
        house_types = response.xpath('//*[@id="content"]/div[1]/div[1]/div/div/p[2]/text()[7]').getall()
        # 价格
        prices = response.xpath('//*[@id="content"]/div[1]/div[1]/div/div/span/em/text()').getall()
        # 图片
        imgs = response.xpath('//*[@id="content"]/div[1]/div[1]/div/a/img/@data-src').getall()
        
        # 处理数据
        for i in range(len(names)):
            try:
                item = HouseItem()
                
                # 解析房源名称
                name_parts = names[i].split('·')
                item['type'] = name_parts[0] if len(name_parts) > 0 else ''
                
                if len(name_parts) > 1:
                    building_parts = name_parts[1].split(' ')
                    item['title'] = building_parts[0] if len(building_parts) > 0 else ''
                    item['building'] = building_parts[1] if len(building_parts) > 1 else building_parts[0]
                else:
                    item['title'] = names[i]
                    item['building'] = ''
                
                # 基本信息
                item['city'] = districts[i] if i < len(districts) else ''
                item['street'] = streets[i] if i < len(streets) else ''
                
                # 处理面积
                if i < len(floor_spaces):
                    area_str = floor_spaces[i].strip().replace('㎡', '').replace('\n', '').replace(' ', '')
                    try:
                        item['area'] = float(area_str) if '.' in area_str else 80.0
                    except:
                        item['area'] = 80.0
                else:
                    item['area'] = 80.0
                
                # 朝向
                item['direct'] = orientations[i].strip().replace('㎡', '') if i < len(orientations) else ''
                
                # 房型
                item['type'] = house_types[i].strip() if i < len(house_types) else item['type']
                
                # 价格
                try:
                    item['price'] = float(prices[i]) if i < len(prices) else 0.0
                except:
                    item['price'] = 0.0
                
                # 链接和图片
                item['link'] = hrefs[i] if i < len(hrefs) else ''
                item['tag'] = tags[i] if i < len(tags) else ''
                item['img'] = imgs[i] if i < len(imgs) else ''
                
                # 扩展信息（MongoDB优势）
                item['location'] = {'lat': 0, 'lng': 0}  # 可以后续通过地址解析获取
                item['facilities'] = []  # 设施信息
                item['description'] = f"{item['type']} {item['title']} {item['building']}"
                item['contact_info'] = {}
                item['crawl_time'] = datetime.now().isoformat()
                item['source_url'] = response.url
                item['spider_name'] = self.name
                item['crawl_id'] = self.crawl_id
                
                yield item
                
            except Exception as e:
                self.logger.error(f"解析第{i+1}条数据时出错: {e}")
                continue
