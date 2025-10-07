# ========== 阶段1: 构建前端 ==========
FROM node:18-alpine AS frontend-builder

WORKDIR /app/web/frontend

# 复制前端源码
COPY web/frontend/package*.json ./
RUN npm install

COPY web/frontend/ ./
# 构建前端，输出到 /app/web/dist (因为 vite.config.js 设置了 outDir: '../dist')
RUN npm run build

# ========== 阶段2: 构建最终镜像 ==========
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

# 从前端构建阶段复制构建好的文件 (vite 构建输出在 /app/web/dist)
COPY --from=frontend-builder /app/web/dist /app/web/dist

# 启动命令（使用 start.py 同时启动 Web 和主程序）
CMD ["python", "start.py"]
