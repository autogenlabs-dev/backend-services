from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..database import get_db
from ..auth.dependencies import get_current_user
from ..auth.unified_auth import get_current_user_unified
from ..models.user import User, TokenUsageLog
from ..services.token_service import TokenService, TokenPricingService
from ..schemas.auth import TokenUsageLogResponse

router = APIRouter(prefix="/tokens", tags=["Tokens"])

@router.get("/balance")
def get_token_balance(current_user: User = Depends(get_current_user_unified), db: Session = Depends(get_db)):
    """Get current user's token balance and usage information."""
    token_service = TokenService(db)
    return token_service.get_token_balance(current_user)

@router.get("/usage", response_model=List[TokenUsageLogResponse])
def get_token_usage(
    current_user: User = Depends(get_current_user_unified), 
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip")
):
    """Get user's token usage history."""
    logs = (
        db.query(TokenUsageLog)
        .filter(TokenUsageLog.user_id == current_user.id)
        .order_by(TokenUsageLog.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return logs

@router.post("/reserve")
def reserve_tokens(
    amount: int,
    provider: str,
    model_name: str,
    request_type: str,
    current_user: User = Depends(get_current_user_unified),
    db: Session = Depends(get_db)
):
    """Reserve tokens for a request (check availability without consuming)."""
    token_service = TokenService(db)
    return token_service.reserve_tokens(current_user, amount, provider, model_name, request_type)

@router.post("/consume")
def consume_tokens(
    amount: int,
    provider: str,
    model_name: str,
    request_type: str,
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
    request_metadata: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user_unified),
    db: Session = Depends(get_db)
):
    """Consume tokens and log usage with cost calculation."""
    token_service = TokenService(db)
    
    # Calculate cost if token breakdown is provided
    cost_usd = None
    if input_tokens is not None and output_tokens is not None:
        cost_usd = TokenPricingService.calculate_cost(
            provider, model_name, input_tokens, output_tokens
        )
    
    return token_service.consume_tokens(
        current_user, amount, provider, model_name, request_type, cost_usd, request_metadata
    )

@router.get("/limits")
def get_token_limits(current_user: User = Depends(get_current_user_unified), db: Session = Depends(get_db)):
    """Get user's rate limits based on subscription plan."""
    token_service = TokenService(db)
    return token_service.get_rate_limits(current_user)

@router.get("/stats")
def get_usage_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user_unified),
    db: Session = Depends(get_db)
):
    """Get detailed usage statistics for the user."""
    token_service = TokenService(db)
    return token_service.get_usage_stats(current_user, days)

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
