# -*- coding: utf-8 -*-
"""
RAG系统主入口
整合数据处理、向量存储和问答功能
"""

import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from .config import LOGGING_CONFIG
from .data_process import HouseDataProcessor, export_and_process_data
from .vector_store import HouseVectorStore, create_and_save_vector_store, load_vector_store
from .llm_module import HouseQASystem

# 配置日志
logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)

class HouseRAGSystem:
    """房源RAG系统主类"""
    
    def __init__(self):
        self.data_processor = HouseDataProcessor()
        self.vector_manager = HouseVectorStore()
        self.qa_system = HouseQASystem()
        self.is_initialized = False
        
        logger.info("房源RAG系统初始化完成")
    
    def setup_system(self, force_rebuild: bool = False, data_source: str = "mongodb", data_file: str = None):
        """
        设置RAG系统
        包括数据处理、向量索引构建和问答系统初始化

        Args:
            force_rebuild: 是否强制重建索引
            data_source: 数据源类型 ("mongodb" 或 "file")
            data_file: 数据文件路径（当data_source="file"时使用）
        """
        try:
            logger.info(f"开始设置RAG系统... (数据源: {data_source})")

            index_name = "house_index"
            index_exists = self._check_index_exists(index_name)

            if force_rebuild or not index_exists:
                logger.info("构建新的向量索引...")

                # 1. 处理数据
                if data_source == "file" and data_file:
                    documents = self._load_documents_from_file(data_file)
                else:
                    # 默认从MongoDB加载
                    documents = self.data_processor.process_all_data("json")

                # 2. 创建向量存储
                vector_store = self.vector_manager.create_vector_store(documents)

                # 3. 保存向量存储
                self.vector_manager.save_vector_store(vector_store, index_name)

            else:
                logger.info("加载现有向量索引...")

                # 加载现有向量存储
                vector_store = self.vector_manager.load_vector_store(index_name)

            # 4. 初始化问答系统
            self.qa_system.set_vector_store(vector_store)

            self.is_initialized = True
            logger.info("RAG系统设置完成")

            return self.get_system_stats()

        except Exception as e:
            logger.error(f"RAG系统设置失败: {e}")
            raise
    
    def ask_question(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """
        问答接口
        """
        if not self.is_initialized:
            raise ValueError("RAG系统未初始化，请先调用setup_system()")
        
        return self.qa_system.ask(question, top_k)
    
    def add_new_data(self, export_format: str = "json"):
        """
        添加新数据到现有索引
        """
        try:
            if not self.is_initialized:
                raise ValueError("RAG系统未初始化")
            
            logger.info("添加新数据到向量索引...")
            
            # 处理新数据
            documents = self.data_processor.process_all_data(export_format)
            
            # 添加到现有向量存储
            self.vector_manager.add_documents(documents)
            
            # 保存更新后的向量存储
            self.vector_manager.save_vector_store()
            
            logger.info("新数据添加完成")
            
        except Exception as e:
            logger.error(f"添加新数据失败: {e}")
            raise
    
    def rebuild_index(self, export_format: str = "json"):
        """
        重建向量索引
        """
        try:
            logger.info("重建向量索引...")
            
            # 处理数据
            documents = self.data_processor.process_all_data(export_format)
            
            # 重建索引
            self.vector_manager.rebuild_index(documents)
            
            # 重新加载向量存储
            vector_store = self.vector_manager.load_vector_store()
            self.qa_system.set_vector_store(vector_store)
            
            self.is_initialized = True
            logger.info("向量索引重建完成")
            
        except Exception as e:
            logger.error(f"重建索引失败: {e}")
            raise
    
    def search_houses(self, query: str, top_k: int = 5, with_scores: bool = False):
        """
        搜索房源
        直接返回搜索结果，不生成答案
        """
        if not self.is_initialized:
            raise ValueError("RAG系统未初始化")
        
        if with_scores:
            return self.vector_manager.search_with_scores(query, top_k)
        else:
            return self.vector_manager.search(query, top_k)
    
    def clear_cache(self):
        """清空问答系统缓存"""
        if self.qa_system:
            self.qa_system.clear_cache()
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        stats = {
            "system_initialized": self.is_initialized,
            "timestamp": __import__('time').time()
        }
        
        if self.vector_manager:
            stats["vector_store"] = self.vector_manager.get_stats()
        
        if self.qa_system:
            stats["qa_system"] = self.qa_system.get_stats()
        
        return stats
    
    def _check_index_exists(self, index_name: str = "house_index") -> bool:
        """检查索引是否存在"""
        from .config import FAISS_INDEX_DIR
        index_path = FAISS_INDEX_DIR / index_name
        return index_path.exists() and any(index_path.iterdir())

    def _load_documents_from_file(self, file_path: str) -> List:
        """从文件加载文档"""
        try:
            logger.info(f"从文件加载数据: {file_path}")

            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"数据文件不存在: {file_path}")

            if file_path.suffix.lower() == '.json':
                documents = self.data_processor.load_documents_from_json(str(file_path))
            elif file_path.suffix.lower() == '.csv':
                documents = self.data_processor.load_documents_from_csv(str(file_path))
            else:
                raise ValueError(f"不支持的文件格式: {file_path.suffix}")

            logger.info(f"从文件加载了 {len(documents)} 个文档")
            return documents

        except Exception as e:
            logger.error(f"从文件加载数据失败: {e}")
            raise

    def list_available_data_files(self) -> List[Dict[str, Any]]:
        """列出可用的数据文件"""
        from .config import DOCUMENTS_DIR

        files = []
        for file_path in DOCUMENTS_DIR.glob("*.json"):
            try:
                stat = file_path.stat()
                files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "type": "json"
                })
            except Exception:
                continue

        for file_path in DOCUMENTS_DIR.glob("*.csv"):
            try:
                stat = file_path.stat()
                files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "type": "csv"
                })
            except Exception:
                continue

        # 按修改时间排序
        files.sort(key=lambda x: x["modified"], reverse=True)
        return files

