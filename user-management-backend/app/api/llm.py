"""LLM proxy API endpoints with real provider integration."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..database import get_database
from ..auth.dependencies import get_current_user
from ..auth.unified_auth import get_current_user_unified
from ..models.user import User
from ..services.llm_proxy_service import LLMProxyService


router = APIRouter(prefix="/llm", tags=["LLM Proxy"])


# Request/Response models
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0


class TextCompletionRequest(BaseModel):
    model: str
    prompt: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0


class EmbeddingsRequest(BaseModel):
    model: str
    input: str


# Global proxy service instance (will be initialized per request)
async def get_llm_proxy_service(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get LLM proxy service instance."""
    service = LLMProxyService(db)
    try:
        yield service
    finally:
        await service.close()


@router.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    current_user: User = Depends(get_current_user_unified),
    llm_service: LLMProxyService = Depends(get_llm_proxy_service)
):
    """Create a chat completion via proxy with token management."""
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        response = await llm_service.chat_completion(
            user=current_user,
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty
        )
        
        if "error" in response:
            raise HTTPException(status_code=400, detail=response["error"])
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {str(e)}")


@router.post("/completions")
async def text_completions(
    request: TextCompletionRequest,
    current_user: User = Depends(get_current_user_unified),
    llm_service: LLMProxyService = Depends(get_llm_proxy_service)
):
    """Create a text completion via proxy with token management."""
    try:
        response = await llm_service.text_completion(
            user=current_user,
            prompt=request.prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty
        )
        
        if "error" in response:
            raise HTTPException(status_code=400, detail=response["error"])
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text completion failed: {str(e)}")


@router.post("/embeddings")
async def embeddings(
    request: EmbeddingsRequest,
    current_user: User = Depends(get_current_user_unified),
    llm_service: LLMProxyService = Depends(get_llm_proxy_service)
):
    """Create embeddings via proxy with token management."""
    try:
        response = await llm_service.embeddings(
            user=current_user,
            input_text=request.input,
            model=request.model
        )
        
        if "error" in response:
            raise HTTPException(status_code=400, detail=response["error"])
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embeddings failed: {str(e)}")


@router.get("/models")
async def list_models(
    current_user: User = Depends(get_current_user_unified),
    llm_service: LLMProxyService = Depends(get_llm_proxy_service)
):
    """List available models from all providers."""
    try:
        response = await llm_service.list_all_models()
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.get("/providers")
async def list_providers(
    current_user: User = Depends(get_current_user_unified),
    llm_service: LLMProxyService = Depends(get_llm_proxy_service)
):
    """List available LLM providers and their status."""
    try:
        response = llm_service.get_provider_status()
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get provider status: {str(e)}")


@router.get("/health")
async def health_check(
    current_user: User = Depends(get_current_user_unified),
    llm_service: LLMProxyService = Depends(get_llm_proxy_service)
):
    """Health check for LLM proxy service."""
    try:
        status = llm_service.get_provider_status()
        return {
            "status": "healthy",
            "user_id": str(current_user.id),
            "providers": status["providers"],
            "timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
