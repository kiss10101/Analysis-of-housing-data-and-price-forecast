# -*- coding: utf-8 -*-
"""
RAG智能问答Django视图
"""

import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .decorators import mongo_login_required
from django.utils.decorators import method_decorator
from django.views import View

# 导入RAG系统
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_module.rag_system import get_rag_system, initialize_rag_system, initialize_rag_from_file

logger = logging.getLogger(__name__)

class RAGSystemView(View):
    """RAG系统管理视图"""
    
    def __init__(self):
        super().__init__()
        self.rag_system = get_rag_system()
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

@mongo_login_required
def rag_interface(request):
    """RAG问答界面"""
    try:
        # 检查RAG系统状态
        rag_system = get_rag_system()
        system_stats = rag_system.get_system_stats()
        
        context = {
            'system_initialized': system_stats.get('system_initialized', False),
            'system_stats': system_stats
        }
        
        return render(request, 'mongo/rag_interface.html', context)
        
    except Exception as e:
        logger.error(f"RAG界面加载失败: {e}")
        context = {
            'system_initialized': False,
            'error_message': f"系统初始化失败: {str(e)}"
        }
        return render(request, 'mongo/rag_interface.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def rag_ask(request):
    """处理问答请求"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        top_k = data.get('top_k', 5)
        
        if not question:
            return JsonResponse({
                'success': False,
                'error': '问题不能为空'
            })
        
        # 获取RAG系统
        rag_system = get_rag_system()
        
        # 检查系统是否初始化
        if not rag_system.is_initialized:
            logger.info("RAG系统未初始化，开始初始化...")
            initialize_rag_system()
        
        # 执行问答
        result = rag_system.ask_question(question, top_k)
        
        # 格式化返回结果
        response_data = {
            'success': True,
            'question': result['question'],
            'answer': result['answer'],
            'sources': result.get('sources', []),
            'context_length': result.get('context_length', 0),
            'sort_info': result.get('sort_info', {}),
            'timestamp': result.get('timestamp')
        }
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误'
        })
    except Exception as e:
        logger.error(f"问答处理失败: {e}")
        return JsonResponse({
            'success': False,
            'error': f'问答失败: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def rag_search(request):
    """房源搜索接口"""
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        top_k = data.get('top_k', 5)
        with_scores = data.get('with_scores', False)
        
        if not query:
            return JsonResponse({
                'success': False,
                'error': '搜索查询不能为空'
            })
        
        rag_system = get_rag_system()
        
        if not rag_system.is_initialized:
            initialize_rag_system()
        
        # 执行搜索
        results = rag_system.search_houses(query, top_k, with_scores)
        
        # 格式化结果
        if with_scores:
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': float(score)
                })
        else:
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata
                })
        
        return JsonResponse({
            'success': True,
            'query': query,
            'results': formatted_results,
            'count': len(formatted_results)
        })
        
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        return JsonResponse({
            'success': False,
            'error': f'搜索失败: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def rag_initialize(request):
    """初始化RAG系统"""
    try:
        data = json.loads(request.body)
        force_rebuild = data.get('force_rebuild', False)
        data_source = data.get('data_source', 'mongodb')  # 'mongodb' 或 'file'
        data_file = data.get('data_file', None)

        logger.info(f"开始初始化RAG系统 (force_rebuild={force_rebuild}, data_source={data_source})")

        # 初始化系统
        if data_source == 'file' and data_file:
            stats = initialize_rag_from_file(data_file, force_rebuild)
            message = f'RAG系统从文件初始化完成: {data_file}'
        else:
            stats = initialize_rag_system(force_rebuild, data_source)
            message = 'RAG系统从MongoDB初始化完成'

        return JsonResponse({
            'success': True,
            'message': message,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"RAG系统初始化失败: {e}")
        return JsonResponse({
            'success': False,
            'error': f'初始化失败: {str(e)}'
        })

@require_http_methods(["GET"])
def rag_status(request):
    """获取RAG系统状态"""
    try:
        rag_system = get_rag_system()
        stats = rag_system.get_system_stats()

        return JsonResponse({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        return JsonResponse({
            'success': False,
            'error': f'获取状态失败: {str(e)}'
        })

@require_http_methods(["GET"])
def rag_list_data_files(request):
    """列出可用的数据文件"""
    try:
        rag_system = get_rag_system()
        files = rag_system.list_available_data_files()

        # 格式化文件信息
        formatted_files = []
        for file_info in files:
            formatted_files.append({
                'name': file_info['name'],
                'path': file_info['path'],
                'size_mb': round(file_info['size'] / 1024 / 1024, 2),
                'modified': file_info['modified'],
                'type': file_info['type']
            })

        return JsonResponse({
            'success': True,
            'files': formatted_files,
            'count': len(formatted_files)
        })

    except Exception as e:
        logger.error(f"列出数据文件失败: {e}")
        return JsonResponse({
            'success': False,
            'error': f'列出文件失败: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def rag_clear_cache(request):
    """清空RAG系统缓存"""
    try:
        rag_system = get_rag_system()
        rag_system.clear_cache()
        
        return JsonResponse({
            'success': True,
            'message': '缓存已清空'
        })
        
    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        return JsonResponse({
            'success': False,
            'error': f'清空缓存失败: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def rag_rebuild_index(request):
    """重建向量索引"""
    try:
        data = json.loads(request.body)
        export_format = data.get('export_format', 'json')
        
        logger.info(f"开始重建向量索引 (format={export_format})")
        
        rag_system = get_rag_system()
        rag_system.rebuild_index(export_format)
        
        return JsonResponse({
            'success': True,
            'message': '向量索引重建完成'
        })
        
    except Exception as e:
        logger.error(f"重建索引失败: {e}")
        return JsonResponse({
            'success': False,
            'error': f'重建索引失败: {str(e)}'
        })

# 问答历史记录（简单实现）
@mongo_login_required
def rag_history(request):
    """问答历史记录"""
    # 这里可以实现问答历史记录功能
    # 暂时返回空列表
    return JsonResponse({
        'success': True,
        'history': []
    })

@csrf_exempt
@require_http_methods(["POST"])
def rag_reset_system(request):
    """重置RAG系统（管理员功能）"""
    try:
        logger.info("开始重置RAG系统...")

        rag_system = get_rag_system()

        # 清空缓存
        rag_system.clear_cache()

        # 重置系统状态
        rag_system.is_initialized = False
        rag_system.qa_system.vector_store = None

        # 删除向量索引
        try:
            rag_system.vector_manager.delete_index("house_index")
        except Exception as e:
            logger.warning(f"删除索引时出错: {e}")

        logger.info("RAG系统重置完成")

        return JsonResponse({
            'success': True,
            'message': 'RAG系统已重置'
        })

    except Exception as e:
        logger.error(f"重置RAG系统失败: {e}")
        return JsonResponse({
            'success': False,
            'error': f'重置失败: {str(e)}'
        })
