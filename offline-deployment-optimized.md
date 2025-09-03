# 离线环境部署指南 (优化版)

## 1. 镜像导出和传输

### 在联网环境中导出镜像
```bash
# 使用优化的准备脚本
chmod +x prepare-offline-optimized.sh
./prepare-offline-optimized.sh
```

### 需要传输的文件
将以下文件拷贝到离线环境：
- `offline-package/` 目录下的所有文件

## 2. 离线环境部署

### 在离线环境中导入镜像
```bash
# 进入离线包目录
cd offline-package

# 导入镜像
./deploy-offline.sh
```

### 手动导入镜像（如果需要）
```bash
# 如果自动脚本不工作，可以手动导入
docker load -i postgres-13.tar
docker load -i redis-7-alpine.tar
docker load -i semantic-search-backend-offline.tar
docker load -i semantic-search-frontend-offline.tar

# 验证镜像已导入
docker images | grep -E "(postgres|redis|semantic)"
```

### 启动服务
```bash
# 使用离线版docker-compose文件启动服务
docker-compose -f docker-compose-offline.yml up -d

# 查看服务状态
docker-compose -f docker-compose-offline.yml ps

# 查看日志
docker-compose -f docker-compose-offline.yml logs -f
```

## 3. 访问应用

启动成功后，可以通过以下地址访问：
- **主页面**: http://localhost:30082/scdlsearch/
- **API文档**: http://localhost:9001/docs

## 4. 常用管理命令

```bash
# 停止服务
docker-compose -f docker-compose-offline.yml down

# 重启服务
docker-compose -f docker-compose-offline.yml restart

# 查看特定服务日志
docker-compose -f docker-compose-offline.yml logs backend
docker-compose -f docker-compose-offline.yml logs frontend
docker-compose -f docker-compose-offline.yml logs db

# 进入容器调试
docker-compose -f docker-compose-offline.yml exec backend bash
docker-compose -f docker-compose-offline.yml exec frontend sh
```

## 5. 数据持久化

数据库数据存储在Docker volume中：
- Volume名称: `semantic_search_api_postgres_data`
- Redis数据存储: `semantic_search_api_redis_data`
- 上传文件存储在: `./uploads/` 目录
- 临时文件存储在: `./temp_files/` 目录

### 备份数据库
```bash
# 导出数据库
docker-compose -f docker-compose-offline.yml exec db pg_dump -U postgres semantic_search > backup.sql

# 恢复数据库
docker-compose -f docker-compose-offline.yml exec -T db psql -U postgres semantic_search < backup.sql
```

## 6. 故障排除

### 常见问题
1. **端口冲突**: 使用了不同的端口 (db: 5433, redis: 6380, backend: 9001, frontend: 30082)
2. **磁盘空间**: 确保有足够的磁盘空间存储镜像和数据
3. **权限问题**: 确保Docker有权限访问挂载目录

### 检查服务健康状态
```bash
# 检查所有服务是否健康
docker-compose -f docker-compose-offline.yml exec backend curl -f http://localhost:8500/health

# 检查数据库连接
docker-compose -f docker-compose-offline.yml exec db pg_isready -U postgres
```

## 7. 安全注意事项

在生产环境中，请确保：
- 修改默认密码（POSTGRES_PASSWORD）
- 设置强密钥（SECRET_KEY）
- 配置防火墙规则
- 定期备份数据

## 8. 端口映射详情

| 服务 | 容器端口 | 主机端口 | 说明 |
|------|----------|----------|------|
| PostgreSQL | 5432 | 5433 | 数据库服务 |
| Redis | 6379 | 6380 | 缓存服务 |
| Backend | 8500 | 9001 | API服务 |
| Frontend | 80 | 30082 | Web界面 |

## 9. 环境变量配置

后端服务配置：
- `DATABASE_URL`: postgresql://postgres:postgres@db:5432/semantic_search
- `REDIS_URL`: redis://redis:6379/0
- `ENVIRONMENT`: production

前端服务配置：
- `VITE_API_BASE_URL`: http://localhost:9001

## 10. 清理和卸载

如果需要完全卸载系统，可以使用清理脚本：
```bash
# 在offline-package目录中运行
./cleanup.sh
```