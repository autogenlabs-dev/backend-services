"""Subscription management service with real business logic."""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from decimal import Decimal
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.user import User, SubscriptionPlanModel, UserSubscription


class SubscriptionService:
    """Service for managing user subscriptions and plan enforcement."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_all_plans(self) -> List[SubscriptionPlanModel]:
        """Get all active subscription plans."""
        return await SubscriptionPlanModel.find(
            SubscriptionPlanModel.is_active == True
        ).sort("+price_monthly").to_list()
    
    async def get_plan_by_name(self, plan_name: str) -> Optional[SubscriptionPlanModel]:
        """Get a subscription plan by name."""
        return await SubscriptionPlanModel.find_one(
            SubscriptionPlanModel.name == plan_name,
            SubscriptionPlanModel.is_active == True
        )
    
    async def get_user_subscription(self, user: User) -> Optional[UserSubscription]:
        """Get user's current active subscription."""
        return await UserSubscription.find_one(
            UserSubscription.user_id == user.id,
            UserSubscription.status == "active"
        )
    
    async def get_user_plan(self, user: User) -> SubscriptionPlanModel:
        """Get user's current plan, defaulting to free."""
        subscription = await self.get_user_subscription(user)
        if subscription:
            # Need to fetch the plan details as UserSubscription only stores plan_id
            plan = await SubscriptionPlanModel.get(subscription.plan_id)
            if plan:
                return plan
        
        # Return free plan as default
        free_plan = await self.get_plan_by_name("free")
        if not free_plan:
            # Create default free plan if it doesn't exist
            free_plan = await self._create_default_free_plan()
        
        return free_plan
    
    async def _create_default_free_plan(self) -> SubscriptionPlanModel:
        """Create a default free plan."""
        free_plan = SubscriptionPlanModel(
            name="free",
            display_name="Free Plan",
            monthly_tokens=10000,
            price_monthly=Decimal("0.00"),
            features={
                "models": ["basic"],
                "support": "community",
                "api_access": False,
                "max_requests_per_minute": 10
            },
            is_active=True
        )
        await free_plan.insert()
        return free_plan
    
    async def subscribe_user_to_plan(self, user: User, plan_name: str, stripe_subscription_id: Optional[str] = None) -> UserSubscription:
        """Subscribe user to a new plan."""
        plan = await self.get_plan_by_name(plan_name)
        if not plan:
            raise ValueError(f"Plan '{plan_name}' not found")
        
        # Deactivate existing subscription
        existing_subscription = await self.get_user_subscription(user)
        if existing_subscription:
            existing_subscription.status = "cancelled"
            await existing_subscription.save()
        
        # Calculate billing period
        now = datetime.now(timezone.utc)
        period_start = now
        period_end = now + timedelta(days=30)  # Default 30-day billing cycle
        
        # Create new subscription
        new_subscription = UserSubscription(
            user_id=user.id,
            plan_id=plan.id,
            stripe_subscription_id=stripe_subscription_id,
            status="active",
            current_period_start=period_start,
            current_period_end=period_end
        )
        
        await new_subscription.insert()
        return new_subscription
    
    async def upgrade_user_subscription(self, user: User, new_plan_name: str) -> UserSubscription:
        """Upgrade user's subscription to a higher plan."""
        new_plan = await self.get_plan_by_name(new_plan_name)
        if not new_plan:
            raise ValueError(f"Plan '{new_plan_name}' not found")
        
        current_subscription = await self.get_user_subscription(user)
        current_plan = await self.get_user_plan(user)
        
        # Validate upgrade (new plan should be more expensive)
        if new_plan.price_monthly <= current_plan.price_monthly:
            raise ValueError("New plan must be a higher tier")
        
        if current_subscription:
            # Update existing subscription
            current_subscription.plan_id = new_plan.id
            current_subscription.status = "active"
            # Keep the same billing period for simplicity
            await current_subscription.save()
            return current_subscription
        else:
            # Create new subscription
            return await self.subscribe_user_to_plan(user, new_plan_name)
    
    async def downgrade_user_subscription(self, user: User, new_plan_name: str) -> UserSubscription:
        """Downgrade user's subscription to a lower plan."""
        new_plan = await self.get_plan_by_name(new_plan_name)
        if not new_plan:
            raise ValueError(f"Plan '{new_plan_name}' not found")
        
        current_subscription = await self.get_user_subscription(user)
        current_plan = await self.get_user_plan(user)
        
        # Validate downgrade (new plan should be less expensive)
        if new_plan.price_monthly >= current_plan.price_monthly:
            raise ValueError("New plan must be a lower tier")
        
        if current_subscription:
            # Update existing subscription
            current_subscription.plan_id = new_plan.id
            current_subscription.status = "active"
            await current_subscription.save()
            return current_subscription
        else:
            # Create new subscription (shouldn't happen, but handle gracefully)
            return await self.subscribe_user_to_plan(user, new_plan_name)
    
    async def cancel_user_subscription(self, user: User) -> bool:
        """Cancel user's subscription (move to free plan)."""
        current_subscription = await self.get_user_subscription(user)
        if current_subscription:
            current_subscription.status = "cancelled"
            await current_subscription.save()
            return True
        return False
    
    async def get_subscription_status(self, user: User) -> Dict[str, Any]:
        """Get detailed subscription status for a user."""
        subscription = await self.get_user_subscription(user)
        plan = await self.get_user_plan(user)
        
        if subscription:
            return {
                "has_subscription": True,
                "plan": {
                    "id": str(plan.id),
                    "name": plan.name,
                    "display_name": plan.display_name,
                    "monthly_tokens": plan.monthly_tokens,
                    "price_monthly": float(plan.price_monthly),
                    "features": plan.features
                },
                "subscription": {
                    "id": str(subscription.id),
                    "status": subscription.status,
                    "current_period_start": subscription.current_period_start.isoformat() if subscription.current_period_start else None,
                    "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
                    "stripe_subscription_id": subscription.stripe_subscription_id,
                    "created_at": subscription.created_at.isoformat()
                }
            }
        else:
            return {
                "has_subscription": False,
                "plan": {
                    "id": str(plan.id),
                    "name": plan.name,
                    "display_name": plan.display_name,
                    "monthly_tokens": plan.monthly_tokens,
                    "price_monthly": float(plan.price_monthly),
                    "features": plan.features
                },
                "subscription": None
            }
    
    async def compare_plans(self) -> Dict[str, Any]:
        """Get a comparison of all available plans."""
        plans = await self.get_all_plans()
        
        comparison = {
            "plans": [],
            "features": set()
        }
        
        for plan in plans:
            plan_data = {
                "id": str(plan.id),
                "name": plan.name,
                "display_name": plan.display_name,
                "monthly_tokens": plan.monthly_tokens,
                "price_monthly": float(plan.price_monthly),
                "features": plan.features or [],
                "is_popular": plan.name == "pro",  # Mark pro as popular
                "recommended": plan.name == "pro"
            }
            comparison["plans"].append(plan_data)
            
            # Collect all unique features
            if plan.features:
                comparison["features"].update(plan.features)
        
        comparison["features"] = list(comparison["features"])
        return comparison
    
    async def get_upgrade_options(self, user: User) -> List[Dict[str, Any]]:
        """Get available upgrade options for a user."""
        current_plan = await self.get_user_plan(user)
        all_plans = await self.get_all_plans()
        
        upgrade_options = []
        for plan in all_plans:
            if plan.price_monthly > current_plan.price_monthly:
                upgrade_options.append({
                    "id": str(plan.id),
                    "name": plan.name,
                    "display_name": plan.display_name,
                    "monthly_tokens": plan.monthly_tokens,
                    "price_monthly": float(plan.price_monthly),
                    "price_difference": float(plan.price_monthly - current_plan.price_monthly),
                    "token_increase": plan.monthly_tokens - current_plan.monthly_tokens,
                    "features": plan.features
                })
        
        return upgrade_options
    
    async def handle_subscription_webhook(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Handle Stripe webhook events (stub for now)."""
        # This would integrate with Stripe webhooks
        # For now, just log that we received the event
        print(f"Received Stripe webhook: {event_type}")
        print(f"Event data: {event_data}")
        
        if event_type == "customer.subscription.created":
            # Handle new subscription
            pass
        elif event_type == "customer.subscription.updated":
            # Handle subscription update
            pass
        elif event_type == "customer.subscription.deleted":
            # Handle subscription cancellation
            pass
        elif event_type == "invoice.payment_succeeded":
            # Handle successful payment
            pass
        elif event_type == "invoice.payment_failed":
            # Handle failed payment
            pass
        
        return True


# Plan-specific subscription handler
class PlanSubscriptionService:
    """
    Enhanced subscription service for Codemurf payment plans.
    Handles PAYG, Pro, Ultra subscriptions with API key management.
    """
    
    PLAN_CONFIG = {
        "payg": {
            "price_inr": 850,
            "price_usd": 10,
            "openrouter_limit_usd": 10.0,
            "requires_glm": False,
            "requires_bytez": False,
            "duration_days": None,  # Credits-based, no expiry
        },
        "pro": {
            "price_inr": 299,
            "price_usd": 3.50,
            "openrouter_limit_usd": None,  # Unlimited
            "requires_glm": True,
            "requires_bytez": False,
            "duration_days": 30,
        },
        "ultra": {
            "price_inr": 899,
            "price_usd": 10.50,
            "openrouter_limit_usd": None,  # Unlimited
            "requires_glm": True,
            "requires_bytez": True,
            "duration_days": 30,
            "auto_assign_keys": False,  # No auto-assignment for Ultra
        }
    }
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def activate_plan(self, user: User, plan_name: str, payment_id: str) -> Dict[str, Any]:
        """
        Activate a subscription plan for a user after successful payment.
        
        Returns activation result with api_keys status.
        """
        from ..models.api_key_pool import ApiKeyPool
        from ..models.user import SubscriptionPlan
        from .openrouter_keys import (
            provision_openrouter_key_with_limit,
            ensure_user_openrouter_key
        )
        
        plan_name = plan_name.lower()
        if plan_name not in self.PLAN_CONFIG:
            raise ValueError(f"Invalid plan: {plan_name}")
        
        config = self.PLAN_CONFIG[plan_name]
        now = datetime.now(timezone.utc)
        
        result = {
            "plan": plan_name,
            "api_keys": {"openrouter": False, "glm": False, "bytez": False}
        }
        
        # Update user payment info
        user.last_payment_id = payment_id
        user.total_spent_inr += config["price_inr"]
        user.subscription_plan = plan_name
        
        # Handle plan-specific logic
        if plan_name == "payg":
            # PAYG: Provision OpenRouter with $10 limit
            # PAYG users stay on FREE tier but get credits
            try:
                await provision_openrouter_key_with_limit(user, limit_usd=config["openrouter_limit_usd"])
                result["api_keys"]["openrouter"] = True
                result["credits_added_usd"] = config["openrouter_limit_usd"]
            except Exception as e:
                print(f"Failed to provision PAYG OpenRouter key: {e}")
        
        elif plan_name in ["pro", "ultra"]:
            # Set subscription dates
            user.subscription_start_date = now
            user.subscription_end_date = now + timedelta(days=config["duration_days"])
            # Use proper enum value
            user.subscription = SubscriptionPlan.PRO if plan_name == "pro" else SubscriptionPlan.ULTRA
            
            # Provision OpenRouter (unlimited)
            try:
                await ensure_user_openrouter_key(user)
                result["api_keys"]["openrouter"] = True
            except Exception as e:
                print(f"Failed to provision OpenRouter key: {e}")
            
            # Assign GLM key from pool
            if config["requires_glm"] and config.get("auto_assign_keys", True):
                glm_key = await self._assign_key_from_pool(user, "glm")
                if glm_key:
                    user.glm_api_key = glm_key
                    result["api_keys"]["glm"] = True
            
            # Assign Bytez key from pool (Ultra only)
            if config["requires_bytez"] and config.get("auto_assign_keys", True):
                bytez_key = await self._assign_key_from_pool(user, "bytez")
                if bytez_key:
                    user.bytez_api_key = bytez_key
                    result["api_keys"]["bytez"] = True
            
            result["subscription_end_date"] = user.subscription_end_date.isoformat()
        
        user.updated_at = now
        await user.save()
        
        result["role"] = plan_name
        return result
    
    async def _assign_key_from_pool(self, user: User, key_type: str) -> Optional[str]:
        """
        Assign an API key to user from the pool.
        Finds a key with capacity and assigns the user.
        """
        from ..models.api_key_pool import ApiKeyPool
        
        # Find available key with capacity
        available_keys = await ApiKeyPool.find({
            "key_type": key_type,
            "is_active": True
        }).to_list()
        
        for key in available_keys:
            if key.has_capacity:
                if key.assign_user(user.id):
                    await key.save()
                    return key.key_value
        
        # No available key found
        print(f"Warning: No {key_type} key available for user {user.id}")
        return None
    
    async def release_user_keys(self, user: User) -> None:
        """
        Release all API keys assigned to a user back to the pool.
        Called when subscription expires.
        """
        from ..models.api_key_pool import ApiKeyPool
        
        # Find all keys assigned to this user
        assigned_keys = await ApiKeyPool.find({
            "assigned_user_ids": user.id
        }).to_list()
        
        for key in assigned_keys:
            key.release_user(user.id)
            await key.save()
        
        # Clear user's API keys
        user.glm_api_key = None
        user.bytez_api_key = None
        user.updated_at = datetime.now(timezone.utc)
        await user.save()
    
    async def downgrade_user(self, user: User) -> None:
        """
        Downgrade user to free tier. Called when subscription expires.
        """
        from ..models.user import SubscriptionPlan
        
        # Release API keys back to pool
        await self.release_user_keys(user)
        
        # Update user subscription
        user.subscription = SubscriptionPlan.FREE
        user.subscription_plan = None
        user.subscription_start_date = None
        user.subscription_end_date = None
        user.updated_at = datetime.now(timezone.utc)
        await user.save()
    
    async def get_expired_subscriptions(self) -> List[User]:
        """Get all users with expired subscriptions."""
        now = datetime.now(timezone.utc)
        
        expired_users = await User.find({
            "subscription_end_date": {"$lt": now},
            "subscription": {"$in": ["pro", "ultra"]}
        }).to_list()
        
        return expired_users

