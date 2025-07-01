# -*- coding: utf-8 -*-
"""
大语言模型集成模块
基于火山方舟API的Embedding和LLM实现
"""

import json
import time
import logging
import re
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from langchain.embeddings.base import Embeddings
from langchain.llms.base import LLM
from langchain.schema import Document
import numpy as np

from .config import VOLCANO_CONFIG, QA_CONFIG, SORT_KEYWORDS, SORT_DIRECTION, LOGGING_CONFIG

# 配置日志
logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)

class VolcanoEmbeddings(Embeddings):
    """火山方舟Embedding模型封装"""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or VOLCANO_CONFIG["embedding_api_key"]
        self.model = model or VOLCANO_CONFIG["embedding_model"]
        self.base_url = VOLCANO_CONFIG["embedding_base_url"]
        self.timeout = VOLCANO_CONFIG["timeout"]
        self.max_retries = 3
        self.retry_delay = 1

        if not self.api_key:
            raise ValueError("火山方舟Embedding API密钥未配置")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文档"""
        try:
            logger.info(f"开始嵌入 {len(texts)} 个文档...")
            
            # 分批处理
            batch_size = 10
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = self._embed_batch(batch_texts)
                all_embeddings.extend(batch_embeddings)
                
                # 避免API限流
                if i + batch_size < len(texts):
                    time.sleep(0.1)
            
            logger.info(f"文档嵌入完成，共 {len(all_embeddings)} 个向量")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"文档嵌入失败: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """嵌入单个查询"""
        try:
            embeddings = self._embed_batch([text])
            return embeddings[0] if embeddings else []
        except Exception as e:
            logger.error(f"查询嵌入失败: {e}")
            raise
    
    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入实现"""
        for attempt in range(self.max_retries):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "input": texts
                }
                
                response = requests.post(
                    f"{self.base_url}/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    embeddings = [item["embedding"] for item in result["data"]]
                    return embeddings
                else:
                    logger.warning(f"API请求失败 (状态码: {response.status_code}): {response.text}")
                    
            except Exception as e:
                logger.warning(f"嵌入请求失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                else:
                    raise
        
        raise Exception("所有嵌入请求尝试都失败了")

class VolcanoLLM:
    """火山方舟大语言模型封装"""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or VOLCANO_CONFIG["llm_api_key"]
        self.model = model or VOLCANO_CONFIG["llm_model"]
        self.base_url = VOLCANO_CONFIG["llm_base_url"]
        self.max_tokens = VOLCANO_CONFIG["max_tokens"]
        self.temperature = VOLCANO_CONFIG["temperature"]
        self.top_p = VOLCANO_CONFIG.get("top_p", 0.8)
        self.timeout = VOLCANO_CONFIG["timeout"]

        if not self.api_key:
            raise ValueError("火山方舟LLM API密钥未配置")
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """调用LLM生成回答"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"LLM请求失败 (状态码: {response.status_code}): {response.text}")
                return "抱歉，我现在无法回答您的问题，请稍后再试。"
                
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            return "抱歉，我现在无法回答您的问题，请稍后再试。"

class SmartSorter:
    """智能排序器"""
    
    def __init__(self):
        self.sort_keywords = SORT_KEYWORDS
        self.sort_direction = SORT_DIRECTION
    
    def detect_sorting_intent(self, question: str) -> Dict[str, Any]:
        """检测排序意图"""
        question_lower = question.lower()
        
        # 检测排序字段
        sort_field = None
        for field, keywords in self.sort_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                sort_field = field
                break
        
        # 检测排序方向
        sort_order = "desc"  # 默认降序
        for direction, keywords in self.sort_direction.items():
            if any(keyword in question_lower for keyword in keywords):
                sort_order = direction
                break
        
        return {
            "has_sort_intent": sort_field is not None,
            "sort_field": sort_field,
            "sort_order": sort_order
        }
    
    def sort_documents(self, documents: List[Document], sort_info: Dict[str, Any]) -> List[Document]:
        """根据排序信息对文档进行排序"""
        if not sort_info["has_sort_intent"]:
            return documents
        
        sort_field = sort_info["sort_field"]
        sort_order = sort_info["sort_order"]
        
        try:
            # 提取排序值
            def get_sort_value(doc):
                metadata = doc.metadata

                if sort_field == "price":
                    return float(metadata.get("monthly_rent", 0))
                elif sort_field == "area":
                    return float(metadata.get("area", 0))
                elif sort_field == "location":
                    # 简单的位置排序，可以根据需要扩展
                    return metadata.get("city", "")
                elif sort_field == "type":
                    # 按户型排序，提取数字
                    room_type_str = metadata.get("room_type", "")
                    numbers = re.findall(r'\d+', str(room_type_str))
                    return int(numbers[0]) if numbers else 0
                else:
                    return 0
            
            # 执行排序
            reverse = (sort_order == "desc")
            sorted_docs = sorted(documents, key=get_sort_value, reverse=reverse)
            
            logger.info(f"文档排序完成: 按{sort_field}{'降序' if reverse else '升序'}排列")
            return sorted_docs

        except Exception as e:
            logger.warning(f"文档排序失败: {e}")
            return documents

class HouseQASystem:
    """房源智能问答系统核心类"""

    def __init__(self, vector_store=None):
        """初始化问答系统"""
        self.embeddings = VolcanoEmbeddings()
        self.llm = VolcanoLLM()
        self.sorter = SmartSorter()
        self.vector_store = vector_store
        self.cache = {}  # 简单的内存缓存

        logger.info("房源智能问答系统初始化完成")

    def set_vector_store(self, vector_store):
        """设置向量存储"""
        self.vector_store = vector_store
        logger.info("向量存储设置完成")

    def ask(self, question: str, top_k: int = None) -> Dict[str, Any]:
        """
        核心问答方法
        实现完整的RAG流程
        """
        try:
            logger.info(f"收到问题: {question}")

            # 检查缓存
            if QA_CONFIG["cache_enabled"] and question in self.cache:
                logger.info("从缓存返回答案")
                return self.cache[question]

            # 1. 检测排序意图
            sort_info = self.sorter.detect_sorting_intent(question)
            logger.info(f"排序意图检测: {sort_info}")

            # 2. 向量检索
            if not self.vector_store:
                raise ValueError("向量存储未初始化")

            k = top_k or QA_CONFIG.get("top_k", 5)
            docs = self.vector_store.similarity_search(question, k=k)
            logger.info(f"检索到 {len(docs)} 个相关文档")

            # 3. 智能排序
            if sort_info["has_sort_intent"] and QA_CONFIG["enable_smart_sort"]:
                docs = self.sorter.sort_documents(docs, sort_info)

            # 4. 构建上下文
            context = self._build_context(docs, question)

            # 5. 生成答案
            answer = self._generate_answer(question, context, sort_info)

            # 6. 构建返回结果
            result = {
                "question": question,
                "answer": answer,
                "sources": [doc.metadata for doc in docs],
                "context_length": len(context),
                "sort_info": sort_info,
                "timestamp": time.time()
            }

            # 缓存结果
            if QA_CONFIG["cache_enabled"]:
                self.cache[question] = result

            logger.info("问答完成")
            return result

        except Exception as e:
            logger.error(f"问答失败: {e}")
            return {
                "question": question,
                "answer": "抱歉，我无法回答您的问题，请稍后再试。",
                "sources": [],
                "error": str(e),
                "timestamp": time.time()
            }

    def _build_context(self, docs: List[Document], question: str) -> str:
        """构建上下文"""
        context_parts = []

        # 去重处理，避免重复房源
        seen_houses = set()
        unique_docs = []

        for doc in docs:
            metadata = doc.metadata
            # 使用标题+位置+价格作为唯一标识
            house_key = f"{metadata.get('title', '')}-{metadata.get('city', '')}-{metadata.get('monthly_rent', '')}"
            if house_key not in seen_houses:
                seen_houses.add(house_key)
                unique_docs.append(doc)

        for i, doc in enumerate(unique_docs, 1):
            metadata = doc.metadata

            # 处理空值和None值
            def clean_value(value, default="未知"):
                if value is None or str(value).lower() == "none" or value == "":
                    return default
                return str(value)

            title = clean_value(metadata.get('title'), "无标题房源")
            rental_type = clean_value(metadata.get('rental_type'), "整租")
            room_type = clean_value(metadata.get('room_type'), "户型未知")

            # 位置信息清理
            city = clean_value(metadata.get('city'), "")
            district = clean_value(metadata.get('district'), "")
            street = clean_value(metadata.get('street'), "")

            location_parts = [city, district, street]
            location = " ".join([part for part in location_parts if part and part != "未知"])
            if not location:
                location = "位置未知"

            # 数值处理
            area = metadata.get('area', 0)
            area_str = f"{area}平方米" if area and area > 0 else "面积未知"

            monthly_rent = metadata.get('monthly_rent', 0)
            price_str = f"{monthly_rent}元/月" if monthly_rent and monthly_rent > 0 else "价格面议"

            direction = clean_value(metadata.get('direction'), "朝向未知")
            tags = clean_value(metadata.get('tags'), "无特殊标签")

            # 构建清晰的房源信息
            house_info = f"""房源{i}【{title}】
- 户型：{room_type}
- 位置：{location}
- 面积：{area_str}
- 价格：{price_str}
- 朝向：{direction}
- 特色：{tags}
- 租赁方式：{rental_type}"""

            context_parts.append(house_info)

        context = "\n\n".join(context_parts)

        # 检查上下文长度
        max_length = QA_CONFIG["max_context_length"]
        if len(context) > max_length:
            # 智能截断，保留完整的房源信息
            truncated_parts = []
            current_length = 0
            for part in context_parts:
                if current_length + len(part) <= max_length:
                    truncated_parts.append(part)
                    current_length += len(part)
                else:
                    break
            context = "\n\n".join(truncated_parts)
            logger.warning(f"上下文被截断，保留 {len(truncated_parts)} 个房源信息")

        return context

    def _generate_answer(self, question: str, context: str, sort_info: Dict[str, Any]) -> str:
        """生成答案"""
        # 构建优化的提示词
        if sort_info["has_sort_intent"]:
            prompt = f"""你是一个专业的房源咨询助手。请基于以下房源信息回答用户问题。

房源数据：
{context}

用户问题：{question}

回答要求：
1. 用户问题包含排序需求，请严格按照排序要求组织答案
2. 必须提供准确的价格数字，不要遗漏价格信息
3. 回答要自然流畅，不要使用"-"、"•"等特殊符号开头
4. 直接回答问题，然后详细介绍相关房源
5. 每个房源信息要包含：标题、户型、位置、价格、面积

请用自然的中文回答，语言要流畅专业。"""
        else:
            prompt = f"""你是一个专业的房源咨询助手。请基于以下房源信息回答用户问题。

房源数据：
{context}

用户问题：{question}

回答要求：
1. 必须基于提供的房源数据回答，不要编造信息
2. 价格信息必须准确，包含具体数字
3. 户型信息要准确匹配用户需求
4. 回答要自然流畅，不要使用"-"、"•"等特殊符号开头
5. 直接回答问题，然后详细介绍相关房源
6. 每个房源信息要包含：标题、户型、位置、价格、面积

请用自然的中文回答，语言要流畅专业。"""

        # 调用LLM生成答案
        answer = self.llm._call(prompt)
        return answer

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("缓存已清空")

    def get_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        return {
            "cache_size": len(self.cache),
            "vector_store_ready": self.vector_store is not None,
            "config": QA_CONFIG
        }
