# -*- coding: utf-8 -*-
"""
数据处理模块
负责从MongoDB导出数据并构建向量索引
"""

import json
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd

from .config import DOCUMENTS_DIR, DATA_CONFIG, LOGGING_CONFIG

# 配置日志
logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)

class HouseDataProcessor:
    """房源数据处理器"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=DATA_CONFIG["chunk_size"],
            chunk_overlap=DATA_CONFIG["chunk_overlap"],
            separators=["\n\n", "\n", "。", "，", " ", ""]
        )
        
    def export_mongodb_data(self, export_format="json"):
        """
        导出MongoDB数据
        支持JSON和CSV格式
        """
        try:
            # 导入MongoDB模型
            from mongodb_integration.models.mongo_models import HouseDocument
            
            logger.info("开始导出MongoDB房源数据...")
            houses = HouseDocument.objects.all()
            
            if export_format.lower() == "json":
                return self._export_to_json(houses)
            elif export_format.lower() == "csv":
                return self._export_to_csv(houses)
            else:
                raise ValueError(f"不支持的导出格式: {export_format}")
                
        except Exception as e:
            logger.error(f"导出MongoDB数据失败: {e}")
            raise
    
    def _export_to_json(self, houses) -> str:
        """导出为JSON格式"""
        json_file = DOCUMENTS_DIR / f"houses_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        houses_data = []
        for house in houses:
            house_dict = {
                "id": str(house.id),
                "title": house.title,
                "rental_type": house.rental_type,
                "city": house.location.city if house.location else "未知",
                "district": house.location.district if house.location else "未知",
                "street": house.location.street if house.location else "未知",
                "area": float(house.features.area) if house.features and house.features.area else 0,
                "room_type": house.features.room_type if house.features else "未知",
                "direction": house.features.direction if house.features else "未知",
                "monthly_rent": float(house.price.monthly_rent) if house.price and house.price.monthly_rent else 0,
                "tags": ",".join(house.tags) if house.tags else "",
                "status": house.status,
                "house_id": house.house_id
            }
            houses_data.append(house_dict)
        
        # 使用Relaxed Extended JSON格式
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(houses_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON数据导出完成: {json_file}")
        return str(json_file)
    
    def _export_to_csv(self, houses) -> str:
        """导出为CSV格式"""
        csv_file = DOCUMENTS_DIR / f"houses_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        houses_data = []
        for house in houses:
            houses_data.append({
                "id": str(house.id),
                "title": house.title,
                "rental_type": house.rental_type,
                "city": house.location.city if house.location else "未知",
                "district": house.location.district if house.location else "未知",
                "street": house.location.street if house.location else "未知",
                "area": float(house.features.area) if house.features and house.features.area else 0,
                "room_type": house.features.room_type if house.features else "未知",
                "direction": house.features.direction if house.features else "未知",
                "monthly_rent": float(house.price.monthly_rent) if house.price and house.price.monthly_rent else 0,
                "tags": ",".join(house.tags) if house.tags else "",
                "status": house.status,
                "house_id": house.house_id
            })
        
        df = pd.DataFrame(houses_data)
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        logger.info(f"CSV数据导出完成: {csv_file}")
        return str(csv_file)
    
    def load_documents_from_json(self, json_file: str) -> List[Document]:
        """从JSON文件加载文档"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                houses_data = json.load(f)
            
            documents = []
            for house in houses_data:
                # 构建房源描述文本
                content = self._build_house_description(house)
                
                # 创建Document对象
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": "mongodb_houses",
                        "house_id": house.get("id"),
                        "type": "house_info",
                        **house  # 包含所有房源信息作为元数据
                    }
                )
                documents.append(doc)
            
            logger.info(f"从JSON加载了 {len(documents)} 个房源文档")
            return documents
            
        except Exception as e:
            logger.error(f"从JSON加载文档失败: {e}")
            raise
    
    def load_documents_from_csv(self, csv_file: str) -> List[Document]:
        """从CSV文件加载文档"""
        try:
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            
            documents = []
            for _, row in df.iterrows():
                house = row.to_dict()
                
                # 构建房源描述文本
                content = self._build_house_description(house)
                
                # 创建Document对象
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": "mongodb_houses",
                        "house_id": str(house.get("id")),
                        "type": "house_info",
                        **house  # 包含所有房源信息作为元数据
                    }
                )
                documents.append(doc)
            
            logger.info(f"从CSV加载了 {len(documents)} 个房源文档")
            return documents
            
        except Exception as e:
            logger.error(f"从CSV加载文档失败: {e}")
            raise
    
    def _build_house_description(self, house: Dict[str, Any]) -> str:
        """构建房源描述文本"""
        # 处理可能的空值，提供更好的默认值
        def safe_str(value, default="未知"):
            if value is None or value == "" or str(value).lower() == "none":
                return default
            return str(value)

        # 构建更详细和结构化的描述
        title = safe_str(house.get('title', ''), "无标题房源")
        rental_type = safe_str(house.get('rental_type', ''), "整租")
        room_type = safe_str(house.get('room_type', ''), "户型未知")

        # 位置信息处理
        city = safe_str(house.get('city', ''), "")
        district = safe_str(house.get('district', ''), "")
        street = safe_str(house.get('street', ''), "")

        # 构建完整地址
        location_parts = [city, district, street]
        location = " ".join([part for part in location_parts if part and part != "未知"])
        if not location:
            location = "位置未知"

        # 数值信息处理
        area = house.get('area', 0)
        area_str = f"{area}平方米" if area and area > 0 else "面积未知"

        monthly_rent = house.get('monthly_rent', 0)
        price_str = f"{monthly_rent}元/月" if monthly_rent and monthly_rent > 0 else "价格面议"

        direction = safe_str(house.get('direction', ''), "朝向未知")
        tags = safe_str(house.get('tags', ''), "无特殊标签")

        # 构建结构化描述，便于LLM理解
        description = f"""【房源详情】
房源名称：{title}
租赁方式：{rental_type}
房屋户型：{room_type}
所在位置：{location}
建筑面积：{area_str}
房屋朝向：{direction}
租赁价格：{price_str}
房源特色：{tags}

【关键信息】户型={room_type}，价格={price_str}，位置={location}，面积={area_str}"""

        return description.strip()
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档为更小的块"""
        try:
            split_docs = self.text_splitter.split_documents(documents)
            logger.info(f"文档分割完成: {len(documents)} -> {len(split_docs)} 个文档块")
            return split_docs
        except Exception as e:
            logger.error(f"文档分割失败: {e}")
            raise
    
    def process_all_data(self, export_format="json") -> List[Document]:
        """
        完整的数据处理流程
        1. 导出MongoDB数据
        2. 加载为Document对象
        3. 分割文档
        """
        try:
            logger.info("开始完整数据处理流程...")
            
            # 1. 导出数据
            data_file = self.export_mongodb_data(export_format)
            
            # 2. 加载文档
            if export_format.lower() == "json":
                documents = self.load_documents_from_json(data_file)
            else:
                documents = self.load_documents_from_csv(data_file)
            
            # 3. 分割文档（房源数据通常不需要分割，但保留此功能）
            # split_documents = self.split_documents(documents)
            
            logger.info(f"数据处理完成，共处理 {len(documents)} 个房源文档")
            return documents
            
        except Exception as e:
            logger.error(f"数据处理流程失败: {e}")
            raise

# 便捷函数
def export_and_process_data(export_format="json") -> List[Document]:
    """导出并处理MongoDB数据的便捷函数"""
    processor = HouseDataProcessor()
    return processor.process_all_data(export_format)
