#!/usr/bin/env python3
"""
Clean Database Setup Script
Completely recreates the database with proper schema.
"""

import os
import sys
from datetime import datetime, timezone
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import Base, engine, SessionLocal
from app.models.user import (
    User, OAuthProvider, UserOAuthAccount, SubscriptionPlan,
    UserSubscription, TokenUsageLog, ApiKey, Organization,
    OrganizationMember, OrganizationInvitation, OrganizationKey,
    KeyUsageLog
)


def clean_setup_database():
    """Clean setup of the database."""
    print("🔄 Starting clean database setup...")
    
    try:
        # Drop all tables if they exist
        print("🗑️  Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        print("🏗️  Creating new tables...")
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"✅ Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"   - {table}")
        
        # Create session and add default data
        db = SessionLocal()
        
        try:
            # Add default OAuth providers
            oauth_providers = [
                OAuthProvider(name="google", client_id="google_client_id", enabled=True),
                OAuthProvider(name="github", client_id="github_client_id", enabled=True),
                OAuthProvider(name="microsoft", client_id="microsoft_client_id", enabled=False),
            ]
            
            for provider in oauth_providers:
                db.add(provider)
            
            # Add default subscription plans
            subscription_plans = [
                SubscriptionPlan(
                    name="Free",
                    description="Free tier with basic features",
                    price=0.00,
                    monthly_tokens=10000,
                    features={"api_access": True, "support": "community"},
                    is_active=True
                ),
                SubscriptionPlan(
                    name="Pro",
                    description="Professional tier with advanced features",
                    price=29.99,
                    monthly_tokens=100000,
                    features={"api_access": True, "support": "email", "priority": True},
                    is_active=True
                ),
                SubscriptionPlan(
                    name="Enterprise",
                    description="Enterprise tier with unlimited features",
                    price=99.99,
                    monthly_tokens=1000000,
                    features={"api_access": True, "support": "phone", "priority": True, "custom": True},
                    is_active=True
                ),
            ]
            
            for plan in subscription_plans:
                db.add(plan)
            
            db.commit()
            print("✅ Added default OAuth providers and subscription plans")
            
        except Exception as e:
            db.rollback()
            print(f"⚠️  Warning: Could not add default data: {e}")
        finally:
            db.close()
        
        print("🎉 Database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False


if __name__ == "__main__":
    success = clean_setup_database()
    sys.exit(0 if success else 1)
