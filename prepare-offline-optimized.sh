#!/bin/bash

# 离线部署准备脚本 (优化版)
# 在有网络的环境中运行此脚本来准备离线部署包

echo "=== 准备语义搜索系统离线部署包 (优化版) ==="

# 创建输出目录
mkdir -p offline-package
cd offline-package

echo "1. 清理并构建自定义镜像..."

# 返回项目根目录
cd ..

# 清理Docker缓存和临时文件
echo "清理Docker缓存..."
docker system prune -f

# 构建后端镜像
echo "构建后端镜像..."
docker build --no-cache -t semantic-search-backend:offline .

# 构建前端镜像
echo "构建前端镜像..."
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
cp OFFLINE_DEPLOYMENT.md offline-package/

echo "5. 创建项目代码快照..."

# 创建项目代码的压缩包（排除不必要的文件）\ntar -czf offline-package/semantic-search-code.tar.gz \\\n  --exclude=node_modules \\\n  --exclude=__pycache__ \\\n  --exclude=.git \\\n  --exclude=uploads \\\n  --exclude=temp_files \\\n  --exclude=offline-package \\\n  --exclude=*.tar \\\n  --exclude=*.tar.gz \\\n  --exclude=backend.tar \\\n  --exclude=frontend.tar \\\n  --exclude=redis.tar \\\n  --exclude=docker-compose.yml \\\n  --exclude=docker-compose-offline.yml \\\n  --exclude=Dockerfile.dev \\\n  --exclude=prepare-offline.sh \\\n  --exclude=prepare-offline-optimized.sh \\\n  --exclude=offline-deployment-optimized.md \\\n  --exclude=debug_highlight.py \\\n  --exclude=test_highlight.py \\\n  --exclude=two_file_compaere.md \\\n  --exclude=优化对比.md \\\n  --exclude=.gitignore \\\n  --exclude=package.json \\\n  --exclude=README.md \\\n  --exclude=OFFLINE_DEPLOYMENT.md \\\n  --exclude=offline-deployment.md \\\n  --exclude=nginx.conf \\\n  app/ \\\n  frontend/dist/ \\\n  frontend/nginx.conf \\\n  init_db.py \\\n  reset_db.py \\\n  requirements.txt

echo "6. 创建部署脚本..."

cat > offline-package/deploy-offline.sh << 'EOF'
#!/bin/bash

# 离线环境部署脚本 (优化版)

echo "=== 开始部署语义搜索系统 ==="

# 检查必要文件
if [ ! -f postgres-13.tar ] || [ ! -f redis-7-alpine.tar ] || [ ! -f semantic-search-backend-offline.tar ] || [ ! -f semantic-search-frontend-offline.tar ]; then
  echo "错误: 缺少必要的镜像文件"
  echo "请确保以下文件存在:"
  echo " - postgres-13.tar"
  echo " - redis-7-alpine.tar"
  echo " - semantic-search-backend-offline.tar"
  echo " - semantic-search-frontend-offline.tar"
  exit 1
fi

# 导入镜像
echo "1. 导入Docker镜像..."
docker load -i postgres-13.tar
docker load -i redis-7-alpine.tar
docker load -i semantic-search-backend-offline.tar
docker load -i semantic-search-frontend-offline.tar

# 检查是否需要解压代码
if [ ! -d "app" ] || [ ! -f "docker-compose-offline.yml" ]; then
  echo "2. 解压项目代码..."
  tar -xzf semantic-search-code.tar.gz
fi

# 创建必要的目录
echo "3. 创建必要的目录..."
mkdir -p uploads temp_files

# 设置目录权限
chmod -R 755 uploads temp_files

# 启动服务
echo "4. 启动服务..."
docker-compose -f docker-compose-offline.yml up -d

echo "5. 等待服务启动..."
sleep 30

echo "6. 检查服务状态..."
docker-compose -f docker-compose-offline.yml ps

echo "=== 部署完成 ==="
echo "后端API: http://localhost:9001"
echo "前端应用: http://localhost:30082"
echo "数据库: localhost:5433"
echo "Redis: localhost:6380"

echo ""
echo "如果需要查看日志，请运行:"
echo "  docker-compose -f docker-compose-offline.yml logs -f"
echo ""
echo "如果需要停止服务，请运行:"
echo "  docker-compose -f docker-compose-offline.yml down"
EOF

chmod +x offline-package/deploy-offline.sh

echo "7. 创建清理脚本..."

cat > offline-package/cleanup.sh << 'EOF'
#!/bin/bash

# 清理脚本 - 用于卸载服务和删除数据

echo "=== 清理语义搜索系统 ==="

# 停止并删除容器
echo "1. 停止并删除容器..."
docker-compose -f docker-compose-offline.yml down

# 删除镜像
echo "2. 删除镜像..."
docker rmi semantic-search-backend:offline semantic-search-frontend:offline postgres:13 redis:7-alpine

# 删除卷
echo "3. 删除数据卷..."
docker volume rm $(docker volume ls -q | grep semantic_search_api)

# 删除目录
echo "4. 删除数据目录..."
rm -rf uploads temp_files

echo "=== 清理完成 ==="
EOF

chmod +x offline-package/cleanup.sh

echo "8. 创建文件清单..."

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
- OFFLINE_DEPLOYMENT.md - 另一份离线部署指南

## 项目代码
- semantic-search-code.tar.gz - 项目源代码压缩包

## 部署脚本
- deploy-offline.sh - 一键部署脚本
- cleanup.sh - 清理脚本

## 总大小
EOF

echo "总大小: $(du -sh . | cut -f1)" >> offline-package/FILES.md

echo "=== 准备完成 ==="
echo "离线部署包已创建到: offline-package/"
echo "包含文件:"
ls -la offline-package/
echo ""
echo "请将整个offline-package目录复制到离线环境中"
echo "然后在离线环境中运行: cd offline-package && ./deploy-offline.sh"