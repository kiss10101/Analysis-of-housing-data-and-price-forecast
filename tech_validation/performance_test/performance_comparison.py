#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
性能对比测试脚本
对比现有爬虫 vs Scrapy爬虫的性能差异
"""

import time
import psutil
import subprocess
import sys
import os
import json
from datetime import datetime
from memory_profiler import profile
import requests
from lxml import etree
import pymysql


class PerformanceTest:
    def __init__(self):
        self.results = {
            'test_time': datetime.now().isoformat(),
            'original_crawler': {},
            'scrapy_crawler': {},
            'comparison': {}
        }
        
    def test_original_crawler(self, pages=3):
        """测试原始爬虫性能"""
        print("🔍 测试原始爬虫性能...")
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # 模拟原始爬虫逻辑
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36'}
        
        total_items = 0
        errors = 0
        
        for page in range(1, pages + 1):
            try:
                url = f'https://gz.lianjia.com/zufang/pg{page}/#contentList'
                res = requests.get(url, headers=headers)
                html = etree.HTML(res.text)
                
                # 提取数据
                names = html.xpath('//*[@id="content"]/div[1]/div[1]/div/div/p[1]/a/text()')
                prices = html.xpath('//*[@id="content"]/div[1]/div[1]/div/div/span/em/text()')
                
                total_items += len(names)
                time.sleep(2)  # 模拟延迟
                
            except Exception as e:
                errors += 1
                print(f"页面 {page} 出错: {e}")
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        self.results['original_crawler'] = {
            'total_time': end_time - start_time,
            'total_items': total_items,
            'items_per_second': total_items / (end_time - start_time) if end_time > start_time else 0,
            'memory_usage': end_memory - start_memory,
            'errors': errors,
            'pages_tested': pages
        }
        
        print(f"✅ 原始爬虫测试完成: {total_items}条数据, {end_time - start_time:.2f}秒")
        
    def test_scrapy_crawler(self):
        """测试Scrapy爬虫性能"""
        print("🔍 测试Scrapy爬虫性能...")
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # 切换到scrapy项目目录
        scrapy_dir = os.path.join(os.path.dirname(__file__), '..', 'scrapy_test', 'house_spider')
        
        try:
            # 运行Scrapy爬虫
            result = subprocess.run([
                sys.executable, '-m', 'scrapy', 'crawl', 'lianjia', 
                '-s', 'CLOSESPIDER_PAGECOUNT=3',  # 限制页面数
                '-o', 'test_output.json'
            ], 
            cwd=scrapy_dir, 
            capture_output=True, 
            text=True, 
            timeout=300
            )
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            # 分析输出
            total_items = 0
            errors = 0
            
            # 尝试读取输出文件
            output_file = os.path.join(scrapy_dir, 'test_output.json')
            if os.path.exists(output_file):
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        total_items = len(data) if isinstance(data, list) else 1
                except:
                    pass
            
            # 从日志中提取统计信息
            if result.stderr:
                log_lines = result.stderr.split('\n')
                for line in log_lines:
                    if 'item_scraped_count' in line:
                        try:
                            total_items = int(line.split('item_scraped_count')[1].split(',')[0].strip().split(':')[1])
                        except:
                            pass
            
            self.results['scrapy_crawler'] = {
                'total_time': end_time - start_time,
                'total_items': total_items,
                'items_per_second': total_items / (end_time - start_time) if end_time > start_time else 0,
                'memory_usage': end_memory - start_memory,
                'errors': errors,
                'return_code': result.returncode,
                'stdout': result.stdout[:500] if result.stdout else '',
                'stderr': result.stderr[:500] if result.stderr else ''
            }
            
            print(f"✅ Scrapy爬虫测试完成: {total_items}条数据, {end_time - start_time:.2f}秒")
            
        except subprocess.TimeoutExpired:
            print("❌ Scrapy测试超时")
            self.results['scrapy_crawler'] = {
                'error': 'timeout',
                'total_time': 300,
                'total_items': 0
            }
        except Exception as e:
            print(f"❌ Scrapy测试出错: {e}")
            self.results['scrapy_crawler'] = {
                'error': str(e),
                'total_time': 0,
                'total_items': 0
            }
    
    def compare_results(self):
        """对比测试结果"""
        print("📊 生成性能对比报告...")
        
        original = self.results['original_crawler']
        scrapy = self.results['scrapy_crawler']
        
        if 'error' not in scrapy and 'error' not in original:
            self.results['comparison'] = {
                'speed_improvement': (scrapy['items_per_second'] / original['items_per_second'] - 1) * 100 if original['items_per_second'] > 0 else 0,
                'time_difference': scrapy['total_time'] - original['total_time'],
                'memory_difference': scrapy['memory_usage'] - original['memory_usage'],
                'reliability_improvement': (original['errors'] - scrapy['errors']) / max(original['errors'], 1) * 100
            }
        
    def generate_report(self):
        """生成测试报告"""
        report_file = os.path.join(os.path.dirname(__file__), '..', 'reports', 'performance_comparison.json')
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        # 生成可读报告
        readable_report = self.generate_readable_report()
        report_md_file = os.path.join(os.path.dirname(report_file), 'performance_comparison.md')
        
        with open(report_md_file, 'w', encoding='utf-8') as f:
            f.write(readable_report)
        
        print(f"📄 报告已生成: {report_md_file}")
        
    def generate_readable_report(self):
        """生成可读的Markdown报告"""
        original = self.results.get('original_crawler', {})
        scrapy = self.results.get('scrapy_crawler', {})
        comparison = self.results.get('comparison', {})
        
        report = f"""# 爬虫性能对比测试报告

