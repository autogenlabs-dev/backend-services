"""Subscription management service with real business logic."""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.user import User, SubscriptionPlan, UserSubscription


class SubscriptionService:
    """Service for managing user subscriptions and plan enforcement."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_plans(self) -> List[SubscriptionPlan]:
        """Get all active subscription plans."""
        return (
            self.db.query(SubscriptionPlan)
            .filter(SubscriptionPlan.is_active == True)
            .order_by(SubscriptionPlan.price_monthly.asc())
            .all()
        )
    
    def get_plan_by_name(self, plan_name: str) -> Optional[SubscriptionPlan]:
        """Get a subscription plan by name."""
        return (
            self.db.query(SubscriptionPlan)
            .filter(SubscriptionPlan.name == plan_name)
            .filter(SubscriptionPlan.is_active == True)
            .first()
        )
    
    def get_user_subscription(self, user: User) -> Optional[UserSubscription]:
        """Get user's current active subscription."""
        return (
            self.db.query(UserSubscription)
            .filter(UserSubscription.user_id == user.id)
            .filter(UserSubscription.status == "active")
            .first()
        )
    
    def get_user_plan(self, user: User) -> SubscriptionPlan:
        """Get user's current plan, defaulting to free."""
        subscription = self.get_user_subscription(user)
        if subscription:
            return subscription.plan
        
        # Return free plan as default
        free_plan = self.get_plan_by_name("free")
        if not free_plan:
            # Create default free plan if it doesn't exist
            free_plan = self._create_default_free_plan()
        
        return free_plan
    
    def _create_default_free_plan(self) -> SubscriptionPlan:
        """Create a default free plan."""
        free_plan = SubscriptionPlan(
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
        self.db.add(free_plan)
        self.db.commit()
        self.db.refresh(free_plan)
        return free_plan
    
    def subscribe_user_to_plan(self, user: User, plan_name: str, stripe_subscription_id: Optional[str] = None) -> UserSubscription:
        """Subscribe user to a new plan."""
        plan = self.get_plan_by_name(plan_name)
        if not plan:
            raise ValueError(f"Plan '{plan_name}' not found")
        
        # Deactivate existing subscription
        existing_subscription = self.get_user_subscription(user)
        if existing_subscription:
            existing_subscription.status = "cancelled"
            self.db.add(existing_subscription)
        
        # Calculate billing period
        now = datetime.utcnow()
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
        
        self.db.add(new_subscription)
        self.db.commit()
        self.db.refresh(new_subscription)
        
        return new_subscription
    
    def upgrade_user_subscription(self, user: User, new_plan_name: str) -> UserSubscription:
        """Upgrade user's subscription to a higher plan."""
        new_plan = self.get_plan_by_name(new_plan_name)
        if not new_plan:
            raise ValueError(f"Plan '{new_plan_name}' not found")
        
        current_subscription = self.get_user_subscription(user)
        current_plan = self.get_user_plan(user)
        
        # Validate upgrade (new plan should be more expensive)
        if new_plan.price_monthly <= current_plan.price_monthly:
            raise ValueError("New plan must be a higher tier")
        
        if current_subscription:
            # Update existing subscription
            current_subscription.plan_id = new_plan.id
            current_subscription.status = "active"
            # Keep the same billing period for simplicity
            self.db.add(current_subscription)
            self.db.commit()
            self.db.refresh(current_subscription)
            return current_subscription
        else:
            # Create new subscription
            return self.subscribe_user_to_plan(user, new_plan_name)
    
    def downgrade_user_subscription(self, user: User, new_plan_name: str) -> UserSubscription:
        """Downgrade user's subscription to a lower plan."""
        new_plan = self.get_plan_by_name(new_plan_name)
        if not new_plan:
            raise ValueError(f"Plan '{new_plan_name}' not found")
        
        current_subscription = self.get_user_subscription(user)
        current_plan = self.get_user_plan(user)
        
        # Validate downgrade (new plan should be less expensive)
        if new_plan.price_monthly >= current_plan.price_monthly:
            raise ValueError("New plan must be a lower tier")
        
        if current_subscription:
            # Update existing subscription
            current_subscription.plan_id = new_plan.id
            current_subscription.status = "active"
            self.db.add(current_subscription)
            self.db.commit()
            self.db.refresh(current_subscription)
            return current_subscription
        else:
            # Create new subscription (shouldn't happen, but handle gracefully)
            return self.subscribe_user_to_plan(user, new_plan_name)
    
    def cancel_user_subscription(self, user: User) -> bool:
        """Cancel user's subscription (move to free plan)."""
        current_subscription = self.get_user_subscription(user)
        if current_subscription:
            current_subscription.status = "cancelled"
            self.db.add(current_subscription)
            self.db.commit()
            return True
        return False
    
    def get_subscription_status(self, user: User) -> Dict[str, Any]:
        """Get detailed subscription status for a user."""
        subscription = self.get_user_subscription(user)
        plan = self.get_user_plan(user)
        
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
    
    def compare_plans(self) -> Dict[str, Any]:
        """Get a comparison of all available plans."""
        plans = self.get_all_plans()
        
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
                "features": plan.features or {},
                "is_popular": plan.name == "pro",  # Mark pro as popular
                "recommended": plan.name == "pro"
            }
            comparison["plans"].append(plan_data)
            
            # Collect all unique features
            if plan.features:
                comparison["features"].update(plan.features.keys())
        
        comparison["features"] = list(comparison["features"])
        return comparison
    
    def get_upgrade_options(self, user: User) -> List[Dict[str, Any]]:
        """Get available upgrade options for a user."""
        current_plan = self.get_user_plan(user)
        all_plans = self.get_all_plans()
        
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
    
    def handle_subscription_webhook(self, event_type: str, event_data: Dict[str, Any]) -> bool:
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
