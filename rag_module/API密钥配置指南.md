# RAG模块API密钥配置指南

## 🔐 安全配置方式

RAG模块支持三种API密钥配置方式，按优先级排序：

### 1. 环境变量配置（推荐）

在系统环境变量中设置：

```bash
# Windows (命令提示符)
set RAG_EMBEDDING_API_KEY=your-embedding-api-key
set RAG_LLM_API_KEY=your-llm-api-key

# Windows (PowerShell)
$env:RAG_EMBEDDING_API_KEY="your-embedding-api-key"
$env:RAG_LLM_API_KEY="your-llm-api-key"

# Linux/Mac
export RAG_EMBEDDING_API_KEY="your-embedding-api-key"
export RAG_LLM_API_KEY="your-llm-api-key"
```

### 2. 配置文件（适合开发环境）

编辑 `rag_module/api_keys.json` 文件：

```json
{
    "embedding_api_key": "your-embedding-api-key",
    "llm_api_key": "your-llm-api-key"
}
```

### 3. 默认值（仅用于测试）

如果以上两种方式都没有配置，系统会使用默认值。

## 🔧 模型配置

除了API密钥，您还可以通过环境变量配置模型参数：

```bash
# 模型选择
RAG_EMBEDDING_MODEL=doubao-embedding-text-240715
RAG_LLM_MODEL=doubao-1-5-pro-256k-250115

# API端点
RAG_EMBEDDING_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
RAG_LLM_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# 生成参数
RAG_MAX_TOKENS=1500
RAG_TEMPERATURE=0.3
RAG_TOP_P=0.8
RAG_TIMEOUT=30
```

## 🚀 快速更换API密钥

### 方法1：修改配置文件
1. 编辑 `rag_module/api_keys.json`
2. 重启Django服务

### 方法2：设置环境变量
1. 设置环境变量
2. 重启Django服务

### 方法3：临时测试
在Python代码中临时修改：
```python
from rag_module.config import VOLCANO_CONFIG
VOLCANO_CONFIG["embedding_api_key"] = "new-key"
VOLCANO_CONFIG["llm_api_key"] = "new-key"
```

## 🔒 安全建议

1. **生产环境**：使用环境变量
2. **开发环境**：使用配置文件，但不要提交到版本控制
3. **测试环境**：可以使用默认值
4. **密钥轮换**：定期更换API密钥
5. **权限控制**：限制配置文件的访问权限

## 📝 支持的模型

### 火山引擎Doubao系列
- **Embedding模型**：doubao-embedding-text-240715
- **LLM模型**：
  - doubao-1-5-pro-256k-250115
  - doubao-1-5-pro-32k-250115
  - doubao-1-5-lite-32k-250115

### 其他模型
如需使用其他模型，请修改相应的配置参数。

## ❓ 常见问题

**Q: 如何验证配置是否正确？**
A: 访问RAG页面，系统会自动检测配置状态。

**Q: 配置文件在哪里？**
A: `rag_module/api_keys.json`

**Q: 如何重置配置？**
A: 删除配置文件，重新创建或使用环境变量。
