# Scrapy项目设置
# 房源数据分析系统 - 生产级配置

BOT_NAME = "house_spider"

SPIDER_MODULES = ["house_spider.spiders"]
NEWSPIDER_MODULE = "house_spider.spiders"

# 遵守robots.txt规则
ROBOTSTXT_OBEY = False

# 并发设置
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# 下载延迟设置 (秒)
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = 0.5

# 请求头设置
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

# 中间件设置
DOWNLOADER_MIDDLEWARES = {
    'house_spider.middlewares.RotateUserAgentMiddleware': 400,
    'house_spider.middlewares.CustomRetryMiddleware': 550,
    'house_spider.middlewares.RequestLoggingMiddleware': 600,
    'house_spider.middlewares.AntiSpiderMiddleware': 700,
}

# 数据管道设置
ITEM_PIPELINES = {
    'house_spider.pipelines.ValidationPipeline': 200,
    'house_spider.pipelines.DuplicatesPipeline': 300,
    'house_spider.pipelines.MySQLPipeline': 400,
    'house_spider.pipelines.StatisticsPipeline': 500,
}

# 重试设置
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429, 403]

# 超时设置
DOWNLOAD_TIMEOUT = 30

# 缓存设置
HTTPCACHE_ENABLED = False

# 日志设置
LOG_LEVEL = 'INFO'
LOG_FILE = 'scrapy_spider.log'

# 数据库配置
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'
MYSQL_DATABASE = 'guangzhou_house'

# 自动限速设置
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

# 内存使用监控
MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 2048
MEMUSAGE_WARNING_MB = 1024

# 统计收集
STATS_CLASS = 'scrapy.statscollectors.MemoryStatsCollector'

# Telnet控制台 (调试用)
TELNETCONSOLE_ENABLED = False

# 扩展设置
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'scrapy.extensions.memusage.MemoryUsage': 500,
    'scrapy.extensions.statsmailer.StatsMailer': 500,
}

# 请求指纹过滤
DUPEFILTER_CLASS = 'scrapy.dupefilters.RFPDupeFilter'

# Feed导出设置 (可选)
FEEDS = {
    'output/houses_%(time)s.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'fields': ['title', 'type', 'building', 'city', 'street', 'area', 'direct', 'price', 'link', 'tag', 'img'],
    },
}
