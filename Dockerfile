FROM python:3.11-slim

WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai


# 安装系统依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
        libpango-1.0-0 \
        libharfbuzz0b \
        libpangoft2-1.0-0 \
        fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*


RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 先复制requirements.txt
COPY requirements.txt .

# Install dependencies using default PyPI source
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 再复制其他文件
COPY . .

# 创建上传目录
RUN mkdir -p /app/uploads

# 添加健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8500/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8500"]
