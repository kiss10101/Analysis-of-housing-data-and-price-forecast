import scrapy
import time
import uuid
from datetime import datetime
from house_spider.items import HouseItem


class LianjiaSpider(scrapy.Spider):
    """链家租房爬虫 - 生产级实现"""
    
    name = 'lianjia'
    allowed_domains = ['gz.lianjia.com']
    
    # 起始URL - 支持多页面爬取
    start_urls = []
    
    # 自定义设置
    custom_settings = {
        'DOWNLOAD_DELAY': 2,  # 下载延迟2秒
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,  # 随机延迟0.5倍
        'CONCURRENT_REQUESTS': 2,  # 并发请求数
        'ROBOTSTXT_OBEY': False,  # 忽略robots.txt
        'RETRY_TIMES': 3,  # 重试次数
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],
    }
    
    def __init__(self, pages=5, *args, **kwargs):
        super(LianjiaSpider, self).__init__(*args, **kwargs)
        self.crawl_id = str(uuid.uuid4())
        self.pages = int(pages)
        
        # 生成起始URL
        self.start_urls = [
            f'https://gz.lianjia.com/zufang/pg{i}/#contentList' 
            for i in range(1, self.pages + 1)
        ]
        
        self.logger.info(f"初始化爬虫，爬取页数: {self.pages}, 批次ID: {self.crawl_id}")
        
    def parse(self, response):
        """解析房源列表页"""
        self.logger.info(f"正在解析页面: {response.url}")
        
        # 提取房源信息
        house_items = response.xpath('//*[@id="content"]/div[1]/div[1]/div')
        
        if not house_items:
            self.logger.warning(f"页面无房源数据: {response.url}")
            return
            
        self.logger.info(f"找到 {len(house_items)} 个房源")
        
        for i, house in enumerate(house_items):
            try:
                item = self.extract_house_data(house, response.url, i)
                if item:
                    yield item
            except Exception as e:
                self.logger.error(f"解析第{i+1}个房源失败: {e}")
                continue
                
    def extract_house_data(self, house_selector, source_url, index):
        """提取单个房源数据"""
        try:
            item = HouseItem()
            
            # 房源名称和链接
            name_link = house_selector.xpath('./div/p[1]/a')
            if not name_link:
                return None
                
            name = name_link.xpath('./text()').get('').strip()
            link = name_link.xpath('./@href').get('')
            
            if not name:
                return None
                
            # 解析房源名称 (格式: "整租·建设大马路123号 2室1厅")
            name_parts = name.split('·')
            item['type'] = name_parts[0] if len(name_parts) > 0 else ''
            
            if len(name_parts) > 1:
                building_parts = name_parts[1].split(' ')
                item['title'] = building_parts[0] if len(building_parts) > 0 else ''
                item['building'] = building_parts[1] if len(building_parts) > 1 else building_parts[0]
            else:
                item['title'] = name
                item['building'] = ''
            
            # 位置信息
            location_info = house_selector.xpath('./div/p[2]/a/text()').getall()
            item['city'] = location_info[0] if len(location_info) > 0 else ''
            item['street'] = location_info[1] if len(location_info) > 1 else ''
            
            # 房屋详细信息
            detail_texts = house_selector.xpath('./div/p[2]/text()').getall()
            
            # 面积 (第5个text节点)
            area_text = detail_texts[4] if len(detail_texts) > 4 else ''
            area_clean = area_text.replace('㎡', '').replace('\n', '').replace(' ', '').strip()
            try:
                item['area'] = float(area_clean) if area_clean and '.' in area_clean else 80.0
            except:
                item['area'] = 80.0
                
            # 朝向 (第6个text节点)
            direct_text = detail_texts[5] if len(detail_texts) > 5 else ''
            item['direct'] = direct_text.replace('㎡', '').strip()
            
            # 价格
            price_text = house_selector.xpath('./div/span/em/text()').get('')
            try:
                item['price'] = float(price_text) if price_text else 0.0
            except:
                item['price'] = 0.0
                
            # 标签
            tag_text = house_selector.xpath('./div/p[3]/i[1]/text()').get('')
            item['tag'] = tag_text.strip() if tag_text else ''
            
            # 图片
            img_url = house_selector.xpath('./a/img/@data-src').get('')
            item['img'] = img_url if img_url else ''
            
            # 链接
            item['link'] = link
            
            # 元数据
            item['crawl_time'] = datetime.now().isoformat()
            item['spider_name'] = self.name
            item['source_url'] = source_url
            item['crawl_id'] = self.crawl_id
            item['data_quality'] = self.calculate_data_quality(item)
            
            return item
            
        except Exception as e:
            self.logger.error(f"提取房源数据失败: {e}")
            return None
            
    def calculate_data_quality(self, item):
        """计算数据质量评分 (0-100)"""
        score = 0
        total_fields = 11  # 主要字段数量
        
        # 检查必填字段
        required_fields = ['title', 'type', 'city', 'price']
        for field in required_fields:
            if item.get(field):
                score += 25
                
        # 检查可选字段
        optional_fields = ['building', 'street', 'area', 'direct', 'tag', 'img', 'link']
        for field in optional_fields:
            if item.get(field):
                score += 7
                
        return min(score, 100)
