# Scrapy-Redis分布式爬虫实施代码示例

## 📋 代码改造对比

### 1. 爬虫类改造

**现有代码 (scrapy_spider/house_spider/spiders/lianjia_spider.py)**:
```python
import scrapy
from house_spider.items import HouseItem

class LianjiaSpider(scrapy.Spider):
    """链家租房爬虫 - 单机版"""
    
    name = 'lianjia'
    allowed_domains = ['gz.lianjia.com']
    
    def __init__(self, pages=5, *args, **kwargs):
        super(LianjiaSpider, self).__init__(*args, **kwargs)
        self.pages = int(pages)
        
        # 生成起始URL
        self.start_urls = [
            f'https://gz.lianjia.com/zufang/pg{i}/#contentList' 
            for i in range(1, self.pages + 1)
        ]
```

**分布式改造后**:
```python
import scrapy
from scrapy_redis.spiders import RedisSpider
from house_spider.items import HouseItem

class LianjiaSpider(RedisSpider):
    """链家租房爬虫 - 分布式版"""
    
    name = 'lianjia'
    allowed_domains = ['gz.lianjia.com']
    redis_key = 'lianjia:start_urls'
    
    def __init__(self, *args, **kwargs):
        super(LianjiaSpider, self).__init__(*args, **kwargs)
        
    def make_request_from_data(self, data):
        """从Redis数据创建请求"""
        url = data.decode('utf-8')
        return scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        """解析房源列表页 - 保持不变"""
        # 现有解析逻辑保持不变
        ...
        
        # 新增: 发现新URL时推送到Redis
        for page in range(1, 100):  # 动态发现更多页面
            next_url = f'https://gz.lianjia.com/zufang/pg{page}/#contentList'
            yield scrapy.Request(url=next_url, callback=self.parse)
```

### 2. 配置文件改造

**现有配置 (scrapy_spider/house_spider/settings.py)**:
```python
# 现有配置
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_DELAY = 2

# 去重器
DUPEFILTER_CLASS = 'scrapy.dupefilters.RFPDupeFilter'

# 数据管道
ITEM_PIPELINES = {
    'house_spider.pipelines.ValidationPipeline': 200,
    'house_spider.pipelines.DuplicatesPipeline': 300,
    'house_spider.pipelines.MySQLPipeline': 400,
}
```

**分布式配置**:
```python
# Redis连接配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None
REDIS_PARAMS = {
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'retry_on_timeout': True,
    'health_check_interval': 30,
}

# 分布式调度器
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'
SCHEDULER_DUPEFILTER_KEY = '%(spider)s:dupefilter'
SCHEDULER_DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'

# 分布式去重器
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
DUPEFILTER_DEBUG = True

# 分布式数据管道
ITEM_PIPELINES = {
    'house_spider.pipelines.ValidationPipeline': 200,
    'scrapy_redis.pipelines.RedisPipeline': 300,  # 新增Redis管道
    'house_spider.pipelines.MySQLPipeline': 400,
    'house_spider.pipelines.StatisticsPipeline': 500,
}

# 性能优化配置
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = 0.5

# 分布式特有配置
REDIS_START_URLS_AS_SET = True  # 使用Set存储起始URL
REDIS_START_URLS_KEY = '%(name)s:start_urls'
```

### 3. Docker容器化配置

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  # Redis服务
  redis:
    image: redis:6.2-alpine
    container_name: scrapy_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped
    
  # Redis哨兵 (高可用)
  redis-sentinel:
    image: redis:6.2-alpine
    container_name: scrapy_redis_sentinel
    ports:
      - "26379:26379"
    depends_on:
      - redis
    volumes:
      - ./sentinel.conf:/usr/local/etc/redis/sentinel.conf
    command: redis-sentinel /usr/local/etc/redis/sentinel.conf
    restart: unless-stopped

  # 爬虫节点1
  spider-node-1:
    build: .
    container_name: scrapy_spider_1
    depends_on:
      - redis
      - mysql
      - mongodb
    environment:
      - REDIS_HOST=redis
      - MYSQL_HOST=mysql
      - MONGODB_HOST=mongodb
    volumes:
      - ./scrapy_spider:/app
    command: scrapy crawl lianjia
    restart: unless-stopped

  # 爬虫节点2
  spider-node-2:
    build: .
    container_name: scrapy_spider_2
    depends_on:
      - redis
      - mysql
      - mongodb
    environment:
      - REDIS_HOST=redis
      - MYSQL_HOST=mysql
      - MONGODB_HOST=mongodb
    volumes:
      - ./scrapy_spider:/app
    command: scrapy crawl lianjia
    restart: unless-stopped

  # 爬虫节点3
  spider-node-3:
    build: .
    container_name: scrapy_spider_3
    depends_on:
      - redis
      - mysql
      - mongodb
    environment:
      - REDIS_HOST=redis
      - MYSQL_HOST=mysql
      - MONGODB_HOST=mongodb
    volumes:
      - ./scrapy_spider:/app
    command: scrapy crawl lianjia
    restart: unless-stopped

  # MySQL数据库
  mysql:
    image: mysql:8.0
    container_name: scrapy_mysql
    environment:
      MYSQL_ROOT_PASSWORD: 123456
      MYSQL_DATABASE: guangzhou_house
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped

  # MongoDB数据库
  mongodb:
    image: mongo:5.0
    container_name: scrapy_mongodb
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    restart: unless-stopped

  # 监控服务
  prometheus:
    image: prom/prometheus
    container_name: scrapy_prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    container_name: scrapy_grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

