#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrapy爬虫启动脚本
房源数据分析系统 - 生产级爬虫启动器
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def setup_logging():
    """设置日志"""
    log_dir = os.path.join(current_dir, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, f'spider_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_file

def run_spider(spider_name='lianjia', pages=5, output_format=None):
    """运行爬虫"""
    
    # 设置日志
    log_file = setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("房源数据分析系统 - Scrapy爬虫启动")
    logger.info("=" * 60)
    logger.info(f"爬虫名称: {spider_name}")
    logger.info(f"爬取页数: {pages}")
    logger.info(f"日志文件: {log_file}")
    logger.info(f"启动时间: {datetime.now()}")
    
    try:
        # 获取项目设置
        settings = get_project_settings()
        
        # 动态设置输出格式
        if output_format:
            output_dir = os.path.join(current_dir, 'output')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f'houses_{timestamp}.{output_format}')
            
            settings.set('FEEDS', {
                output_file: {
                    'format': output_format,
                    'encoding': 'utf8',
                    'store_empty': False,
                }
            })
            logger.info(f"输出文件: {output_file}")
        
        # 创建爬虫进程
        process = CrawlerProcess(settings)
        
        # 添加爬虫
        process.crawl(spider_name, pages=pages)
        
        # 启动爬虫
        logger.info("开始爬取数据...")
        process.start()
        
        logger.info("爬取完成!")
        
    except Exception as e:
        logger.error(f"爬虫运行失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='房源数据爬虫启动器')
    parser.add_argument('-s', '--spider', default='lianjia', help='爬虫名称 (默认: lianjia)')
    parser.add_argument('-p', '--pages', type=int, default=5, help='爬取页数 (默认: 5)')
    parser.add_argument('-o', '--output', choices=['json', 'csv', 'xml'], help='输出格式')
    parser.add_argument('--test', action='store_true', help='测试模式 (只爬取1页)')
    
    args = parser.parse_args()
    
    # 测试模式
    if args.test:
        args.pages = 1
        print("测试模式: 只爬取1页数据")
    
    # 运行爬虫
    run_spider(
        spider_name=args.spider,
        pages=args.pages,
        output_format=args.output
    )

if __name__ == '__main__':
    main()
