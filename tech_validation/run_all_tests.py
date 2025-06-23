#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
综合测试运行脚本
运行所有技术验证测试并生成综合报告
"""

import os
import sys
import json
import subprocess
from datetime import datetime


def run_test_script(script_path, test_name):
    """运行测试脚本"""
    print(f"\n{'='*60}")
    print(f"🚀 开始运行: {test_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([
            sys.executable, script_path
        ], capture_output=True, text=True, timeout=600)
        
        print(f"✅ {test_name} 完成")
        print(f"返回码: {result.returncode}")
        
        if result.stdout:
            print("输出:")
            print(result.stdout[-1000:])  # 显示最后1000字符
        
        if result.stderr and result.returncode != 0:
            print("错误:")
            print(result.stderr[-500:])  # 显示最后500字符
        
        return {
            'success': result.returncode == 0,
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        print(f"❌ {test_name} 超时")
        return {
            'success': False,
            'error': 'timeout'
        }
    except Exception as e:
        print(f"❌ {test_name} 执行失败: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def generate_comprehensive_report(test_results):
    """生成综合报告"""
    print("\n📊 生成综合测试报告...")
    
    # 创建报告目录
    report_dir = os.path.join(os.path.dirname(__file__), 'reports')
    os.makedirs(report_dir, exist_ok=True)
    
    # 综合结果
    comprehensive_results = {
        'test_time': datetime.now().isoformat(),
        'test_results': test_results,
        'summary': {
            'total_tests': len(test_results),
            'passed_tests': sum(1 for r in test_results.values() if r.get('success')),
            'failed_tests': sum(1 for r in test_results.values() if not r.get('success'))
        }
    }
    
    # 读取各个测试的详细报告
    detailed_reports = {}
    
    # 性能对比报告
    perf_report_file = os.path.join(report_dir, 'performance_comparison.json')
    if os.path.exists(perf_report_file):
        try:
            with open(perf_report_file, 'r', encoding='utf-8') as f:
                detailed_reports['performance'] = json.load(f)
        except:
            pass
    
    # MongoDB集成报告
    mongo_report_file = os.path.join(report_dir, 'mongodb_integration_test.json')
    if os.path.exists(mongo_report_file):
        try:
            with open(mongo_report_file, 'r', encoding='utf-8') as f:
                detailed_reports['mongodb'] = json.load(f)
        except:
            pass
    
    # 数据迁移报告
    migration_report_file = os.path.join(report_dir, 'data_migration_test.json')
    if os.path.exists(migration_report_file):
        try:
            with open(migration_report_file, 'r', encoding='utf-8') as f:
                detailed_reports['migration'] = json.load(f)
        except:
            pass
    
    comprehensive_results['detailed_reports'] = detailed_reports
    
    # 保存JSON报告
    json_file = os.path.join(report_dir, 'comprehensive_test_report.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_results, f, ensure_ascii=False, indent=2)
    
    # 生成Markdown报告
    md_content = generate_markdown_summary(comprehensive_results)
    md_file = os.path.join(report_dir, 'comprehensive_test_report.md')
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"📄 综合报告已生成: {md_file}")
    return md_file


def generate_markdown_summary(results):
    """生成Markdown综合报告"""
    test_results = results['test_results']
    summary = results['summary']
    detailed = results.get('detailed_reports', {})
    
    # 基本信息
    md = f"""# 架构升级技术验证综合报告

## 测试概览
- **测试时间**: {results['test_time']}
- **总测试数**: {summary['total_tests']}
- **通过测试**: {summary['passed_tests']} ✅
- **失败测试**: {summary['failed_tests']} ❌
- **成功率**: {(summary['passed_tests']/summary['total_tests']*100):.1f}%

## 测试结果详情

"""
    
    # 各项测试结果
    for test_name, result in test_results.items():
        status = "✅ 通过" if result.get('success') else "❌ 失败"
        md += f"### {test_name}\n"
        md += f"- **状态**: {status}\n"
        if not result.get('success') and result.get('error'):
            md += f"- **错误**: {result['error']}\n"
        md += "\n"
    
    # 性能对比分析
    if 'performance' in detailed:
        perf = detailed['performance']
        original = perf.get('original_crawler', {})
        scrapy = perf.get('scrapy_crawler', {})
        comparison = perf.get('comparison', {})
        
        md += f"""## 性能对比分析

### 爬虫性能对比
| 指标 | 原始爬虫 | Scrapy爬虫 | 改进 |
|------|----------|------------|------|
| 抓取速度 | {original.get('items_per_second', 0):.2f} 条/秒 | {scrapy.get('items_per_second', 0):.2f} 条/秒 | {comparison.get('speed_improvement', 0):.1f}% |
| 总耗时 | {original.get('total_time', 0):.2f} 秒 | {scrapy.get('total_time', 0):.2f} 秒 | {comparison.get('time_difference', 0):.2f} 秒 |
| 内存使用 | {original.get('memory_usage', 0):.2f} MB | {scrapy.get('memory_usage', 0):.2f} MB | {comparison.get('memory_difference', 0):.2f} MB |
| 错误数量 | {original.get('errors', 0)} | {scrapy.get('errors', 0)} | {comparison.get('reliability_improvement', 0):.1f}% |

