from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from typing import Optional
import openai
from app.core.config import settings
from app.routers.auth import get_current_user
from app.models.users import User

router = APIRouter()
security = HTTPBearer()

# Configure OpenAI API
openai.api_key = settings.OPENAI_API_KEY

@router.get("/models")
async def get_models():
    """
    Endpoint to list available chat models.
    Returns: { "object": "list", "data": [ { "id": "model-id", "object": "model", "owned_by": "owner" } ] }
    """
    return {
        "object": "list",
        "data": [
            {"id": "gpt-3.5-turbo", "object": "model", "owned_by": "openai"},
            {"id": "gpt-4", "object": "model", "owned_by": "openai"}
        ]
    }

@router.post("/chat")
async def chat_with_ai(
    message: dict,
    current_user: User = Depends(get_current_user)
):
    """
    固定返回“功能正在开发中呢？”
    """
    return {"response": "功能正在开发中呢！"}