#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬件性能评估工具
评估10000条数据的硬件开销
"""

import psutil
import time
import pymongo
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HardwareAnalyzer:
    """硬件性能分析器"""
    
    def __init__(self):
        self.baseline_memory = None
        self.baseline_cpu = None
        
    def get_system_info(self):
        """获取系统信息"""
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else 'N/A',
            'memory_total': psutil.virtual_memory().total / (1024**3),  # GB
            'memory_available': psutil.virtual_memory().available / (1024**3),  # GB
            'disk_usage': psutil.disk_usage('/').percent if hasattr(psutil.disk_usage('/'), 'percent') else 'N/A'
        }
    
    def start_monitoring(self):
        """开始监控"""
        self.baseline_memory = psutil.virtual_memory().used / (1024**3)
        self.baseline_cpu = psutil.cpu_percent(interval=1)
        logger.info(f"基线内存使用: {self.baseline_memory:.2f} GB")
        logger.info(f"基线CPU使用: {self.baseline_cpu:.1f}%")
    
    def get_current_usage(self):
        """获取当前使用情况"""
        current_memory = psutil.virtual_memory().used / (1024**3)
        current_cpu = psutil.cpu_percent(interval=1)
        
        memory_increase = current_memory - self.baseline_memory if self.baseline_memory else 0
        cpu_increase = current_cpu - self.baseline_cpu if self.baseline_cpu else 0
        
        return {
            'memory_current': current_memory,
            'memory_increase': memory_increase,
            'cpu_current': current_cpu,
            'cpu_increase': cpu_increase
        }
    
    def estimate_10k_impact(self, current_data_count=1000):
        """估算10000条数据的影响"""
        current_usage = self.get_current_usage()
        scale_factor = 10000 / current_data_count
        
        estimated_memory_increase = current_usage['memory_increase'] * scale_factor
        estimated_cpu_increase = current_usage['cpu_increase'] * scale_factor
        
        system_info = self.get_system_info()
        
        # 评估是否可接受
        memory_acceptable = estimated_memory_increase < (system_info['memory_available'] * 0.5)
        cpu_acceptable = estimated_cpu_increase < 30  # 30%以下认为可接受
        
        return {
            'estimated_memory_increase': estimated_memory_increase,
            'estimated_cpu_increase': estimated_cpu_increase,
            'memory_acceptable': memory_acceptable,
            'cpu_acceptable': cpu_acceptable,
            'recommendations': self._generate_recommendations(
                estimated_memory_increase, estimated_cpu_increase, system_info
            )
        }
    
    def _generate_recommendations(self, memory_increase, cpu_increase, system_info):
        """生成优化建议"""
        recommendations = []
        
        if memory_increase > 2:  # 超过2GB
            recommendations.append("建议启用分页加载，每页显示50-100条数据")
            recommendations.append("考虑使用虚拟滚动技术")
            recommendations.append("启用数据缓存机制")
        
        if cpu_increase > 20:  # 超过20%
            recommendations.append("建议使用服务器端分页")
            recommendations.append("优化数据库查询，添加索引")
            recommendations.append("考虑使用CDN加速静态资源")
        
        if system_info['memory_total'] < 8:  # 小于8GB内存
            recommendations.append("建议升级内存到8GB以上")
            recommendations.append("启用数据压缩")
        
        if not recommendations:
            recommendations.append("当前硬件配置足够支持10000条数据")
        
        return recommendations

def test_mongodb_performance():
    """测试MongoDB性能"""
    analyzer = HardwareAnalyzer()
    
    logger.info("🔍 开始硬件性能评估...")
    logger.info("=" * 50)
    
    # 系统信息
    system_info = analyzer.get_system_info()
    logger.info("💻 系统配置:")
    logger.info(f"  CPU核心数: {system_info['cpu_count']}")
    logger.info(f"  CPU频率: {system_info['cpu_freq']} MHz")
    logger.info(f"  总内存: {system_info['memory_total']:.1f} GB")
    logger.info(f"  可用内存: {system_info['memory_available']:.1f} GB")
    
    # 开始监控
    analyzer.start_monitoring()
    
    # 模拟数据库操作
    try:
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['house_data']
        collection = db['houses']
        
        # 查询当前数据量
        current_count = collection.count_documents({})
        logger.info(f"📊 当前数据量: {current_count} 条")
        
        # 模拟数据加载
        logger.info("🔄 模拟数据加载...")
        start_time = time.time()
        
        # 分批查询模拟大数据量
        batch_size = 100
        total_processed = 0
        
        for skip in range(0, min(current_count, 1000), batch_size):
            batch = list(collection.find().skip(skip).limit(batch_size))
            total_processed += len(batch)
            
            # 模拟数据处理
            for doc in batch:
                # 简单的数据处理操作
                _ = str(doc.get('title', ''))
                _ = doc.get('price', {})
                _ = doc.get('location', {})
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        logger.info(f"✅ 处理完成: {total_processed} 条数据，耗时 {processing_time:.2f} 秒")
        
        # 获取性能数据
        current_usage = analyzer.get_current_usage()
        logger.info("📈 当前资源使用:")
        logger.info(f"  内存增加: {current_usage['memory_increase']:.3f} GB")
        logger.info(f"  CPU增加: {current_usage['cpu_increase']:.1f}%")
        
        # 估算10000条数据的影响
        estimation = analyzer.estimate_10k_impact(total_processed)
        
        logger.info("\n🎯 10000条数据预估:")
        logger.info(f"  预估内存增加: {estimation['estimated_memory_increase']:.3f} GB")
        logger.info(f"  预估CPU增加: {estimation['estimated_cpu_increase']:.1f}%")
        logger.info(f"  内存可接受: {'✅' if estimation['memory_acceptable'] else '❌'}")
        logger.info(f"  CPU可接受: {'✅' if estimation['cpu_acceptable'] else '❌'}")
        
        logger.info("\n💡 优化建议:")
        for i, rec in enumerate(estimation['recommendations'], 1):
            logger.info(f"  {i}. {rec}")
        
        # 性能等级评估
        if estimation['memory_acceptable'] and estimation['cpu_acceptable']:
            logger.info("\n🎉 结论: 您的硬件配置完全可以支持10000条数据！")
        elif estimation['memory_acceptable'] or estimation['cpu_acceptable']:
            logger.info("\n⚠️ 结论: 硬件配置基本可以支持，建议进行优化")
        else:
            logger.info("\n❌ 结论: 建议升级硬件或优化系统配置")
        
    except Exception as e:
        logger.error(f"❌ 性能测试失败: {e}")
    
    finally:
        if 'client' in locals():
            client.close()

if __name__ == '__main__':
    test_mongodb_performance()
