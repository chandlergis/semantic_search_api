# 离线环境部署指南

## 1. 镜像导出和传输

### 在联网环境中导出镜像
```bash
# 导出所有必需的镜像
docker save -o semantic_search_images.tar \
  postgres:13 \
  semantic_search_api-frontend \
  semantic_search_api-backend

# 压缩镜像文件（可选，节省传输空间）
gzip semantic_search_images.tar
```

### 需要传输的文件
将以下文件拷贝到离线环境：
- `semantic_search_images.tar` (或 `semantic_search_images.tar.gz`)
- `docker-compose-offline.yml`
- `uploads/` 目录（如果有历史数据）

## 2. 离线环境部署

### 在离线环境中导入镜像
```bash
# 如果压缩了，先解压
gunzip semantic_search_images.tar.gz

# 导入镜像
docker load -i semantic_search_images.tar

# 验证镜像已导入
docker images | grep -E "(postgres|semantic_search_api)"
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
- **主页面**: http://localhost:30080/scdlsearch/
- **API文档**: http://localhost:30080/scdlsearch/docs

## 4. 常用管理命令

```bash
# 停止服务
docker-compose -f docker-compose-offline.yml down

# 重启服务
docker-compose -f docker-compose-offline.yml restart

# 查看特定服务日志
docker-compose -f docker-compose-offline.yml logs frontend
docker-compose -f docker-compose-offline.yml logs backend
docker-compose -f docker-compose-offline.yml logs db

# 进入容器调试
docker-compose -f docker-compose-offline.yml exec backend bash
docker-compose -f docker-compose-offline.yml exec frontend sh
```

## 5. 数据持久化

数据库数据存储在Docker volume中：
- Volume名称: `postgres_data`
- 上传文件存储在: `./uploads/` 目录

### 备份数据库
```bash
# 导出数据库
docker-compose -f docker-compose-offline.yml exec db pg_dump -U postgres semantic_search > backup.sql

# 恢复数据库
docker-compose -f docker-compose-offline.yml exec -T db psql -U postgres semantic_search < backup.sql
```

## 6. 故障排除

### 常见问题
1. **端口冲突**: 确保30080、8500、5432端口没有被占用
2. **磁盘空间**: 确保有足够的磁盘空间存储镜像和数据
3. **权限问题**: 确保Docker有权限访问挂载目录

### 检查服务健康状态
```bash
# 检查所有服务是否健康
docker-compose -f docker-compose-offline.yml exec backend curl -f http://localhost:8500/scdlsearch/health

# 检查数据库连接
docker-compose -f docker-compose-offline.yml exec db pg_isready -U postgres
```

## 7. 安全注意事项

在生产环境中，请确保：
- 修改默认密码（POSTGRES_PASSWORD）
- 设置强密钥（SECRET_KEY）
- 配置防火墙规则
- 定期备份数据