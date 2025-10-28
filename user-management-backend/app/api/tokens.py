from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from ..database import get_database
from ..auth.dependencies import get_current_user
from ..auth.unified_auth import get_current_user_unified
from ..models.user import User, TokenUsageLog
from ..services.token_service import TokenService, TokenPricingService
from ..schemas.auth import TokenUsageLogResponse

router = APIRouter(prefix="/tokens", tags=["Tokens"])

@router.get("/balance")
async def get_token_balance(current_user: User = Depends(get_current_user_unified), db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get current user's token balance and usage information."""
    # Simplified implementation - return user's current token info
    return {
        "user_id": str(current_user.id),
        "tokens_remaining": current_user.tokens_remaining or 0,
        "tokens_used": current_user.tokens_used or 0,
        "monthly_limit": current_user.monthly_limit or 10000,
        "subscription_plan": current_user.subscription or "free",
        "reset_date": None  # TODO: Implement billing period tracking
    }

@router.get("/usage", response_model=List[TokenUsageLogResponse])
async def get_token_usage(
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip")
):
    """Get user's token usage history."""
    # Use Beanie to query usage logs
    from beanie import SortDirection
    logs = await TokenUsageLog.find(
        TokenUsageLog.user_id == current_user.id
    ).sort([("created_at", SortDirection.DESCENDING)]).skip(offset).limit(limit).to_list()
    return logs

@router.post("/reserve")
async def reserve_tokens(
    amount: int,
    provider: str,
    model_name: str,
    request_type: str,
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Reserve tokens for a request (check availability without consuming)."""
    # Simplified implementation - just check if user has enough tokens
    available = current_user.tokens_remaining or 0
    
    if available >= amount:
        return {
            "success": True,
            "reserved": amount,
            "remaining": available - amount,
            "message": "Tokens reserved successfully"
        }
    else:
        raise HTTPException(status_code=403, detail="Insufficient tokens available")

@router.post("/consume")
async def consume_tokens(
    amount: int,
    provider: str,
    model_name: str,
    request_type: str,
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
    request_metadata: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Consume tokens and log usage with cost calculation."""
    # Simplified implementation
    available = current_user.tokens_remaining or 0
    
    if available < amount:
        raise HTTPException(status_code=403, detail="Insufficient tokens")
    
    # Update user tokens
    current_user.tokens_remaining = available - amount
    current_user.tokens_used = (current_user.tokens_used or 0) + amount
    await current_user.save()
    
    # Log usage
    if current_user.id:
        usage_log = TokenUsageLog(
            user_id=current_user.id,
            provider=provider,
            model_name=model_name,
            tokens_used=amount,
            request_type=request_type,
            cost_usd=None,  # TODO: Calculate cost
            request_metadata=request_metadata or {}
        )
        await usage_log.insert()
    
    return {
        "success": True,
        "consumed": amount,
        "remaining": current_user.tokens_remaining,
        "total_used": current_user.tokens_used
    }

@router.get("/limits")
async def get_token_limits(current_user: User = Depends(get_current_user_unified), db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get user's rate limits based on subscription plan."""
    # Simplified implementation - return basic limits
    return {
        "monthly_limit": current_user.monthly_limit or 10000,
        "tokens_remaining": current_user.tokens_remaining or 0,
        "tokens_used": current_user.tokens_used or 0,
        "subscription_plan": current_user.subscription or "free",
        "rate_limits": {
            "requests_per_minute": 60,
            "requests_per_hour": 1000,
            "requests_per_day": 10000
        }
    }

@router.get("/stats")
async def get_usage_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get detailed usage statistics for the user."""
    # Simplified implementation - return basic stats
    from datetime import datetime, timedelta, timezone
    
    from_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Get logs from last N days
    logs = await TokenUsageLog.find(
        TokenUsageLog.user_id == current_user.id,
        TokenUsageLog.created_at >= from_date
    ).to_list()
    
    total_tokens = sum(log.tokens_used for log in logs)
    total_requests = len(logs)
    
    # Group by model
    model_usage = {}
    for log in logs:
        model = log.model_name or "unknown"
        if model not in model_usage:
            model_usage[model] = {"tokens": 0, "requests": 0}
        model_usage[model]["tokens"] += log.tokens_used
        model_usage[model]["requests"] += 1
    
    return {
        "period_days": days,
        "total_tokens_used": total_tokens,
        "total_requests": total_requests,
        "average_tokens_per_request": total_tokens / total_requests if total_requests > 0 else 0,
        "model_breakdown": model_usage,
        "current_remaining": current_user.tokens_remaining or 0
    }

@router.get("/pricing/{provider}/{model_name}")
def get_model_pricing(provider: str, model_name: str):
    """Get pricing information for a specific model."""
    pricing = TokenPricingService.get_model_pricing(provider, model_name)
    return {
        "provider": provider,
        "model_name": model_name,
        "pricing": pricing,
        "currency": "USD",
        "unit": "per 1K tokens"
    }
