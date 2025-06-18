from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.users import UserCreate, UserInDB, Token, UserLogin
from app.services.users import user_service
from app.db.base import get_db

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/register", response_model=UserInDB)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return user_service.create_user(db, user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = user_service.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = user_service.create_access_token(user.id)
    return Token(access_token=access_token)