## 测试时间
{self.results['test_time']}

## 测试结果

### 原始爬虫 (requests + lxml)
- **总耗时**: {original.get('total_time', 0):.2f} 秒
- **抓取数据**: {original.get('total_items', 0)} 条
- **抓取速度**: {original.get('items_per_second', 0):.2f} 条/秒
- **内存使用**: {original.get('memory_usage', 0):.2f} MB
- **错误数量**: {original.get('errors', 0)} 个

### Scrapy爬虫
- **总耗时**: {scrapy.get('total_time', 0):.2f} 秒
- **抓取数据**: {scrapy.get('total_items', 0)} 条
- **抓取速度**: {scrapy.get('items_per_second', 0):.2f} 条/秒
- **内存使用**: {scrapy.get('memory_usage', 0):.2f} MB
- **错误数量**: {scrapy.get('errors', 0)} 个

## 性能对比

"""
        
        if comparison:
            report += f"""- **速度提升**: {comparison.get('speed_improvement', 0):.1f}%
- **时间差异**: {comparison.get('time_difference', 0):.2f} 秒
- **内存差异**: {comparison.get('memory_difference', 0):.2f} MB
- **可靠性提升**: {comparison.get('reliability_improvement', 0):.1f}%
"""
        
        report += f"""
## 结论

{'Scrapy在性能和可靠性方面表现更优' if comparison.get('speed_improvement', 0) > 0 else '需要进一步优化Scrapy配置'}

## 建议

1. 如果Scrapy性能更优，建议进行架构升级
2. 如果性能相近，考虑Scrapy的其他优势（去重、错误处理、扩展性）
3. 建议进行更大规模的测试验证
"""
        
        return report
    
    def run_full_test(self):
        """运行完整测试"""
        print("🚀 开始性能对比测试...")
        
        # 测试原始爬虫
        self.test_original_crawler(pages=3)
        
        # 测试Scrapy爬虫
        self.test_scrapy_crawler()
        
        # 对比结果
        self.compare_results()
        
        # 生成报告
        self.generate_report()
        
        print("✅ 性能测试完成!")


if __name__ == "__main__":
    test = PerformanceTest()
    test.run_full_test()
