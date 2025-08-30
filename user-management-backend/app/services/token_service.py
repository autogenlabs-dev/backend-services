"""Token management service with real business logic."""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.user import User, TokenUsageLog, SubscriptionPlan, UserSubscription


class TokenService:
    """Service for managing user token balances and consumption."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_subscription_plan(self, user: User) -> SubscriptionPlan:
        """Get user's current subscription plan, defaulting to free."""
        subscription = (
            self.db.query(UserSubscription)
            .filter(UserSubscription.user_id == user.id)
            .filter(UserSubscription.status == "active")
            .first()
        )
        
        if subscription:
            return subscription.plan
        
        # Return free plan as default
        free_plan = (
            self.db.query(SubscriptionPlan)
            .filter(SubscriptionPlan.name == "free")
            .first()
        )
        
        if not free_plan:
            # Create default free plan if it doesn't exist
            free_plan = SubscriptionPlan(
                name="free",
                display_name="Free Plan",
                monthly_tokens=10000,
                price_monthly=Decimal("0.00"),
                features={"models": ["basic"], "support": "community"},
                is_active=True
            )
            self.db.add(free_plan)
            self.db.commit()
            self.db.refresh(free_plan)
        
        return free_plan
    
    def get_current_period_dates(self, user: User) -> Tuple[datetime, datetime]:
        """Get the current billing period start and end dates."""
        subscription = (
            self.db.query(UserSubscription)
            .filter(UserSubscription.user_id == user.id)
            .filter(UserSubscription.status == "active")
            .first()
        )
        
        if subscription and subscription.current_period_start and subscription.current_period_end:
            return subscription.current_period_start, subscription.current_period_end
        
        # For free users or users without active subscription, use monthly periods
        now = datetime.now(timezone.utc)
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate next month
        if period_start.month == 12:
            period_end = period_start.replace(year=period_start.year + 1, month=1)
        else:
            period_end = period_start.replace(month=period_start.month + 1)
        
        return period_start, period_end
    
    def get_tokens_used_this_period(self, user: User) -> int:
        """Get total tokens used in the current billing period."""
        period_start, period_end = self.get_current_period_dates(user)
        
        result = (
            self.db.query(func.sum(TokenUsageLog.tokens_used))
            .filter(TokenUsageLog.user_id == user.id)
            .filter(TokenUsageLog.created_at >= period_start)
            .filter(TokenUsageLog.created_at < period_end)
            .scalar()
        )
        
        return result or 0
    
    def get_token_balance(self, user: User) -> Dict[str, Any]:
        """Get user's current token balance and limits."""
        plan = self.get_user_subscription_plan(user)
        tokens_used = self.get_tokens_used_this_period(user)
        tokens_remaining = max(0, plan.monthly_tokens - tokens_used)
        
        period_start, period_end = self.get_current_period_dates(user)
        
        return {
            "tokens_remaining": tokens_remaining,
            "tokens_used": tokens_used,
            "monthly_limit": plan.monthly_tokens,
            "plan_name": plan.name,
            "plan_display_name": plan.display_name,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "usage_percentage": round((tokens_used / plan.monthly_tokens) * 100, 2) if plan.monthly_tokens > 0 else 0
        }
    
    def check_token_availability(self, user: User, tokens_requested: int) -> Tuple[bool, str]:
        """Check if user has enough tokens available."""
        balance = self.get_token_balance(user)
        
        if balance["tokens_remaining"] < tokens_requested:
            return False, f"Insufficient tokens. Requested: {tokens_requested}, Available: {balance['tokens_remaining']}"
        
        return True, "OK"
    
    def reserve_tokens(self, user: User, amount: int, provider: str, model_name: str, request_type: str) -> Dict[str, Any]:
        """Reserve tokens for a request (check availability)."""
        available, message = self.check_token_availability(user, amount)
        
        if not available:
            return {
                "success": False,
                "message": message,
                "tokens_reserved": 0
            }
        
        return {
            "success": True,
            "message": "Tokens reserved successfully",
            "tokens_reserved": amount,
            "provider": provider,
            "model_name": model_name,
            "request_type": request_type
        }
    
    def consume_tokens(
        self, 
        user: User, 
        tokens: int, 
        model_name: str = "default",
        request_metadata: Dict[str, Any] = None,
        api_key_id: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Consume tokens for a user request with sub-user support
        """
        if tokens <= 0:
            return False, {"error": "Invalid token amount"}
        
        # Handle sub-user token consumption
        if user.is_sub_user and user.parent_user_id:
            return self._consume_sub_user_tokens(user, tokens, model_name, request_metadata, api_key_id)
        
        # Regular user token consumption
        return self._consume_regular_user_tokens(user, tokens, model_name, request_metadata, api_key_id)
    
    def _consume_sub_user_tokens(
        self,
        sub_user: User,
        tokens: int,
        model_name: str,
        request_metadata: Dict[str, Any] = None,
        api_key_id: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Consume tokens for a sub-user"""
        
        # Get parent user for billing
        parent_user = self.db.query(User).filter(User.id == sub_user.parent_user_id).first()
        if not parent_user:
            return False, {"error": "Parent user not found"}
        
        # Check sub-user limits
        sub_user_limits = sub_user.sub_user_limits or {}
        monthly_limit = sub_user_limits.get("monthly_tokens", sub_user.monthly_limit)
        
        if sub_user.tokens_used + tokens > monthly_limit:
            return False, {
                "error": "Sub-user monthly token limit exceeded",
                "limit": monthly_limit,
                "used": sub_user.tokens_used,
                "requested": tokens
            }
        
        # Check parent user has enough tokens
        if parent_user.tokens_used + tokens > parent_user.monthly_limit:
            return False, {
                "error": "Parent user monthly token limit exceeded",
                "parent_limit": parent_user.monthly_limit,
                "parent_used": parent_user.tokens_used,
                "requested": tokens
            }
        
        # Consume tokens from both sub-user and parent user
        sub_user.tokens_used += tokens
        sub_user.tokens_remaining = max(0, monthly_limit - sub_user.tokens_used)
        
        parent_user.tokens_used += tokens
        parent_user.tokens_remaining = max(0, parent_user.monthly_limit - parent_user.tokens_used)
        
        # Log usage for both users
        self._log_token_usage(sub_user, tokens, model_name, request_metadata, api_key_id, is_sub_user=True)
        self._log_token_usage(parent_user, tokens, model_name, request_metadata, api_key_id, sub_user_id=str(sub_user.id))
        
        self.db.commit()
        
        return True, {
            "success": True,
            "tokens_consumed": tokens,
            "sub_user_remaining": sub_user.tokens_remaining,
            "parent_remaining": parent_user.tokens_remaining
        }
    
    def _consume_regular_user_tokens(
        self,
        user: User,
        tokens: int,
        model_name: str,
        request_metadata: Dict[str, Any] = None,
        api_key_id: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Consume tokens for a regular user"""
        
        if user.tokens_used + tokens > user.monthly_limit:
            return False, {
                "error": "Monthly token limit exceeded",
                "limit": user.monthly_limit,
                "used": user.tokens_used,
                "requested": tokens
            }
        
        # Consume tokens
        user.tokens_used += tokens
        user.tokens_remaining = max(0, user.monthly_limit - user.tokens_used)
        
        # Log usage
        self._log_token_usage(user, tokens, model_name, request_metadata, api_key_id)
        
        self.db.commit()
        
        return True, {
            "success": True,
            "tokens_consumed": tokens,
            "remaining": user.tokens_remaining
        }
    
    def _log_token_usage(
        self,
        user: User,
        tokens: int,
        model_name: str,
        request_metadata: Dict[str, Any] = None,
        api_key_id: Optional[str] = None,
        is_sub_user: bool = False,
        sub_user_id: Optional[str] = None
    ):
        """Log token usage for analytics and billing"""
        
        usage_log = TokenUsageLog(
            user_id=user.id,
            tokens_used=tokens,
            model_name=model_name,
            request_metadata=request_metadata or {},
            api_key_id=api_key_id,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Add sub-user context if applicable
        if is_sub_user or sub_user_id:
            usage_log.request_metadata = usage_log.request_metadata or {}
            usage_log.request_metadata.update({
                "is_sub_user_request": is_sub_user,
                "sub_user_id": sub_user_id,
                "billing_user_id": str(user.id)
            })
        
        self.db.add(usage_log)
    
    def get_sub_user_usage_summary(self, sub_user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get usage summary for a sub-user"""
        
        from_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get usage logs for sub-user
        usage_query = (
            self.db.query(TokenUsageLog)
            .filter(TokenUsageLog.user_id == sub_user_id)
            .filter(TokenUsageLog.timestamp >= from_date)
        )
        
        usage_logs = usage_query.all()
        
        # Calculate statistics
        total_tokens = sum(log.tokens_used for log in usage_logs)
        total_requests = len(usage_logs)
        
        # Group by model
        model_usage = {}
        for log in usage_logs:
            model = log.model_name or "unknown"
            if model not in model_usage:
                model_usage[model] = {"tokens": 0, "requests": 0}
            model_usage[model]["tokens"] += log.tokens_used
            model_usage[model]["requests"] += 1
        
        # Group by day
        daily_usage = {}
        for log in usage_logs:
            day = log.timestamp.date().isoformat()
            if day not in daily_usage:
                daily_usage[day] = {"tokens": 0, "requests": 0}
            daily_usage[day]["tokens"] += log.tokens_used
            daily_usage[day]["requests"] += 1
        
        return {
            "period_days": days,
            "total_tokens": total_tokens,
            "total_requests": total_requests,
            "average_tokens_per_request": total_tokens / total_requests if total_requests > 0 else 0,
            "model_breakdown": model_usage,
            "daily_usage": daily_usage,
            "last_activity": max((log.timestamp for log in usage_logs), default=None)
        }
    
    def get_rate_limits(self, user: User) -> Dict[str, int]:
        """Get rate limits based on user's subscription plan."""
        plan = self.get_user_subscription_plan(user)
        
        # Default rate limits
        rate_limits = {
            "per_minute": 60,
            "per_hour": 1000,
            "per_day": 10000
        }
        
        # Adjust based on plan features
        if plan.features:
            max_requests_per_minute = plan.features.get("max_requests_per_minute", 60)
            rate_limits.update({
                "per_minute": max_requests_per_minute,
                "per_hour": max_requests_per_minute * 60,
                "per_day": max_requests_per_minute * 60 * 24
            })
        
        # Plan-specific adjustments
        if plan.name == "free":
            rate_limits.update({
                "per_minute": 10,
                "per_hour": 300,
                "per_day": 1000
            })
        elif plan.name == "pro":
            rate_limits.update({
                "per_minute": 100,
                "per_hour": 3000,
                "per_day": 50000
            })
        elif plan.name == "enterprise":
            rate_limits.update({
                "per_minute": 500,
                "per_hour": 15000,
                "per_day": 200000
            })
        
        return rate_limits
    
    def get_usage_stats(self, user: User, days: int = 30) -> Dict[str, Any]:
        """Get detailed usage statistics for the user."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get usage logs for the period
        logs = (
            self.db.query(TokenUsageLog)
            .filter(TokenUsageLog.user_id == user.id)
            .filter(TokenUsageLog.created_at >= cutoff_date)
            .all()
        )
        
        if not logs:
            return {
                "total_tokens": 0,
                "total_cost": 0.0,
                "tokens_by_provider": {},
                "cost_by_provider": {},
                "tokens_by_model": {},
                "tokens_by_request_type": {},
                "daily_usage": []
            }
        
        # Aggregate data
        total_tokens = sum(log.tokens_used for log in logs)
        total_cost = sum(log.cost_usd or 0.0 for log in logs)
        
        # Group by provider
        tokens_by_provider = {}
        cost_by_provider = {}
        for log in logs:
            tokens_by_provider[log.provider] = tokens_by_provider.get(log.provider, 0) + log.tokens_used
            cost_by_provider[log.provider] = cost_by_provider.get(log.provider, 0.0) + (log.cost_usd or 0.0)
        
        # Group by model
        tokens_by_model = {}
        for log in logs:
            model_key = f"{log.provider}/{log.model_name}"
            tokens_by_model[model_key] = tokens_by_model.get(model_key, 0) + log.tokens_used
        
        # Group by request type
        tokens_by_request_type = {}
        for log in logs:
            tokens_by_request_type[log.request_type] = tokens_by_request_type.get(log.request_type, 0) + log.tokens_used
        
        # Daily usage for the last 30 days
        daily_usage = []
        for i in range(days):
            day = (datetime.now(timezone.utc) - timedelta(days=i)).date()
            day_logs = [log for log in logs if log.created_at.date() == day]
            daily_tokens = sum(log.tokens_used for log in day_logs)
            daily_cost = sum(log.cost_usd or 0.0 for log in day_logs)
            
            daily_usage.append({
                "date": day.isoformat(),
                "tokens": daily_tokens,
                "cost": daily_cost
            })
        
        daily_usage.reverse()  # Most recent first
        
        return {
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 4),
            "tokens_by_provider": tokens_by_provider,
            "cost_by_provider": {k: round(v, 4) for k, v in cost_by_provider.items()},
            "tokens_by_model": tokens_by_model,
            "tokens_by_request_type": tokens_by_request_type,
            "daily_usage": daily_usage
        }

    # New methods required by LLM proxy service
    def can_use_tokens(self, user: User, tokens_requested: int) -> bool:
        """Check if user can use the requested number of tokens."""
        available, _ = self.check_token_availability(user, tokens_requested)
        return available

    def get_available_tokens(self, user: User) -> int:
        """Get the number of available tokens for the user."""
        balance = self.get_token_balance(user)
        return balance["tokens_remaining"]

    def reserve_tokens(self, user: User, tokens: int, request_type: str, metadata: Dict[str, Any]) -> str:
        """Reserve tokens for a request and return reservation ID."""
        # For now, this is a simple implementation that just checks availability
        # In a production system, you might want to actually reserve tokens in a separate table
        available, message = self.check_token_availability(user, tokens)
        if not available:
            raise ValueError(f"Cannot reserve tokens: {message}")
        
        # Generate a simple reservation ID
        import uuid
        reservation_id = str(uuid.uuid4())
        
        # Store reservation info (in production, you'd store this in the database)
        if not hasattr(self, '_reservations'):
            self._reservations = {}
        
        self._reservations[reservation_id] = {
            "user_id": user.id,
            "tokens": tokens,
            "request_type": request_type,
            "metadata": metadata,
            "timestamp": datetime.now(timezone.utc)
        }
        
        return reservation_id

    def consume_reserved_tokens(self, reservation_id: str, actual_tokens: int, cost_usd: float, response_metadata: Dict[str, Any]):
        """Consume tokens that were previously reserved."""
        if not hasattr(self, '_reservations') or reservation_id not in self._reservations:
            raise ValueError(f"Reservation {reservation_id} not found")
        
        reservation = self._reservations[reservation_id]
        user = self.db.query(User).filter(User.id == reservation["user_id"]).first()
        
        if not user:
            raise ValueError("User not found for reservation")
        
        # Consume the actual tokens used
        success, result = self.consume_tokens(
            user=user,
            tokens=actual_tokens,
            model_name=reservation["metadata"].get("model", "unknown"),
            request_metadata={
                **reservation["metadata"],
                **response_metadata,
                "reservation_id": reservation_id,
                "cost_usd": cost_usd
            }
        )
        
        # Remove the reservation
        del self._reservations[reservation_id]
        
        if not success:
            raise ValueError(f"Failed to consume tokens: {result}")

    def release_reserved_tokens(self, reservation_id: str):
        """Release tokens that were reserved but not consumed (e.g., on error)."""
        if hasattr(self, '_reservations') and reservation_id in self._reservations:
            del self._reservations[reservation_id]


class TokenPricingService:
    """Service for calculating token costs based on provider and model."""
    
    # Token costs per 1K tokens (in USD)
    TOKEN_COSTS = {
        "openrouter": {
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        },
        "glama": {
            "llama-2-7b": {"input": 0.0002, "output": 0.0002},
            "llama-2-13b": {"input": 0.0004, "output": 0.0004},
            "llama-2-70b": {"input": 0.0008, "output": 0.0016},
        },
        "requesty": {
            "mistral-7b": {"input": 0.0002, "output": 0.0002},
            "mixtral-8x7b": {"input": 0.0006, "output": 0.0006},
        }
    }
    
    @classmethod
    def calculate_cost(
        cls, 
        provider: str, 
        model_name: str, 
        input_tokens: int = 0, 
        output_tokens: int = 0
    ) -> float:
        """Calculate cost for token usage."""
        provider_costs = cls.TOKEN_COSTS.get(provider.lower(), {})
        model_costs = provider_costs.get(model_name.lower(), {"input": 0.001, "output": 0.001})
        
        input_cost = (input_tokens / 1000) * model_costs["input"]
        output_cost = (output_tokens / 1000) * model_costs["output"]
        
        return round(input_cost + output_cost, 6)
    
    @classmethod
    def get_model_pricing(cls, provider: str, model_name: str) -> Dict[str, float]:
        """Get pricing information for a specific model."""
        provider_costs = cls.TOKEN_COSTS.get(provider.lower(), {})
        return provider_costs.get(model_name.lower(), {"input": 0.001, "output": 0.001})
