from app.db.base import Base, engine
from app.models.users import User

def create_tables():
    """创建所有数据库表"""
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成!")

if __name__ == "__main__":
    create_tables()