"""
    
    # MongoDB集成分析
    if 'mongodb' in detailed:
        mongo = detailed['mongodb']
        conn = mongo.get('connection_test', {})
        crud = mongo.get('crud_test', {})
        perf = mongo.get('performance_test', {})
        
        md += f"""## MongoDB集成分析

### 连接性能
- **连接时间**: {conn.get('connection_time', 0):.3f} 秒
- **MongoDB版本**: {conn.get('server_info', 'N/A')}

### CRUD性能
- **插入性能**: {crud.get('insert_time', 0):.3f} 秒
- **查询性能**: {crud.get('query_time', 0):.3f} 秒
- **聚合查询**: {crud.get('aggregation_time', 0):.3f} 秒

### 批量操作性能
- **插入速度**: {perf.get('insert_rate', 0):.0f} 条/秒
- **测试记录数**: {perf.get('record_count', 0)} 条

"""
    
    # 数据迁移分析
    if 'migration' in detailed:
        migration = detailed['migration']
        extract = migration.get('data_extraction', {})
        load = migration.get('data_loading', {})
        validate = migration.get('validation', {})
        
        md += f"""## 数据迁移分析

### 迁移性能
- **提取速度**: {extract.get('record_count', 0) / extract.get('extraction_time', 1):.0f} 条/秒
- **加载速度**: {load.get('insertion_rate', 0):.0f} 条/秒
- **数据一致性**: {'✅ 一致' if validate.get('data_consistency') else '❌ 不一致'}

### 迁移规模
- **测试记录数**: {extract.get('record_count', 0)} 条
- **成功迁移**: {load.get('total_inserted', 0)} 条

"""
    
    # 总结和建议
    md += f"""## 总结与建议

### 技术可行性评估
"""
    
    if summary['passed_tests'] == summary['total_tests']:
        md += """✅ **所有测试通过** - 技术升级方案完全可行

### 推荐升级路径
1. **第一阶段**: 升级爬虫到Scrapy框架
2. **第二阶段**: 引入MongoDB作为数据存储
3. **第三阶段**: 完成数据迁移和系统优化

### 预期收益
- 爬虫性能和稳定性显著提升
- 数据存储更加灵活和可扩展
- 支持更复杂的数据分析需求
"""
    elif summary['passed_tests'] > summary['total_tests'] / 2:
        md += """⚠️ **部分测试通过** - 技术升级方案基本可行，需要解决部分问题

### 建议措施
1. 解决失败测试中的技术问题
2. 进行更详细的技术验证
3. 制定风险应对方案
"""
    else:
        md += """❌ **多数测试失败** - 当前技术升级方案存在较大风险

### 建议措施
1. 重新评估技术选型
2. 解决基础环境问题
3. 考虑替代方案
"""
    
    md += f"""
### 下一步行动
1. 根据测试结果调整升级方案
2. 制定详细的实施计划
3. 准备生产环境部署

---
*报告生成时间: {results['test_time']}*
"""
    
    return md


def main():
    """主函数"""
    print("🚀 开始运行架构升级技术验证测试套件")
    print(f"测试时间: {datetime.now().isoformat()}")
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定义测试脚本
    tests = {
        "性能对比测试": os.path.join(current_dir, "performance_test", "performance_comparison.py"),
        "MongoDB集成测试": os.path.join(current_dir, "mongodb_test", "mongodb_integration_test.py"),
        "数据迁移测试": os.path.join(current_dir, "migration_test", "data_migration_test.py")
    }
    
    # 运行所有测试
    test_results = {}
    
    for test_name, script_path in tests.items():
        if os.path.exists(script_path):
            test_results[test_name] = run_test_script(script_path, test_name)
        else:
            print(f"❌ 测试脚本不存在: {script_path}")
            test_results[test_name] = {
                'success': False,
                'error': 'script_not_found'
            }
    
    # 生成综合报告
    report_file = generate_comprehensive_report(test_results)
    
    print(f"\n{'='*60}")
    print("🎉 所有测试完成!")
    print(f"📄 综合报告: {report_file}")
    print(f"{'='*60}")
    
    # 显示简要结果
    passed = sum(1 for r in test_results.values() if r.get('success'))
    total = len(test_results)
    print(f"\n📊 测试结果: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    for test_name, result in test_results.items():
        status = "✅" if result.get('success') else "❌"
        print(f"  {status} {test_name}")


if __name__ == "__main__":
    main()
