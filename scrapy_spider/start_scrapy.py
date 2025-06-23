#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrapy爬虫启动器 - 生产版本
房源数据分析系统
"""

import os
import sys
import argparse
import logging
import subprocess
from datetime import datetime

def setup_logging(log_level='INFO'):
    """设置日志"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(current_dir, 'logs')
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, f'scrapy_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_file

def run_scrapy_spider(pages=5, spider_name='lianjia', log_level='INFO'):
    """运行Scrapy爬虫"""
    
    # 设置日志
    log_file = setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("房源数据分析系统 - Scrapy爬虫启动")
    logger.info("=" * 60)
    logger.info(f"爬虫名称: {spider_name}")
    logger.info(f"爬取页数: {pages}")
    logger.info(f"日志级别: {log_level}")
    logger.info(f"日志文件: {log_file}")
    logger.info(f"启动时间: {datetime.now()}")
    
    try:
        # 获取当前目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 设置环境变量
        env = os.environ.copy()
        env['PYTHONPATH'] = current_dir
        
        # 构建命令
        cmd = [
            sys.executable, '-m', 'scrapy', 'crawl', spider_name,
            '-a', f'pages={pages}',
            '-s', f'LOG_LEVEL={log_level}',
            '-s', f'LOG_FILE={log_file}'
        ]
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        logger.info("开始爬取数据...")
        
        # 运行命令
        process = subprocess.Popen(
            cmd,
            cwd=current_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 实时输出日志
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                print(line.strip())
                
        process.wait()
        
        if process.returncode == 0:
            logger.info("✅ 爬取完成!")
            return True
        else:
            logger.error(f"❌ 爬取失败，返回码: {process.returncode}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 爬虫运行异常: {e}")
        return False

def check_environment():
    """检查运行环境"""
    print("检查运行环境...")
    
    try:
        # 检查Python版本
        python_version = sys.version_info
        print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 检查Scrapy
        import scrapy
        print(f"✅ Scrapy版本: {scrapy.__version__}")
        
        # 检查数据库连接
        import pymysql
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='guangzhou_house'
        )
        conn.close()
        print("✅ MySQL连接正常")
        
        # 检查项目模块
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        from house_spider.spiders.lianjia_spider import LianjiaSpider
        print("✅ 爬虫模块正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 环境检查失败: {e}")
        return False

def show_statistics():
    """显示统计信息"""
    print("\n" + "=" * 50)
    print("数据统计")
    print("=" * 50)
    
    try:
        import pymysql
        
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='guangzhou_house',
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # 原始表统计
        cursor.execute("SELECT COUNT(*) FROM House")
        original_count = cursor.fetchone()[0]
        print(f"原始House表记录数: {original_count}")
        
        # Scrapy表统计
        cursor.execute("SHOW TABLES LIKE 'House_scrapy'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM House_scrapy")
            scrapy_count = cursor.fetchone()[0]
            print(f"Scrapy备份表记录数: {scrapy_count}")
            
            if scrapy_count > 0:
                # 最新记录
                cursor.execute("""
                    SELECT crawl_time, COUNT(*) as count
                    FROM House_scrapy 
                    GROUP BY DATE(crawl_time)
                    ORDER BY crawl_time DESC
                    LIMIT 5
                """)
                daily_stats = cursor.fetchall()
                
                print("\n最近爬取统计:")
                for stat in daily_stats:
                    print(f"  {stat[0]}: {stat[1]} 条")
        else:
            print("Scrapy备份表: 不存在")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"统计信息获取失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='房源数据分析系统 - Scrapy爬虫启动器')
    parser.add_argument('-p', '--pages', type=int, default=5, help='爬取页数 (默认: 5)')
    parser.add_argument('-s', '--spider', default='lianjia', help='爬虫名称 (默认: lianjia)')
    parser.add_argument('-l', '--log-level', default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='日志级别 (默认: INFO)')
    parser.add_argument('--check', action='store_true', help='检查环境')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--test', action='store_true', help='测试模式 (只爬取1页)')
    
    args = parser.parse_args()
    
    # 检查环境
    if args.check:
        check_environment()
        return
    
    # 显示统计
    if args.stats:
        show_statistics()
        return
    
    # 测试模式
    if args.test:
        args.pages = 1
        args.log_level = 'DEBUG'
        print("🧪 测试模式: 只爬取1页数据")
    
    print("房源数据分析系统 - Scrapy爬虫启动器")
    print(f"启动时间: {datetime.now()}")
    
    # 检查环境
    if not check_environment():
        print("❌ 环境检查失败，请检查配置")
        sys.exit(1)
    
    # 运行爬虫
    success = run_scrapy_spider(
        pages=args.pages,
        spider_name=args.spider,
        log_level=args.log_level
    )
    
    if success:
        print("\n🎉 爬取任务完成!")
        show_statistics()
    else:
        print("\n❌ 爬取任务失败!")
        sys.exit(1)

if __name__ == '__main__':
    main()
