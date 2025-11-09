# 客服机器人 Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY src/ ./src/
COPY main.py .
COPY config.example.yaml .
COPY data/knowledge_base.example.json ./data/

# 创建必要的目录
RUN mkdir -p logs data

# 创建非 root 用户
RUN useradd -m -u 1000 chatbot && \
    chown -R chatbot:chatbot /app

USER chatbot

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# 暴露端口（如果需要 Web 服务）
# EXPOSE 8000

# 启动命令
CMD ["python", "main.py"]
