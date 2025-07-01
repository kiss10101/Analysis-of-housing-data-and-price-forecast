# -*- coding: utf-8 -*-
"""
RAG模块配置文件
"""

import os
from pathlib import Path

# 基础路径配置
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DOCUMENTS_DIR = BASE_DIR / "documents"
VECTOR_DB_DIR = BASE_DIR / "vector_db"

# 使用临时目录避免中文路径问题
import tempfile
TEMP_DIR = Path(tempfile.gettempdir()) / "rag_faiss_index"
FAISS_INDEX_DIR = TEMP_DIR

# 确保目录存在
DOCUMENTS_DIR.mkdir(exist_ok=True)
VECTOR_DB_DIR.mkdir(exist_ok=True)
FAISS_INDEX_DIR.mkdir(exist_ok=True)

# 火山方舟API配置
VOLCANO_CONFIG = {
    # Embedding模型配置
    "embedding_api_key": "b380f961-5cea-4c1b-95e2-8e909befbff5",
    "embedding_model": "doubao-embedding-text-240715",
    "embedding_base_url": "https://ark.cn-beijing.volces.com/api/v3",

    # LLM模型配置
    "llm_api_key": "3c797b67-7ee3-45da-ab41-7dd6971155ae",
    "llm_model": "doubao-1-5-pro-256k-250115",
    "llm_base_url": "https://ark.cn-beijing.volces.com/api/v3",

    # 通用配置
    "max_tokens": 1500,
    "temperature": 0.3,  # 降低随机性，提高准确性
    "top_p": 0.8,        # 核采样参数
    "timeout": 30
}

# FAISS配置
FAISS_CONFIG = {
    "index_type": "IndexFlatIP",  # 内积索引，适合相似度搜索
    "dimension": 1024,            # 向量维度，根据embedding模型调整
    "nprobe": 10,                 # 搜索时的探测数量
    "top_k": 5                    # 默认检索数量
}

# 数据处理配置
DATA_CONFIG = {
    "chunk_size": 500,            # 文本分块大小
    "chunk_overlap": 50,          # 分块重叠大小
    "batch_size": 10,             # 批处理大小
    "max_retries": 3,             # 最大重试次数
    "retry_delay": 1              # 重试延迟(秒)
}

# 问答系统配置
QA_CONFIG = {
    "max_context_length": 3000,   # 最大上下文长度
    "answer_max_tokens": 800,     # 答案最大token数
    "similarity_threshold": 0.6,  # 降低相似度阈值，增加召回
    "enable_smart_sort": True,    # 启用智能排序
    "cache_enabled": True,        # 启用缓存
    "cache_ttl": 3600,           # 缓存过期时间(秒)
    "top_k": 8                   # 增加检索数量
}

# 智能排序关键词
SORT_KEYWORDS = {
    "price": ["价格", "便宜", "贵", "费用", "租金", "最低", "最高"],
    "area": ["面积", "大", "小", "平米", "平方"],
    "location": ["位置", "地段", "区域", "附近", "距离"],
    "type": ["户型", "房型", "室", "厅", "卫"]
}

# 排序方向关键词
SORT_DIRECTION = {
    "asc": ["最少", "最小", "最低", "最便宜", "最近"],
    "desc": ["最多", "最大", "最高", "最贵", "最远"]
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": BASE_DIR / "logs" / "rag.log"
}

# 确保日志目录存在
(BASE_DIR / "logs").mkdir(exist_ok=True)
