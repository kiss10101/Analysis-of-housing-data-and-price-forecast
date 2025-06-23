#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MongoDB数据模型
"""

import sys
import os
from datetime import datetime
from decimal import Decimal

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def test_mongoengine_connection():
    """测试MongoEngine连接"""
    print("测试MongoEngine连接")
    print("=" * 40)
    
    try:
        from mongodb_integration.mongodb_config import setup_mongoengine
        
        success = setup_mongoengine()
        if success:
            print("✅ MongoEngine连接成功")
            return True
        else:
            print("❌ MongoEngine连接失败")
            return False
            
    except Exception as e:
        print(f"❌ MongoEngine连接异常: {e}")
        return False

def test_model_creation():
    """测试模型创建"""
    print("\n测试MongoDB模型创建")
    print("=" * 40)
    
    try:
        from mongodb_integration.models.mongo_models import (
            HouseDocument, LocationInfo, PriceInfo, 
            HouseFeatures, CrawlMetadata
        )
        
        # 创建测试数据
        location = LocationInfo(
            city="天河区",
            street="天河路",
            building="测试小区"
        )
        
        price = PriceInfo(
            monthly_rent=Decimal('3000.00')
        )
        
        features = HouseFeatures(
            area=Decimal('80.5'),
            room_type="2室1厅",
            direction="南"
        )
        
        crawl_meta = CrawlMetadata(
            spider_name="test_spider",
            crawl_id="test-123",
            source_url="http://test.com",
            data_quality=95
        )
        
        # 创建主文档
        house = HouseDocument(
            title="测试房源",
            rental_type="整租",
            location=location,
            price=price,
            features=features,
            crawl_meta=crawl_meta,
            tags=["精装修", "地铁房"],
            images=["http://test.com/img1.jpg"]
        )
        
        print("✅ MongoDB模型创建成功")
        print(f"   房源标题: {house.title}")
        print(f"   城市: {house.location.city}")
        print(f"   价格: ¥{house.price.monthly_rent}")
        print(f"   面积: {house.features.area}㎡")
        
        return house
        
    except Exception as e:
        print(f"❌ 模型创建失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_model_save():
    """测试模型保存"""
    print("\n测试MongoDB模型保存")
    print("=" * 40)
    
    try:
        # 创建测试模型
        house = test_model_creation()
        if not house:
            return False
        
        # 保存到数据库
        house.save()
        print(f"✅ 模型保存成功，ID: {house.id}")
        
        # 查询验证
        saved_house = house.__class__.objects(id=house.id).first()
        if saved_house:
            print("✅ 模型查询成功")
            print(f"   查询到房源: {saved_house.title}")
            print(f"   创建时间: {saved_house.created_at}")
            
            # 清理测试数据
            saved_house.delete()
            print("✅ 测试数据清理完成")
            
            return True
        else:
            print("❌ 模型查询失败")
            return False
            
    except Exception as e:
        print(f"❌ 模型保存失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_mapper():
    """测试数据映射器"""
    print("\n测试数据映射器")
    print("=" * 40)
    
    try:
        from mongodb_integration.models.data_mapper import DataMapper
        
        # 模拟Scrapy Item数据
        scrapy_item = {
            'title': '测试房源映射',
            'type': '整租',
            'building': '映射测试小区',
            'city': '天河区',
            'street': '测试街道',
            'area': 85.0,
            'direct': '南北',
            'price': 3500.0,
            'link': 'http://test.com/house/123',
            'tag': '精装修,地铁房,拎包入住',
            'img': 'http://test.com/img.jpg',
            'spider_name': 'test_mapper',
            'crawl_id': 'mapper-123',
            'data_quality': 90,
            'crawl_time': datetime.now()
        }
        
        # 测试Scrapy Item -> MongoDB
        mongo_doc = DataMapper.scrapy_item_to_mongo(scrapy_item)
        print("✅ Scrapy Item -> MongoDB 转换成功")
        print(f"   标题: {mongo_doc.title}")
        print(f"   标签: {mongo_doc.tags}")
        
        # 测试MongoDB -> MySQL Dict
        mysql_dict = DataMapper.mongo_to_mysql_dict(mongo_doc)
        print("✅ MongoDB -> MySQL Dict 转换成功")
        print(f"   MySQL格式标题: {mysql_dict['title']}")
        print(f"   MySQL格式标签: {mysql_dict['tag']}")
        
        # 测试数据验证
        validation = DataMapper.validate_data(mysql_dict)
        print("✅ 数据验证完成")
        print(f"   验证结果: {'通过' if validation['valid'] else '失败'}")
        print(f"   质量评分: {validation['quality_score']}")
        
        if validation['errors']:
            print(f"   错误: {validation['errors']}")
        if validation['warnings']:
            print(f"   警告: {validation['warnings']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据映射测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_indexes():
    """测试索引创建"""
    print("\n测试索引创建")
    print("=" * 40)
    
    try:
        from mongodb_integration.models.mongo_models import HouseDocument
        
        # 获取集合
        collection = HouseDocument._get_collection()
        
        # 获取现有索引
        indexes = collection.list_indexes()
        index_names = [index['name'] for index in indexes]
        
        print("✅ 当前索引列表:")
        for name in index_names:
            print(f"   - {name}")
        
        # 检查关键索引
        expected_indexes = ['_id_', 'house_id_1', 'rental_type_1', 'location.city_1']
        missing_indexes = [idx for idx in expected_indexes if idx not in index_names]
        
        if missing_indexes:
            print(f"⚠️  缺少索引: {missing_indexes}")
        else:
            print("✅ 关键索引都已存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 索引测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("MongoDB数据模型测试")
    print("=" * 60)
    
    tests = [
        ("MongoEngine连接", test_mongoengine_connection),
        ("模型创建", test_model_creation),
        ("模型保存", test_model_save),
        ("数据映射器", test_data_mapper),
        ("索引创建", test_indexes),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if test_name == "模型创建":
                # 这个测试返回对象，不是布尔值
                result = test_func()
                results.append((test_name, result is not None))
            else:
                result = test_func()
                results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n通过率: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 所有测试通过!")
        print("✅ MongoDB数据模型准备就绪")
        print("✅ 可以开始双写机制开发")
    else:
        print("⚠️  部分测试失败，请检查配置")

if __name__ == '__main__':
    main()
