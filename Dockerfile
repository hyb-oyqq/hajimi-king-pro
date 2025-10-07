FROM registry-1.docker.io/library/python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DOCKER_ENVIRONMENT=true

# 安装系统依赖（包含libxml2和libxslt用于lxml）
RUN apt-get update && apt-get install -y \
    curl \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装uv包管理器
RUN pip install uv

# 使用uv安装Python依赖
RUN uv pip install --system --no-cache -r pyproject.toml

# 复制应用代码
COPY . .

# 启动命令（使用 start.py 同时启动 Web 和主程序）
CMD ["python", "start.py"]
