# 离线部署指南

## 1. 在有网络的环境中准备镜像

### 构建自定义镜像
```bash
# 构建后端镜像
docker build -t semantic-search-backend:offline .

# 构建前端镜像  
cd frontend
docker build -t semantic-search-frontend:offline .
cd ..
```

### 拉取基础镜像
```bash
# PostgreSQL
docker pull postgres:13

# Redis
docker pull redis:7-alpine
```

## 2. 导出镜像为tar文件

```bash
# 导出基础镜像
docker save -o postgres-13.tar postgres:13
docker save -o redis-7-alpine.tar redis:7-alpine

# 导出自定义镜像
docker save -o semantic-search-backend-offline.tar semantic-search-backend:offline
docker save -o semantic-search-frontend-offline.tar semantic-search-frontend:offline
```

## 3. 传输文件到离线环境

将以下文件复制到离线环境：
- `postgres-13.tar`
- `redis-7-alpine.tar` 
- `semantic-search-backend-offline.tar`
- `semantic-search-frontend-offline.tar`
- `docker-compose-offline.yml`
- 整个项目代码目录（包含app/, frontend/, requirements.txt等）

## 4. 在离线环境中导入镜像

```bash
# 导入基础镜像
docker load -i postgres-13.tar
docker load -i redis-7-alpine.tar

# 导入自定义镜像
docker load -i semantic-search-backend-offline.tar
docker load -i semantic-search-frontend-offline.tar
```

## 5. 启动服务

```bash
# 使用离线compose文件启动
docker-compose -f docker-compose-offline.yml up -d
```

## 6. 验证部署

```bash
# 检查服务状态
docker-compose -f docker-compose-offline.yml ps

# 查看日志
docker-compose -f docker-compose-offline.yml logs backend
docker-compose -f docker-compose-offline.yml logs frontend

# 访问应用
curl http://localhost:9000/health
```

## 7. 需要的依赖包

### 系统依赖（已在Dockerfile中包含）
- libpango-1.0-0
- libharfbuzz0b  
- libpangoft2-1.0-0
- fonts-dejavu
- gcc
- postgresql-client

### Python依赖（已在requirements.txt中包含）
- fastapi==0.95.2
- uvicorn==0.22.0
- python-multipart==0.0.6
- sqlalchemy==2.0.15
- psycopg2-binary==2.9.6
- pydantic[email]==1.10.7
- python-dotenv==1.0.0
- nltk==3.8.1
- email-validator==2.0.0
- PyJWT==2.8.0
- passlib[bcrypt]==1.7.4
- aiofiles==23.1.0
- httpx==0.24.1
- markitdown[all]
- scikit-learn==1.3.0
- numpy<2.0.0
- rank-bm25==0.2.2
- redis==4.5.0
- PyMuPDF==1.23.26
- python-docx==1.1.0
- weasyprint==60.0
- fpdf2==2.7.6

## 8. 注意事项

1. **数据库数据持久化**：确保`postgres_data`和`redis_data`卷正确挂载
2. **文件上传目录**：`uploads`卷用于存储上传的文件
3. **临时文件目录**：`temp_files`卷用于存储临时转换的文件
4. **网络配置**：所有服务在`app-network`网络内通信
5. **健康检查**：服务启动后有健康检查确保依赖服务就绪

## 9. 故障排除

如果遇到问题，检查：
- 镜像是否正确导入（`docker images`）
- 容器日志（`docker-compose logs`）
- 网络连通性（容器间ping测试）
- 卷权限（确保挂载目录有写权限）