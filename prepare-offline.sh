#!/bin/bash

# 离线部署准备脚本
# 在有网络的环境中运行此脚本来准备离线部署包

echo "=== 准备语义搜索系统离线部署包 ==="

# 创建输出目录
mkdir -p offline-package
cd offline-package

echo "1. 构建自定义镜像..."

# 构建后端镜像
cd ..
docker build -t semantic-search-backend:offline .

# 构建前端镜像
cd frontend
docker build -t semantic-search-frontend:offline .
cd ..

echo "2. 拉取基础镜像..."

docker pull postgres:13
docker pull redis:7-alpine

echo "3. 导出镜像为tar文件..."

# 导出基础镜像
docker save -o offline-package/postgres-13.tar postgres:13
docker save -o offline-package/redis-7-alpine.tar redis:7-alpine

# 导出自定义镜像
docker save -o offline-package/semantic-search-backend-offline.tar semantic-search-backend:offline
docker save -o offline-package/semantic-search-frontend-offline.tar semantic-search-frontend:offline

echo "4. 复制配置文件..."

# 复制compose文件
cp docker-compose-offline.yml offline-package/

# 复制部署指南
cp offline-deployment.md offline-package/

echo "5. 创建项目代码快照..."

# 创建项目代码的压缩包（排除不必要的文件）
tar -czf offline-package/semantic-search-code.tar.gz \
  --exclude=node_modules \
  --exclude=__pycache__ \
  --exclude=.git \
  --exclude=uploads \
  --exclude=temp_files \
  .

echo "6. 创建部署脚本..."

cat > offline-package/deploy-offline.sh << 'EOF'
#!/bin/bash

# 离线环境部署脚本

echo "=== 开始部署语义搜索系统 ==="

# 导入镜像
echo "1. 导入Docker镜像..."
docker load -i postgres-13.tar
docker load -i redis-7-alpine.tar
docker load -i semantic-search-backend-offline.tar
docker load -i semantic-search-frontend-offline.tar

# 解压项目代码
echo "2. 解压项目代码..."
tar -xzf semantic-search-code.tar.gz

# 启动服务
echo "3. 启动服务..."
docker-compose -f docker-compose-offline.yml up -d

echo "4. 等待服务启动..."
sleep 30

echo "5. 检查服务状态..."
docker-compose -f docker-compose-offline.yml ps

echo "=== 部署完成 ==="
echo "后端API: http://localhost:9000"
echo "前端应用: http://localhost:30081"
echo "数据库: localhost:5432"
echo "Redis: localhost:6379"
EOF

chmod +x offline-package/deploy-offline.sh

echo "7. 创建文件清单..."

cat > offline-package/FILES.md << 'EOF'
# 离线部署包文件清单

## 镜像文件
- postgres-13.tar - PostgreSQL数据库镜像
- redis-7-alpine.tar - Redis缓存镜像  
- semantic-search-backend-offline.tar - 后端API服务镜像
- semantic-search-frontend-offline.tar - 前端Web应用镜像

## 配置文件
- docker-compose-offline.yml - 离线部署的Docker Compose配置
- offline-deployment.md - 离线部署详细指南

## 项目代码
- semantic-search-code.tar.gz - 项目源代码压缩包

## 部署脚本
- deploy-offline.sh - 一键部署脚本

## 总大小
$(du -sh . | cut -f1)
EOF

echo "=== 准备完成 ==="
echo "离线部署包已创建到: offline-package/"
echo "包含文件:"
ls -la offline-package/
echo ""
echo "请将整个offline-package目录复制到离线环境中"
echo "然后在离线环境中运行: cd offline-package && ./deploy-offline.sh"