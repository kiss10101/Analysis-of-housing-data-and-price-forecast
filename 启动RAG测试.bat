@echo off
chcp 65001
echo ========================================
echo 房源数据分析系统 - RAG智能问答模块测试
echo ========================================
echo.

echo [1/3] 检查Python环境...
python --version
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo.
echo [2/3] 安装RAG模块依赖...
pip install faiss-cpu langchain langchain-community volcengine-python-sdk sentence-transformers tiktoken
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo.
echo [3/3] 运行RAG系统测试...
python rag_module/test_rag.py

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 如果测试通过，您可以：
echo 1. 启动Django服务器: python manage.py runserver 8000
echo 2. 访问RAG界面: http://127.0.0.1:8000/mongo/rag/
echo 3. 开始智能问答体验
echo.
pause
