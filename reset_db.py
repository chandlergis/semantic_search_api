from app.db.base import Base, engine
from app.models.users import User
from app.models.documents import Document, Chunk
from app.models.projects import Project, ProjectDocument

def reset_database():
    """删除并重新创建所有表"""
    try:
        # 删除所有表
        Base.metadata.drop_all(bind=engine)
        print("所有表已删除")
        
        # 重新创建所有表
        Base.metadata.create_all(bind=engine)
        print("所有表已重新创建")
        
        # 显示创建的表
        print("创建的表:")
        print("- users")
        print("- projects")
        print("- documents") 
        print("- chunks")
        print("- project_documents")
        
    except Exception as e:
        print(f"重置数据库时出错: {e}")

if __name__ == "__main__":
    reset_database()