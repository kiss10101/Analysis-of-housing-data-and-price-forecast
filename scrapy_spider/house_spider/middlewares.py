# 中间件定义
# 包含User-Agent轮换、错误处理等功能

import random
import logging
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware


class RotateUserAgentMiddleware(UserAgentMiddleware):
    """User-Agent轮换中间件"""
    
    def __init__(self, user_agent=''):
        self.user_agent = user_agent
        self.user_agent_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        ]
        
    def process_request(self, request, spider):
        ua = random.choice(self.user_agent_list)
        request.headers['User-Agent'] = ua
        spider.logger.debug(f"使用User-Agent: {ua}")
        return None


class CustomRetryMiddleware(RetryMiddleware):
    """自定义重试中间件"""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.max_retry_times = settings.getint('RETRY_TIMES', 3)
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        
    def process_response(self, request, response, spider):
        if response.status in self.retry_http_codes:
            reason = f'HTTP {response.status}'
            spider.logger.warning(f"重试请求 {request.url}: {reason}")
            return self._retry(request, reason, spider) or response
        return response
        
    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
            spider.logger.warning(f"重试请求 {request.url}: {exception}")
            return self._retry(request, exception, spider)


class RequestLoggingMiddleware:
    """请求日志中间件"""
    
    def process_request(self, request, spider):
        spider.logger.debug(f"发送请求: {request.url}")
        return None
        
    def process_response(self, request, response, spider):
        spider.logger.debug(f"收到响应: {response.url} [{response.status}]")
        return response
        
    def process_exception(self, request, exception, spider):
        spider.logger.error(f"请求异常: {request.url} - {exception}")
        return None


class AntiSpiderMiddleware:
    """反爬虫中间件"""
    
    def __init__(self):
        self.request_count = 0
        
    def process_request(self, request, spider):
        self.request_count += 1
        
        # 每50个请求增加额外延迟
        if self.request_count % 50 == 0:
            spider.logger.info(f"已发送 {self.request_count} 个请求，增加延迟...")
            import time
            time.sleep(5)
            
        return None
