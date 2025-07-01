# -*- coding: utf-8 -*-
"""
向量存储模块
基于FAISS的向量数据库实现
"""

import os
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import faiss
import numpy as np
from langchain.schema import Document
from langchain_community.vectorstores import FAISS

from .config import FAISS_INDEX_DIR, FAISS_CONFIG, LOGGING_CONFIG
from .llm_module import VolcanoEmbeddings

# 配置日志
logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)

class HouseVectorStore:
    """房源向量存储管理器"""
    
    def __init__(self, embeddings: VolcanoEmbeddings = None):
        self.embeddings = embeddings or VolcanoEmbeddings()
        self.vector_store = None
        self.index_path = FAISS_INDEX_DIR
        
        # 确保索引目录存在
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("房源向量存储管理器初始化完成")
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """
        创建向量存储
        从文档列表创建FAISS向量索引
        """
        try:
            logger.info(f"开始创建向量存储，文档数量: {len(documents)}")
            
            if not documents:
                raise ValueError("文档列表为空，无法创建向量存储")
            
            # 使用LangChain的FAISS包装器
            vector_store = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
            
            self.vector_store = vector_store
            logger.info("向量存储创建完成")
            
            return vector_store
            
        except Exception as e:
            logger.error(f"创建向量存储失败: {e}")
            raise
    
    def save_vector_store(self, vector_store: FAISS = None, index_name: str = "house_index"):
        """
        保存向量存储到磁盘
        """
        try:
            vs = vector_store or self.vector_store
            if not vs:
                raise ValueError("没有可保存的向量存储")

            save_path = self.index_path / index_name
            # 确保保存目录存在
            save_path.mkdir(parents=True, exist_ok=True)

            vs.save_local(str(save_path))

            logger.info(f"向量存储已保存到: {save_path}")

        except Exception as e:
            logger.error(f"保存向量存储失败: {e}")
            raise
    
    def load_vector_store(self, index_name: str = "house_index") -> FAISS:
        """
        从磁盘加载向量存储
        """
        try:
            load_path = self.index_path / index_name
            
            if not load_path.exists():
                raise FileNotFoundError(f"向量索引不存在: {load_path}")
            
            vector_store = FAISS.load_local(
                str(load_path),
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True  # 允许反序列化
            )
            
            self.vector_store = vector_store
            logger.info(f"向量存储已从 {load_path} 加载")
            
            return vector_store
            
        except Exception as e:
            logger.error(f"加载向量存储失败: {e}")
            raise

    def delete_index(self, index_name: str = "house_index"):
        """
        删除向量索引
        """
        try:
            import shutil

            index_path = self.index_path / index_name
            if index_path.exists():
                shutil.rmtree(index_path)
                logger.info(f"向量索引已删除: {index_path}")
            else:
                logger.warning(f"向量索引不存在: {index_path}")

        except Exception as e:
            logger.error(f"删除向量索引失败: {e}")
            raise

    def add_documents(self, documents: List[Document]):
        """
        向现有向量存储添加文档
        """
        try:
            if not self.vector_store:
                raise ValueError("向量存储未初始化，请先创建或加载向量存储")
            
            self.vector_store.add_documents(documents)
            logger.info(f"已添加 {len(documents)} 个文档到向量存储")
            
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            raise
    
    def search(self, query: str, k: int = 5, score_threshold: float = None) -> List[Document]:
        """
        搜索相似文档
        """
        try:
            if not self.vector_store:
                raise ValueError("向量存储未初始化")
            
            if score_threshold:
                # 使用相似度阈值搜索
                docs_and_scores = self.vector_store.similarity_search_with_score(
                    query, k=k
                )
                docs = [doc for doc, score in docs_and_scores if score >= score_threshold]
            else:
                # 普通相似度搜索
                docs = self.vector_store.similarity_search(query, k=k)
            
            logger.info(f"搜索完成，返回 {len(docs)} 个文档")
            return docs
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            raise
    
    def search_with_scores(self, query: str, k: int = 5) -> List[tuple]:
        """
        搜索相似文档并返回相似度分数
        """
        try:
            if not self.vector_store:
                raise ValueError("向量存储未初始化")
            
            docs_and_scores = self.vector_store.similarity_search_with_score(query, k=k)
            logger.info(f"搜索完成，返回 {len(docs_and_scores)} 个文档和分数")
            
            return docs_and_scores
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            raise
    
    def get_vector_count(self) -> int:
        """获取向量数量"""
        try:
            if not self.vector_store:
                return 0
            
            # 通过FAISS索引获取向量数量
            return self.vector_store.index.ntotal
            
        except Exception as e:
            logger.warning(f"获取向量数量失败: {e}")
            return 0
    
    def delete_index(self, index_name: str = "house_index"):
        """删除索引文件"""
        try:
            index_path = self.index_path / index_name
            
            if index_path.exists():
                # 删除索引目录及其内容
                import shutil
                shutil.rmtree(index_path)
                logger.info(f"索引已删除: {index_path}")
            else:
                logger.warning(f"索引不存在: {index_path}")
                
        except Exception as e:
            logger.error(f"删除索引失败: {e}")
            raise
    
    def rebuild_index(self, documents: List[Document], index_name: str = "house_index"):
        """重建索引"""
        try:
            logger.info("开始重建索引...")
            
            # 删除旧索引
            self.delete_index(index_name)
            
            # 创建新索引
            vector_store = self.create_vector_store(documents)
            
            # 保存新索引
            self.save_vector_store(vector_store, index_name)
            
            logger.info("索引重建完成")
            
        except Exception as e:
            logger.error(f"重建索引失败: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """获取向量存储统计信息"""
        return {
            "vector_count": self.get_vector_count(),
            "index_path": str(self.index_path),
            "vector_store_ready": self.vector_store is not None,
            "embeddings_model": self.embeddings.model if hasattr(self.embeddings, 'model') else "unknown"
        }

# 便捷函数
def create_and_save_vector_store(documents: List[Document], index_name: str = "house_index") -> HouseVectorStore:
    """创建并保存向量存储的便捷函数"""
    manager = HouseVectorStore()
    vector_store = manager.create_vector_store(documents)
    manager.save_vector_store(vector_store, index_name)
    return manager

def load_vector_store(index_name: str = "house_index") -> HouseVectorStore:
    """加载向量存储的便捷函数"""
    manager = HouseVectorStore()
    manager.load_vector_store(index_name)
    return manager
