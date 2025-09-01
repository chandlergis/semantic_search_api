import logging
from fastapi import FastAPI
from app.routers import users, documents, search, projects, chat, compare
from app.db.base import Base, engine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/app.log')
    ]
)

app = FastAPI(root_path="/scdlsearch")

# 启动时创建数据库表
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(projects.router)
app.include_router(chat.router)
app.include_router(compare.router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
