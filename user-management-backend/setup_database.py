#!/usr/bin/env python3
"""
Database setup script to create all required tables and initialize data
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User, OAuthProvider, SubscriptionPlan
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_all_tables():
    """Create all database tables."""
    try:
        # Create engine
        engine = create_engine(settings.database_url)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("All tables created successfully!")
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Initialize OAuth providers
        init_oauth_providers(db)
        
        # Initialize subscription plans  
        init_subscription_plans(db)
        
        db.close()
        logger.info("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def init_oauth_providers(db):
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
            provider = OAuthProvider(**provider_data)
            db.add(provider)
            logger.info(f"Created OAuth provider: {provider_data['name']}")
        else:
            logger.info(f"OAuth provider already exists: {provider_data['name']}")
    
    try:
        db.commit()
    except Exception as e:
        logger.error(f"Error initializing OAuth providers: {e}")
        db.rollback()

def init_subscription_plans(db):
    """Initialize subscription plans."""
    plans = [
        {
            "name": "free",
            "display_name": "Free Plan",
            "monthly_tokens": 10000,
            "price_monthly": 0.00,
            "is_active": True
        },
        {
            "name": "pro",
            "display_name": "Pro Plan", 
            "monthly_tokens": 100000,
            "price_monthly": 29.99,
            "is_active": True
        },
        {
            "name": "enterprise",
            "display_name": "Enterprise Plan",
            "monthly_tokens": 1000000,
            "price_monthly": 99.99,
            "is_active": True
        }
    ]
    
    for plan_data in plans:
        # Check if plan already exists
        existing_plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.name == plan_data["name"]
        ).first()
        
        if not existing_plan:
            plan = SubscriptionPlan(**plan_data)
            db.add(plan)
            logger.info(f"Created subscription plan: {plan_data['name']}")
        else:
            logger.info(f"Subscription plan already exists: {plan_data['name']}")
    
    try:
        db.commit()
    except Exception as e:
        logger.error(f"Error initializing subscription plans: {e}")
        db.rollback()

if __name__ == "__main__":
    print("Setting up database...")
    success = create_all_tables()
    if success:
        print("✅ Database setup completed successfully!")
    else:
        print("❌ Database setup failed!")
        exit(1)
