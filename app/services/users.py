from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from uuid import uuid4

from app.models.users import User
from app.schemas.users import UserCreate, UserInDB
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def create_user(self, db: Session, user: UserCreate) -> UserInDB:
        # 检查邮箱是否已存在
        if self.get_user_by_email(db, user.email):
            raise ValueError("Email already registered")
        
        # 创建新用户
        hashed_password = pwd_context.hash(user.password)
        db_user = User(
            id=str(uuid4()),
            email=user.email,
            username=user.username,
            password_hash=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return UserInDB.from_orm(db_user)

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(db, email)
        if not user or not pwd_context.verify(password, user.password_hash):
            return None
        return user

    def create_access_token(self, user_id: str) -> str:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": user_id,
            "exp": expire
        }
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

user_service = UserService()
