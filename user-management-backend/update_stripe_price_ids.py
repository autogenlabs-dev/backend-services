#!/usr/bin/env python3
"""
Update Stripe Price IDs in subscription plans
This script updates the database with the Stripe price IDs generated during testing.
"""
import sys
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError

# Configuration
DATABASE_URL = "sqlite:///./test.db"
PRO_PLAN_PRICE_ID = "price_1RZHEU00tZAh2watv4rB5k9M"
ENTERPRISE_PLAN_PRICE_ID = "price_1RZHEV00tZAh2watN7lx4nW2"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def update_price_ids():
    """Update subscription plans with Stripe price IDs."""
    db = SessionLocal()
    
    try:
        # Update Pro plan
        db.execute(
            text("UPDATE subscription_plans SET stripe_price_id = :price_id WHERE name = 'pro'"),
            {"price_id": PRO_PLAN_PRICE_ID}
        )
        print("✅ Updated Pro plan with price ID:", PRO_PLAN_PRICE_ID)
        
        # Update Enterprise plan
        db.execute(
            text("UPDATE subscription_plans SET stripe_price_id = :price_id WHERE name = 'enterprise'"),
            {"price_id": ENTERPRISE_PLAN_PRICE_ID}
        )
        print("✅ Updated Enterprise plan with price ID:", ENTERPRISE_PLAN_PRICE_ID)
        
        # Commit changes
        db.commit()
        print("✅ Changes committed to database")
        
        # Verify updates
        result = db.execute(text("SELECT name, stripe_price_id FROM subscription_plans")).fetchall()
        print("\n📋 CURRENT SUBSCRIPTION PLANS:")
        for row in result:
            print(f"   {row[0].upper()}: {row[1]}")
        
    except SQLAlchemyError as e:
        db.rollback()
        print("❌ Database error:", str(e))
    except Exception as e:
        print("❌ Error:", str(e))
    finally:
        db.close()

if __name__ == "__main__":
    print("🔄 UPDATING STRIPE PRICE IDs IN DATABASE")
    print("=" * 50)
    update_price_ids()