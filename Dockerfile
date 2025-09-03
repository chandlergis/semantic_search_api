FROM python:3.11-slim AS builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpango-1.0-0 \
        libharfbuzz0b \
        libpangoft2-1.0-0 \
        fonts-dejavu \
        fonts-wqy-microhei \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --user -r requirements.txt

# 最终阶段
FROM python:3.11-slim

WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai \
    PATH="/root/.local/bin:${PATH}"

# 安装运行时依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        libpango-1.0-0 \
        libharfbuzz0b \
        libpangoft2-1.0-0 \
        fonts-dejavu \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 从构建阶段复制已安装的包
COPY --from=builder /root/.local /root/.local

# 复制应用代码
COPY app/ ./app/
COPY init_db.py reset_db.py ./

# 创建上传目录
RUN mkdir -p /app/uploads

# 添加健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8500/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8500"]
