from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/semantic_search"
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 文档处理服务配置
    DOCUMENT_PARSER_URL: str = "http://localhost:8490"
    UPLOAD_DIR: str = "/app/uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # OpenAI API配置
    OPENAI_API_KEY: str = "your-openai-api-key-here"
    
    class Config:
        env_file = ".env"

settings = Settings()
