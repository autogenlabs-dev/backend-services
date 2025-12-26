"""
Chat Completions Proxy for GLM Models
Provides secure server-side proxy to Z.AI while validating subscription tiers
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional
import httpx
from ..auth.unified_auth import get_current_user_unified
from ..models.user import User

router = APIRouter(prefix="/chat", tags=["Chat Proxy"])

# Z.AI Configuration (GLM models)
ZAI_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"

import time
import jwt

def generate_zai_token(apikey: str, exp_seconds: int = 3600) -> str:
    """
    Generate signed JWT for Z.AI API from the raw API key (id.secret).
    """
    try:
        id, secret = apikey.split(".")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Invalid GLM API Key format")

    payload = {
        "api_key": id,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }

    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )


async def get_user_glm_key(user: User) -> Optional[str]:
    """
    Get user's assigned GLM API key.
    
    Priority:
    1. User's personal glm_api_key field (if set)
    2. Assigned key from ApiKeyPool (most common)
    """
    # Check if user has personal key
    if user.glm_api_key:
        return user.glm_api_key
    
    # Try to get from pool assignment
    from ..models.api_key_pool import ApiKeyPool
    
    assigned_keys = await ApiKeyPool.find({
        "key_type": "glm",
        "is_active": True,
        "assigned_user_ids": user.id
    }).to_list()
    
    if assigned_keys:
        return assigned_keys[0].key_value
    
    return None


@router.post("/completions")
async def chat_completions_proxy(
    request: Request,
    current_user: User = Depends(get_current_user_unified)
):
    """
    Secure proxy for chat completions with tier validation.
    
    - Validates subscription tier for GLM models
    - Fetches user's assigned GLM key from pool
    - Streams responses from Z.AI
    - Returns subscription info in response headers
    - Enables Z.AI context caching automatically
    """
    try:
        # Parse request body
        body = await request.json()
        model_id = body.get("model")
        
        # CODEMURF: Map frontend model IDs to Z.AI model IDs
        model_mapping = {
            "glm-4.7": "glm-4-plus",
            "glm-4.6": "glm-4-0520",
            "glm-4.5": "glm-4",
            "glm-4": "glm-4",
            "glm-4-air": "glm-4-air",
            "glm-4-flash": "glm-4-flash"
        }
        
        # Use mapped ID or fallback to original
        actual_model_id = model_mapping.get(model_id, model_id)
        body["model"] = actual_model_id
        
        print(f"Proxying request for model: {model_id} -> {actual_model_id}") # Debug log
        
        # Validate GLM model access
        if model_id.startswith("glm-"):
            # Check if user has Pro/Ultra subscription (check both fields for compatibility)
            tier = current_user.subscription_plan or str(current_user.subscription).lower()
            
            if tier not in ["pro", "ultra"]:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "GLM models require Pro or Ultra subscription",
                        "subscription_tier": tier,
                        "model": model_id
                    }
                )
            
            # Get user's assigned GLM key from pool
            glm_key = await get_user_glm_key(current_user)
            if not glm_key:
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "No GLM API key assigned. Please contact support.",
                        "subscription_tier": tier
                    }
                )
        
        # Prepare headers for Z.AI
        # Generate JWT from the raw key
        zai_token = generate_zai_token(glm_key)
        headers = {
            "Authorization": f"Bearer {zai_token}",
            "Content-Type": "application/json"
        }
        

        
        # Create streaming response
        async def stream_response():
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{ZAI_BASE_URL}/chat/completions",
                    headers=headers,
                    json=body,
                    timeout=120.0  # 2 minute timeout for LLM responses
                ) as response:
                    # Check for errors
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_msg = error_text.decode()
                        print(f"Z.AI API Error ({response.status_code}): {error_msg}")
                        # Yield error as a JSON chunk so client sees it
                        import json
                        error_json = json.dumps({"error": {"message": f"Z.AI Error: {error_msg}", "code": response.status_code}})
                        yield f"data: {error_json}\n\n".encode('utf-8')
                        return

                    # Stream chunks back to client
                    async for chunk in response.aiter_bytes():
                        yield chunk
        
        # Get user subscription info for headers
        tier = current_user.subscription_plan or str(current_user.subscription).lower()
        expires = current_user.subscription_end_date.isoformat() if current_user.subscription_end_date else None
        
        # Return streaming response with subscription headers
        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream",
            headers={
                "X-Subscription-Tier": tier,
                "X-Subscription-Valid": "true",
                "X-Subscription-Expires": expires or "never",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Proxy error: {str(e)}"
        )


@router.get("/status")
async def chat_proxy_status(current_user: User = Depends(get_current_user_unified)):
    """
    Check chat proxy status and user's subscription tier.
    Also shows if user has a GLM key assigned.
    """
    tier = current_user.subscription_plan or str(current_user.subscription).lower()
    
    # Check if user has GLM key assigned
    glm_key = await get_user_glm_key(current_user)
    
    return {
        "status": "ok",
        "user_tier": tier,
        "glm_access": tier in ["pro", "ultra"],
        "glm_key_assigned": bool(glm_key)
    }