volumes:
  redis_data:
  mysql_data:
  mongodb_data:
  grafana_data:
```

### 4. 启动脚本改造

**分布式启动脚本 (start_distributed_spider.py)**:
```python
#!/usr/bin/env python3
import redis
import argparse
import logging
from scrapy.utils.project import get_project_settings

def setup_redis_urls(redis_client, spider_name, pages=10):
    """设置Redis起始URL"""
    key = f"{spider_name}:start_urls"
    
    # 清空现有URL
    redis_client.delete(key)
    
    # 添加起始URL
    urls = [
        f'https://gz.lianjia.com/zufang/pg{i}/#contentList' 
        for i in range(1, pages + 1)
    ]
    
    for url in urls:
        redis_client.sadd(key, url)
    
    print(f"✅ 已添加 {len(urls)} 个起始URL到Redis")
    return len(urls)

def check_cluster_status(redis_client):
    """检查集群状态"""
    try:
        # 检查Redis连接
        redis_client.ping()
        print("✅ Redis连接正常")
        
        # 检查队列状态
        keys = redis_client.keys("*")
        print(f"📊 Redis中共有 {len(keys)} 个键")
        
        return True
    except Exception as e:
        print(f"❌ 集群状态检查失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='分布式爬虫启动器')
    parser.add_argument('-p', '--pages', type=int, default=10, help='爬取页数')
    parser.add_argument('-s', '--spider', default='lianjia', help='爬虫名称')
    parser.add_argument('--setup', action='store_true', help='设置起始URL')
    parser.add_argument('--status', action='store_true', help='检查集群状态')
    parser.add_argument('--clear', action='store_true', help='清空Redis数据')
    
    args = parser.parse_args()
    
    # 连接Redis
    settings = get_project_settings()
    redis_client = redis.Redis(
        host=settings.get('REDIS_HOST', 'localhost'),
        port=settings.get('REDIS_PORT', 6379),
        db=settings.get('REDIS_DB', 0),
        decode_responses=True
    )
    
    if args.status:
        check_cluster_status(redis_client)
        return
    
    if args.clear:
        redis_client.flushdb()
        print("✅ Redis数据已清空")
        return
    
    if args.setup:
        setup_redis_urls(redis_client, args.spider, args.pages)
        return
    
    print("分布式爬虫集群管理器")
    print("使用 --help 查看可用选项")

if __name__ == '__main__':
    main()
```

### 5. 监控配置

**Prometheus配置 (monitoring/prometheus.yml)**:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'scrapy-spiders'
    static_configs:
      - targets: ['spider-node-1:8000', 'spider-node-2:8000', 'spider-node-3:8000']
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    
  - job_name: 'mysql'
    static_configs:
      - targets: ['mysql:3306']
```

### 6. 新增依赖

**requirements_distributed.txt**:
```
# 现有依赖
Django>=4.0.0
pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.5.0
scikit-learn>=1.0.0
wordcloud>=1.8.0
PyMySQL>=1.0.0
requests>=2.25.0
lxml>=4.6.0
Pillow>=8.0.0
Scrapy>=2.8.0

# 分布式新增依赖
scrapy-redis>=0.7.0
redis>=4.5.0
docker>=6.0.0
docker-compose>=2.0.0

# 监控相关
prometheus-client>=0.15.0
grafana-api>=1.0.3

# 容器化相关
gunicorn>=20.1.0
supervisor>=4.2.0
```

---

## 🚀 部署流程

### 1. 环境准备
```bash
# 安装依赖
pip install -r requirements_distributed.txt

# 启动Redis
docker-compose up -d redis

# 验证Redis连接
python -c "import redis; r=redis.Redis(); print(r.ping())"
```

### 2. 配置部署
```bash
# 设置起始URL
python start_distributed_spider.py --setup --pages 50

# 检查集群状态
python start_distributed_spider.py --status
```

### 3. 启动集群
```bash
# 启动完整集群
docker-compose up -d

# 查看日志
docker-compose logs -f spider-node-1
```

### 4. 监控验证
```bash
# 访问监控面板
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)

# 检查爬虫状态
docker-compose ps
```

---

## 📊 性能对比测试

### 测试脚本
```python
import time
import redis
import pymysql
from datetime import datetime

def performance_test():
    """性能对比测试"""
    
    # 连接Redis
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    # 连接MySQL
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='guangzhou_house'
    )
    
    start_time = datetime.now()
    
    # 监控指标
    while True:
        # Redis队列长度
        queue_len = r.llen('lianjia:requests')
        
        # 已处理请求数
        processed = r.get('lianjia:processed') or 0
        
        # 数据库记录数
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM house_scrapy WHERE crawl_time > %s", [start_time])
        db_count = cursor.fetchone()[0]
        
        print(f"队列长度: {queue_len}, 已处理: {processed}, 数据库: {db_count}")
        time.sleep(10)

if __name__ == '__main__':
    performance_test()
```

这个详细的代码示例展示了从单机Scrapy到分布式Scrapy-Redis的完整改造过程，包括所有必要的配置和部署脚本。
