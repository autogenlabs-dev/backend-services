"""Database initialization script to populate initial data."""

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.user import OAuthProvider, SubscriptionPlan
from uuid import uuid4
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_oauth_providers(db: Session):
    """Initialize OAuth providers."""
    providers = [
        {
            "name": "openrouter",
            "display_name": "OpenRouter",
            "is_active": True
        },
        {
            "name": "glama",
            "display_name": "Glama",
            "is_active": True
        },
        {
            "name": "requesty",
            "display_name": "Requesty",
            "is_active": True
        }
    ]
    
    for provider_data in providers:
        # Check if provider already exists
        existing_provider = db.query(OAuthProvider).filter(
            OAuthProvider.name == provider_data["name"]
        ).first()
        
        if not existing_provider:
            provider = OAuthProvider(
                id=uuid4(),
                **provider_data
            )
            db.add(provider)
            logger.info(f"Created OAuth provider: {provider_data['name']}")
        else:
            logger.info(f"OAuth provider already exists: {provider_data['name']}")
    
    db.commit()


def init_subscription_plans(db: Session):
    """Initialize subscription plans."""
    plans = [
        {
            "name": "free",
            "display_name": "Free Plan",
            "monthly_tokens": 1000,
            "price_monthly": 0.00,
            "features": {
                "models": ["basic"],
                "support": "community",
                "api_access": False,
                "max_requests_per_minute": 10
            },
            "is_active": True
        },
        {
            "name": "pro",
            "display_name": "Pro Plan",
            "monthly_tokens": 10000,
            "price_monthly": 9.99,
            "features": {
                "models": ["basic", "advanced"],
                "support": "email",
                "api_access": True,
                "max_requests_per_minute": 60,
                "priority_support": True
            },
            "is_active": True
        },
        {
            "name": "enterprise",
            "display_name": "Enterprise Plan",
            "monthly_tokens": 100000,
            "price_monthly": 49.99,
            "features": {
                "models": ["basic", "advanced", "premium"],
                "support": "priority",
                "api_access": True,
                "max_requests_per_minute": 300,
                "priority_support": True,
                "custom_integrations": True,
                "dedicated_support": True
            },
            "is_active": True
        }
    ]
    
    for plan_data in plans:
        # Check if plan already exists
        existing_plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.name == plan_data["name"]
        ).first()
        
        if not existing_plan:
            plan = SubscriptionPlan(
                id=uuid4(),
                **plan_data
            )
            db.add(plan)
            logger.info(f"Created subscription plan: {plan_data['name']}")
        else:
            logger.info(f"Subscription plan already exists: {plan_data['name']}")
    
    db.commit()


def main():
    """Main initialization function."""
    logger.info("Starting database initialization...")
    
    db = SessionLocal()
    try:
        init_oauth_providers(db)
        init_subscription_plans(db)
        logger.info("Database initialization completed successfully!")
        
        # Print summary
        provider_count = db.query(OAuthProvider).count()
        plan_count = db.query(SubscriptionPlan).count()
        logger.info(f"Total OAuth providers: {provider_count}")
        logger.info(f"Total subscription plans: {plan_count}")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
