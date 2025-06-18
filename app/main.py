import logging
from fastapi import FastAPI
from app.routers import users, documents, search, projects
from app.db.base import Base, engine

# 配置日志
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# 启动时创建数据库表
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(projects.router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
