#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双写机制爬虫测试脚本
使用超保守设置进行小规模爬取测试
"""

import os
import sys
import time
import subprocess
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DualWriteCrawlTest:
    """双写机制爬虫测试"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
    
    def create_conservative_spider_config(self):
        """创建超保守的爬虫配置"""
        
        # 超保守的Scrapy设置
        conservative_settings = {
            'BOT_NAME': 'house_spider_dual_write_test',
            'SPIDER_MODULES': ['house_spider.spiders'],
            'NEWSPIDER_MODULE': 'house_spider.spiders',
            'ROBOTSTXT_OBEY': False,
            
            # 超级保守的性能设置
            'CONCURRENT_REQUESTS': 1,           # 只允许1个并发请求
            'CONCURRENT_REQUESTS_PER_DOMAIN': 1, # 每个域名1个请求
            'DOWNLOAD_DELAY': 8,                # 8秒延迟
            'RANDOMIZE_DOWNLOAD_DELAY': 1.0,    # 随机延迟100%
            'AUTOTHROTTLE_ENABLED': True,       # 启用自动限速
            'AUTOTHROTTLE_START_DELAY': 8,      # 起始延迟8秒
            'AUTOTHROTTLE_MAX_DELAY': 20,       # 最大延迟20秒
            'AUTOTHROTTLE_TARGET_CONCURRENCY': 0.3,  # 目标并发0.3
            'AUTOTHROTTLE_DEBUG': True,         # 显示限速调试信息
            
            # 重试设置
            'RETRY_TIMES': 2,
            'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429, 403],
            'DOWNLOAD_TIMEOUT': 30,
            
            # 请求头设置
            'DEFAULT_REQUEST_HEADERS': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            
            # 中间件 (只启用必要的)
            'DOWNLOADER_MIDDLEWARES': {
                'house_spider.middlewares.RotateUserAgentMiddleware': 400,
                'house_spider.middlewares.CustomRetryMiddleware': 550,
            },
            
            # 双写数据管道
            'ITEM_PIPELINES': {
                'house_spider.pipelines.ValidationPipeline': 200,
                'mongodb_integration.pipelines.mongo_pipeline.DualWritePipeline': 300,
                'mongodb_integration.pipelines.mongo_pipeline.DataConsistencyPipeline': 400,
                'house_spider.pipelines.StatisticsPipeline': 500,
            },
            
            # 日志设置
            'LOG_LEVEL': 'INFO',
            'LOG_FILE': f'dual_write_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            
            # MySQL配置
            'MYSQL_HOST': 'localhost',
            'MYSQL_PORT': 3306,
            'MYSQL_USER': 'root',
            'MYSQL_PASSWORD': '123456',
            'MYSQL_DATABASE': 'guangzhou_house',
            
            # MongoDB配置
            'MONGO_HOST': '127.0.0.1',
            'MONGO_PORT': 27017,
            'MONGO_DATABASE': 'house_data',
            
            # 内存使用监控
            'MEMUSAGE_ENABLED': True,
            'MEMUSAGE_LIMIT_MB': 1024,
            'MEMUSAGE_WARNING_MB': 512,
        }
        
        return conservative_settings
    
    def check_prerequisites(self):
        """检查测试前提条件"""
        print("🔍 检查测试前提条件...")
        
        # 检查MongoDB状态
        try:
            import pymongo
            client = pymongo.MongoClient('mongodb://127.0.0.1:27017/', serverSelectionTimeoutMS=2000)
            client.admin.command('ping')
            print("✅ MongoDB连接正常")
            client.close()
        except Exception as e:
            print(f"❌ MongoDB连接失败: {e}")
            return False
        
        # 检查MySQL状态
        try:
            import pymysql
            conn = pymysql.connect(host='localhost', user='root', password='123456', database='guangzhou_house')
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            print("✅ MySQL连接正常")
        except Exception as e:
            print(f"❌ MySQL连接失败: {e}")
            return False
        
        # 检查Scrapy项目
        if not os.path.exists('scrapy_spider/house_spider'):
            print("❌ Scrapy项目不存在")
            return False
        print("✅ Scrapy项目存在")
        
        # 检查双写管道
        if not os.path.exists('mongodb_integration/pipelines/mongo_pipeline.py'):
            print("❌ 双写管道不存在")
            return False
        print("✅ 双写管道存在")
        
        return True
    
    def run_conservative_crawl(self, pages=1):
        """运行超保守爬虫测试"""
        print(f"\n🚀 开始双写机制爬虫测试 (爬取{pages}页)...")
        print("⚠️  使用超保守设置：8秒延迟，单并发，最大20秒限速")
        
        try:
            # 切换到scrapy项目目录
            original_dir = os.getcwd()
            os.chdir('scrapy_spider')
            
            # 构建scrapy命令
            cmd = [
                'scrapy', 'crawl', 'lianjia',
                '-a', f'pages={pages}',
                '-s', 'CONCURRENT_REQUESTS=1',
                '-s', 'DOWNLOAD_DELAY=8',
                '-s', 'RANDOMIZE_DOWNLOAD_DELAY=True',
                '-s', 'AUTOTHROTTLE_ENABLED=True',
                '-s', 'AUTOTHROTTLE_START_DELAY=8',
                '-s', 'AUTOTHROTTLE_MAX_DELAY=20',
                '-s', 'AUTOTHROTTLE_TARGET_CONCURRENCY=0.3',
                '-s', 'AUTOTHROTTLE_DEBUG=True',
                '-s', 'RETRY_TIMES=2',
                '-s', 'DOWNLOAD_TIMEOUT=30',
                '-s', 'LOG_LEVEL=INFO',
                # 配置双写管道
                '-s', 'ITEM_PIPELINES={"house_spider.pipelines.ValidationPipeline": 200, "mongodb_integration.pipelines.mongo_pipeline.DualWritePipeline": 300, "mongodb_integration.pipelines.mongo_pipeline.DataConsistencyPipeline": 400, "house_spider.pipelines.StatisticsPipeline": 500}',
                # MongoDB配置
                '-s', 'MONGO_HOST=127.0.0.1',
                '-s', 'MONGO_PORT=27017',
                '-s', 'MONGO_DATABASE=house_data'
            ]
            
            print(f"执行命令: {' '.join(cmd)}")
            
            # 运行爬虫
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10分钟超时
            crawl_time = time.time() - start_time
            
            # 切换回原目录
            os.chdir(original_dir)
            
            # 分析结果
            if result.returncode == 0:
                print(f"✅ 爬虫执行成功")
                print(f"⏱️  执行时间: {crawl_time:.1f} 秒")
                
                # 分析日志输出
                output = result.stdout + result.stderr
                
                # 提取统计信息
                stats = self.extract_crawl_stats(output)
                
                self.test_results['crawl_test'] = {
                    'success': True,
                    'crawl_time': crawl_time,
                    'pages_requested': pages,
                    'stats': stats
                }
                
                print(f"📊 爬取统计:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                
                return True
                
            else:
                print(f"❌ 爬虫执行失败 (返回码: {result.returncode})")
                print(f"错误输出: {result.stderr}")
                
                self.test_results['crawl_test'] = {
                    'success': False,
                    'error': result.stderr,
                    'return_code': result.returncode
                }
                
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ 爬虫执行超时")
            os.chdir(original_dir)
            return False
        except Exception as e:
            print(f"❌ 爬虫执行异常: {e}")
            os.chdir(original_dir)
            return False
    
    def extract_crawl_stats(self, output):
        """从爬虫输出中提取统计信息"""
        stats = {}
        
        lines = output.split('\n')
        for line in lines:
            if 'item_scraped_count' in line:
                try:
                    count = int(line.split(':')[-1].strip())
                    stats['爬取条数'] = count
                except:
                    pass
            elif 'request_count' in line:
                try:
                    count = int(line.split(':')[-1].strip())
                    stats['请求数'] = count
                except:
                    pass
            elif 'response_received_count' in line:
                try:
                    count = int(line.split(':')[-1].strip())
                    stats['响应数'] = count
                except:
                    pass
            elif 'downloader/exception_count' in line:
                try:
                    count = int(line.split(':')[-1].strip())
                    stats['异常数'] = count
                except:
                    pass
        
        return stats
    
    def verify_dual_write_results(self):
        """验证双写结果"""
        print("\n🔍 验证双写结果...")
        
        try:
            import pymysql
            import mongoengine
            from mongodb_integration.models.mongo_models import HouseDocument
            
            # 连接数据库
            mysql_conn = pymysql.connect(host='localhost', user='root', password='123456', database='guangzhou_house')
            mongoengine.connect('house_data', host='127.0.0.1', port=27017)
            
            # 检查MySQL双写表
            cursor = mysql_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM House_dual_write")
            mysql_count = cursor.fetchone()[0]
            
            # 检查MongoDB
            mongo_count = HouseDocument.objects(crawl_meta__spider_name='lianjia').count()
            
            cursor.close()
            mysql_conn.close()
            mongoengine.disconnect()
            
            print(f"📊 双写结果:")
            print(f"  MySQL双写表: {mysql_count} 条")
            print(f"  MongoDB新增: {mongo_count} 条")
            
            # 判断双写是否成功
            if mysql_count > 0 and mongo_count > 0:
                print("✅ 双写机制工作正常")
                success_rate = min(mysql_count, mongo_count) / max(mysql_count, mongo_count) * 100
                print(f"📈 数据一致性: {success_rate:.1f}%")
                
                self.test_results['dual_write_verification'] = {
                    'success': True,
                    'mysql_count': mysql_count,
                    'mongo_count': mongo_count,
                    'consistency_rate': success_rate
                }
                
                return True
            else:
                print("❌ 双写机制可能存在问题")
                self.test_results['dual_write_verification'] = {
                    'success': False,
                    'mysql_count': mysql_count,
                    'mongo_count': mongo_count
                }
                return False
                
        except Exception as e:
            print(f"❌ 双写验证失败: {e}")
            return False
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📋 双写机制爬虫测试报告")
        print("="*60)
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        print(f"⏱️  总测试时间: {total_time:.1f} 秒")
        print(f"📅 测试时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 爬虫测试结果
        if 'crawl_test' in self.test_results:
            crawl_result = self.test_results['crawl_test']
            if crawl_result['success']:
                print(f"\n🚀 爬虫测试结果: ✅ 成功")
                print(f"  - 执行时间: {crawl_result['crawl_time']:.1f} 秒")
                if 'stats' in crawl_result:
                    for key, value in crawl_result['stats'].items():
                        print(f"  - {key}: {value}")
            else:
                print(f"\n🚀 爬虫测试结果: ❌ 失败")
                print(f"  - 错误: {crawl_result.get('error', 'Unknown error')}")
        
        # 双写验证结果
        if 'dual_write_verification' in self.test_results:
            verify_result = self.test_results['dual_write_verification']
            if verify_result['success']:
                print(f"\n🔍 双写验证结果: ✅ 成功")
                print(f"  - MySQL记录: {verify_result['mysql_count']} 条")
                print(f"  - MongoDB记录: {verify_result['mongo_count']} 条")
                print(f"  - 一致性: {verify_result['consistency_rate']:.1f}%")
            else:
                print(f"\n🔍 双写验证结果: ❌ 失败")
                print(f"  - MySQL记录: {verify_result['mysql_count']} 条")
                print(f"  - MongoDB记录: {verify_result['mongo_count']} 条")
        
        print("\n" + "="*60)

def main():
    """主函数"""
    print("🎯 双写机制爬虫测试套件")
    print("="*60)
    
    # 创建测试套件
    test_suite = DualWriteCrawlTest()
    
    try:
        # 1. 检查前提条件
        if not test_suite.check_prerequisites():
            print("❌ 前提条件检查失败，无法继续测试")
            return False
        
        # 2. 运行保守爬虫测试 (只爬取1页，约20条数据)
        if not test_suite.run_conservative_crawl(pages=1):
            print("❌ 爬虫测试失败")
            return False
        
        # 3. 验证双写结果
        test_suite.verify_dual_write_results()
        
        # 4. 生成报告
        test_suite.generate_report()
        
        print("\n🎉 双写机制爬虫测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
