#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG模块API密钥管理工具
"""

import json
import os
from pathlib import Path

def get_config_file():
    """获取配置文件路径"""
    return Path(__file__).parent / "api_keys.json"

def load_current_config():
    """加载当前配置"""
    config_file = get_config_file()
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_config(config):
    """保存配置"""
    config_file = get_config_file()
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    print(f"配置已保存到: {config_file}")

def show_current_config():
    """显示当前配置"""
    print("\n=== 当前API密钥配置 ===")
    
    # 检查环境变量
    env_embedding = os.getenv('RAG_EMBEDDING_API_KEY')
    env_llm = os.getenv('RAG_LLM_API_KEY')
    
    if env_embedding or env_llm:
        print("环境变量配置:")
        print(f"  Embedding API Key: {'已设置' if env_embedding else '未设置'}")
        print(f"  LLM API Key: {'已设置' if env_llm else '未设置'}")
    
    # 检查配置文件
    config = load_current_config()
    if config:
        print("配置文件:")
        for key, value in config.items():
            masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"  {key}: {masked_value}")
    else:
        print("配置文件: 未找到")

def update_api_keys():
    """更新API密钥"""
    print("\n=== 更新API密钥 ===")
    config = load_current_config()
    
    print("请输入新的API密钥（直接回车保持不变）:")
    
    # Embedding API Key
    current_embedding = config.get('embedding_api_key', '')
    if current_embedding:
        print(f"当前Embedding API Key: {current_embedding[:8]}...{current_embedding[-4:]}")
    new_embedding = input("新的Embedding API Key: ").strip()
    if new_embedding:
        config['embedding_api_key'] = new_embedding
    
    # LLM API Key
    current_llm = config.get('llm_api_key', '')
    if current_llm:
        print(f"当前LLM API Key: {current_llm[:8]}...{current_llm[-4:]}")
    new_llm = input("新的LLM API Key: ").strip()
    if new_llm:
        config['llm_api_key'] = new_llm
    
    if new_embedding or new_llm:
        save_config(config)
        print("✅ API密钥更新成功！")
        print("⚠️  请重启Django服务以使配置生效。")
    else:
        print("❌ 没有更新任何配置。")

def set_environment_variables():
    """设置环境变量指导"""
    print("\n=== 环境变量设置指导 ===")
    config = load_current_config()
    
    if not config:
        print("❌ 未找到配置文件，请先设置API密钥。")
        return
    
    embedding_key = config.get('embedding_api_key', '')
    llm_key = config.get('llm_api_key', '')
    
    print("Windows命令提示符:")
    print(f'set RAG_EMBEDDING_API_KEY={embedding_key}')
    print(f'set RAG_LLM_API_KEY={llm_key}')
    
    print("\nWindows PowerShell:")
    print(f'$env:RAG_EMBEDDING_API_KEY="{embedding_key}"')
    print(f'$env:RAG_LLM_API_KEY="{llm_key}"')
    
    print("\nLinux/Mac:")
    print(f'export RAG_EMBEDDING_API_KEY="{embedding_key}"')
    print(f'export RAG_LLM_API_KEY="{llm_key}"')

def main():
    """主函数"""
    while True:
        print("\n" + "="*50)
        print("RAG模块API密钥管理工具")
        print("="*50)
        print("1. 查看当前配置")
        print("2. 更新API密钥")
        print("3. 生成环境变量设置命令")
        print("4. 退出")
        
        choice = input("\n请选择操作 (1-4): ").strip()
        
        if choice == '1':
            show_current_config()
        elif choice == '2':
            update_api_keys()
        elif choice == '3':
            set_environment_variables()
        elif choice == '4':
            print("再见！")
            break
        else:
            print("❌ 无效选择，请重试。")

if __name__ == "__main__":
    main()
