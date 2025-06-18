from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
from jwt import PyJWTError
from uuid import uuid4

from app.core.config import settings
from app.db.base import get_db
from app.models.users import User

security = HTTPBearer()

# 固定测试token: sue143591#%
FIXED_TEST_TOKEN = "sue143591#%"

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前认证用户"""
    # 检查是否使用固定测试token
    if credentials.credentials == FIXED_TEST_TOKEN:
        # 查找或创建测试用户
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if not test_user:
            test_user = User(
                id=str(uuid4()),
                email="test@example.com",
                username="testuser",
                password_hash="dummy_hash"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
        return test_user
    
    # 正常JWT token验证
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user