# 全局RAG系统实例
_rag_system_instance = None

def get_rag_system() -> HouseRAGSystem:
    """获取RAG系统单例"""
    global _rag_system_instance
    if _rag_system_instance is None:
        _rag_system_instance = HouseRAGSystem()
    return _rag_system_instance

def initialize_rag_system(force_rebuild: bool = False, data_source: str = "mongodb", data_file: str = None) -> Dict[str, Any]:
    """初始化RAG系统的便捷函数"""
    rag_system = get_rag_system()
    return rag_system.setup_system(force_rebuild, data_source, data_file)

def initialize_rag_from_file(data_file: str, force_rebuild: bool = True) -> Dict[str, Any]:
    """从文件初始化RAG系统的便捷函数"""
    rag_system = get_rag_system()
    return rag_system.setup_system(force_rebuild, "file", data_file)

def ask_question(question: str, top_k: int = 5) -> Dict[str, Any]:
    """问答的便捷函数"""
    rag_system = get_rag_system()
    return rag_system.ask_question(question, top_k)

def search_houses(query: str, top_k: int = 5, with_scores: bool = False):
    """搜索房源的便捷函数"""
    rag_system = get_rag_system()
    return rag_system.search_houses(query, top_k, with_scores)

# 快速测试函数
def quick_test():
    """快速测试RAG系统"""
    try:
        logger.info("开始RAG系统快速测试...")
        
        # 初始化系统
        stats = initialize_rag_system()
        logger.info(f"系统初始化完成: {stats}")
        
        # 测试问答
        test_questions = [
            "海珠区有什么房子？",
            "3室2厅的房子价格如何？",
            "最便宜的房子在哪里？",
            "面积最大的房源是什么？"
        ]
        
        for question in test_questions:
            logger.info(f"测试问题: {question}")
            result = ask_question(question)
            logger.info(f"答案: {result['answer'][:100]}...")
        
        logger.info("RAG系统测试完成")
        return True
        
    except Exception as e:
        logger.error(f"RAG系统测试失败: {e}")
        return False

if __name__ == "__main__":
    # 运行快速测试
    quick_test()
