"""Stripe payment processing service."""

import stripe
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from decimal import Decimal
from sqlalchemy.orm import Session

from ..config import settings
from ..models.user import User, SubscriptionPlan, UserSubscription
from .subscription_service import SubscriptionService


# Configure Stripe API key
stripe.api_key = settings.stripe_secret_key


class StripeService:
    """Service for handling Stripe payment processing."""
    
    def __init__(self, db: Session):
        self.db = db
        self.subscription_service = SubscriptionService(db)
    
    def create_customer(self, user: User) -> str:
        """Create a Stripe customer for a user."""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                metadata={
                    "user_id": str(user.id),
                    "source": "vscode_extension"
                }
            )
            
            # Store Stripe customer ID on user
            user.stripe_customer_id = customer.id
            self.db.add(user)
            self.db.commit()
            
            return customer.id
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create Stripe customer: {str(e)}")
    
    def get_or_create_customer(self, user: User) -> str:
        """Get existing Stripe customer ID or create new one."""
        if user.stripe_customer_id:
            try:
                # Verify customer still exists
                stripe.Customer.retrieve(user.stripe_customer_id)
                return user.stripe_customer_id
            except stripe.error.InvalidRequestError:
                # Customer doesn't exist, create new one
                pass
        
        return self.create_customer(user)
    
    def create_subscription(self, user: User, plan_name: str) -> Dict[str, Any]:
        """Create a new Stripe subscription for a user."""
        try:
            plan = self.subscription_service.get_plan_by_name(plan_name)
            if not plan:
                raise ValueError(f"Plan '{plan_name}' not found")
            
            if not plan.stripe_price_id:
                raise ValueError(f"Plan '{plan_name}' has no Stripe price ID configured")
            
            customer_id = self.get_or_create_customer(user)
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": plan.stripe_price_id}],
                metadata={
                    "user_id": str(user.id),
                    "plan_name": plan_name
                },
                expand=["latest_invoice.payment_intent"]
            )
            
            # Create local subscription record
            user_subscription = self.subscription_service.subscribe_user_to_plan(
                user=user,
                plan_name=plan_name,
                stripe_subscription_id=subscription.id
            )
            
            return {
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "status": subscription.status,
                "user_subscription_id": str(user_subscription.id)
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create subscription: {str(e)}")
    
    def upgrade_subscription(self, user: User, new_plan_name: str) -> Dict[str, Any]:
        """Upgrade a user's subscription to a higher plan."""
        try:
            new_plan = self.subscription_service.get_plan_by_name(new_plan_name)
            if not new_plan or not new_plan.stripe_price_id:
                raise ValueError(f"Invalid plan: {new_plan_name}")
            
            current_subscription = self.subscription_service.get_user_subscription(user)
            if not current_subscription or not current_subscription.stripe_subscription_id:
                raise ValueError("No active subscription found")
            
            # Update Stripe subscription
            stripe_subscription = stripe.Subscription.modify(
                current_subscription.stripe_subscription_id,
                items=[{
                    "id": stripe.Subscription.retrieve(current_subscription.stripe_subscription_id).items.data[0].id,
                    "price": new_plan.stripe_price_id,
                }],
                proration_behavior="immediate_with_remainder"
            )
            
            # Update local subscription
            updated_subscription = self.subscription_service.upgrade_user_subscription(
                user=user,
                new_plan_name=new_plan_name
            )
            
            return {
                "subscription_id": stripe_subscription.id,
                "status": stripe_subscription.status,
                "user_subscription_id": str(updated_subscription.id),
                "message": f"Successfully upgraded to {new_plan.display_name}"
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to upgrade subscription: {str(e)}")
    
    def cancel_subscription(self, user: User) -> Dict[str, Any]:
        """Cancel a user's subscription."""
        try:
            current_subscription = self.subscription_service.get_user_subscription(user)
            if not current_subscription or not current_subscription.stripe_subscription_id:
                raise ValueError("No active subscription found")
            
            # Cancel at period end to allow continued usage
            stripe_subscription = stripe.Subscription.modify(
                current_subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )
            
            # Update local subscription status
            self.subscription_service.cancel_user_subscription(user)
            
            return {
                "subscription_id": stripe_subscription.id,
                "status": "cancelling",
                "cancel_at": datetime.fromtimestamp(stripe_subscription.current_period_end),
                "message": "Subscription will cancel at the end of the current billing period"
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to cancel subscription: {str(e)}")
    
    def get_payment_methods(self, user: User) -> List[Dict[str, Any]]:
        """Get user's saved payment methods."""
        try:
            customer_id = self.get_or_create_customer(user)
            
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
            
            return [{
                "id": pm.id,
                "brand": pm.card.brand,
                "last4": pm.card.last4,
                "exp_month": pm.card.exp_month,
                "exp_year": pm.card.exp_year,
                "is_default": False  # Would need to check default payment method
            } for pm in payment_methods.data]
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to retrieve payment methods: {str(e)}")
    
    def create_payment_intent(self, user: User, amount: Decimal, currency: str = "usd") -> Dict[str, Any]:
        """Create a payment intent for one-time payments."""
        try:
            customer_id = self.get_or_create_customer(user)
            
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe uses cents
                currency=currency,
                customer=customer_id,
                metadata={
                    "user_id": str(user.id),
                    "type": "token_purchase"
                }
            )
            
            return {
                "client_secret": intent.client_secret,
                "amount": amount,
                "currency": currency
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create payment intent: {str(e)}")
    
    def handle_webhook(self, payload: str, sig_header: str) -> Dict[str, Any]:
        """Handle Stripe webhook events."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.stripe_webhook_secret
            )
            
            event_type = event["type"]
            event_data = event["data"]["object"]
            
            if event_type == "customer.subscription.created":
                return self._handle_subscription_created(event_data)
            elif event_type == "customer.subscription.updated":
                return self._handle_subscription_updated(event_data)
            elif event_type == "customer.subscription.deleted":
                return self._handle_subscription_deleted(event_data)
            elif event_type == "invoice.payment_succeeded":
                return self._handle_payment_succeeded(event_data)
            elif event_type == "invoice.payment_failed":
                return self._handle_payment_failed(event_data)
            
            return {"status": "ignored", "event_type": event_type}
            
        except ValueError as e:
            raise Exception(f"Invalid webhook payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            raise Exception(f"Invalid webhook signature: {str(e)}")
    
    def _handle_subscription_created(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription.created webhook."""
        # Extract user_id from metadata
        user_id = subscription_data.get("metadata", {}).get("user_id")
        if not user_id:
            return {"status": "error", "message": "No user_id in metadata"}
        
        # Update subscription status if needed
        user_subscription = (
            self.db.query(UserSubscription)
            .filter(UserSubscription.stripe_subscription_id == subscription_data["id"])
            .first()
        )
        
        if user_subscription:
            user_subscription.status = "active"
            user_subscription.current_period_start = datetime.fromtimestamp(subscription_data["current_period_start"])
            user_subscription.current_period_end = datetime.fromtimestamp(subscription_data["current_period_end"])
            self.db.add(user_subscription)
            self.db.commit()
        
        return {"status": "processed", "subscription_id": subscription_data["id"]}
    
    def _handle_subscription_updated(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription.updated webhook."""
        user_subscription = (
            self.db.query(UserSubscription)
            .filter(UserSubscription.stripe_subscription_id == subscription_data["id"])
            .first()
        )
        
        if user_subscription:
            user_subscription.status = subscription_data["status"]
            user_subscription.current_period_start = datetime.fromtimestamp(subscription_data["current_period_start"])
            user_subscription.current_period_end = datetime.fromtimestamp(subscription_data["current_period_end"])
            self.db.add(user_subscription)
            self.db.commit()
        
        return {"status": "processed", "subscription_id": subscription_data["id"]}
    
    def _handle_subscription_deleted(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription.deleted webhook."""
        user_subscription = (
            self.db.query(UserSubscription)
            .filter(UserSubscription.stripe_subscription_id == subscription_data["id"])
            .first()
        )
        
        if user_subscription:
            user_subscription.status = "cancelled"
            self.db.add(user_subscription)
            self.db.commit()
        
        return {"status": "processed", "subscription_id": subscription_data["id"]}
    
    def _handle_payment_succeeded(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle invoice.payment_succeeded webhook."""
        # Could be used to reset token balance or send confirmation emails
        return {"status": "processed", "invoice_id": invoice_data["id"]}
    
    def _handle_payment_failed(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle invoice.payment_failed webhook."""
        # Could be used to notify users of failed payments
        return {"status": "processed", "invoice_id": invoice_data["id"]}
