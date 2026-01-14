"""
Seed Subscription Plans Script
Seeds the subscription_plans collection in MongoDB

Usage:
    python seed_subscription_plans.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import SubscriptionPlanModel
from app.config import settings


async def seed_subscription_plans():
    """Seed subscription plans to database"""
    
    print("🚀 Starting subscription plans seeding...")
    print(f"📦 Database: {settings.database_url.split('@')[-1] if '@' in settings.database_url else settings.database_url}")
    
    # Connect to database
    client = AsyncIOMotorClient(settings.database_url)
    database = client["user_management_db"]
    
    # Initialize Beanie
    await init_beanie(database=database, document_models=[SubscriptionPlanModel])
    print("✅ Database connected\n")
    
    # Check existing plans
    existing_count = await SubscriptionPlanModel.find({}).count()
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing plans. Skipping seed.")
        print("   Use --clear flag to clear and reseed.")
        
        # List existing plans
        plans = await SubscriptionPlanModel.find({}).to_list()
        for plan in plans:
            print(f"   - {plan.name}: ${plan.price_monthly}/month, {plan.monthly_tokens} tokens")
        
        client.close()
        return
    
    # Define subscription plans
    plans_data = [
        {
            "name": "free",
            "display_name": "Free Plan",
            "monthly_tokens": 10000,
            "price_monthly": 0.00,
            "stripe_price_id": None,
            "features": [
                "10,000 tokens/month",
                "Basic models access",
                "Community support",
                "Standard response times"
            ],
            "is_active": True
        },
        {
            "name": "payg",
            "display_name": "Pay As You Go",
            "monthly_tokens": 100000,  # Credits-based
            "price_monthly": 10.00,  # $10 credits
            "stripe_price_id": None,
            "features": [
                "$10 credits (no expiry)",
                "All basic models",
                "Email support",
                "Usage tracking"
            ],
            "is_active": True
        },
        {
            "name": "pro",
            "display_name": "Pro Plan",
            "monthly_tokens": 500000,
            "price_monthly": 3.50,  # ₹299 (~$3.50)
            "stripe_price_id": None,
            "features": [
                "500,000 tokens/month",
                "GPT-4, Claude, and advanced models",
                "GLM API key included",
                "Priority support",
                "Faster response times",
                "30-day subscription"
            ],
            "is_active": True
        },
        {
            "name": "ultra",
            "display_name": "Ultra Plan",
            "monthly_tokens": 2000000,
            "price_monthly": 10.50,  # ₹899 (~$10.50)
            "stripe_price_id": None,
            "features": [
                "2,000,000 tokens/month",
                "All AI models including latest",
                "GLM + Bytez API keys",
                "Premium support",
                "Fastest response times",
                "Team features",
                "30-day subscription"
            ],
            "is_active": True
        }
    ]
    
    print("📋 Creating subscription plans...")
    for plan_data in plans_data:
        plan = SubscriptionPlanModel(**plan_data)
        await plan.insert()
        print(f"✅ {plan.display_name} - ${plan.price_monthly}/month, {plan.monthly_tokens:,} tokens")
    
    # Verify
    print("\n📊 Verification:")
    total = await SubscriptionPlanModel.find({}).count()
    print(f"✅ Total plans created: {total}")
    
    client.close()
    print("\n✅ Subscription plans seeded successfully!\n")


async def clear_and_seed():
    """Clear existing plans and reseed"""
    client = AsyncIOMotorClient(settings.database_url)
    database = client["user_management_db"]
    await init_beanie(database=database, document_models=[SubscriptionPlanModel])
    
    deleted = await SubscriptionPlanModel.find({}).delete()
    print(f"🗑️  Cleared {deleted.deleted_count} existing plans")
    client.close()
    
    await seed_subscription_plans()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed subscription plans")
    parser.add_argument("--clear", action="store_true", help="Clear existing plans before seeding")
    args = parser.parse_args()
    
    if args.clear:
        asyncio.run(clear_and_seed())
    else:
        asyncio.run(seed_subscription_plans())
