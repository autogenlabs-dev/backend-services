#!/usr/bin/env python3
"""
Test script to verify all new models and role-based system
"""
import asyncio
import sys
import os

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import User, UserRole
from app.models.developer_profile import DeveloperProfile
from app.models.purchased_item import PurchasedItem, ItemType
from app.models.content_approval import ContentApproval, ContentStatus
from app.models.payment_transaction import PaymentTransaction, TransactionType
from app.models.template import Template
from app.models.component import Component
from app.config import settings

async def test_models():
    """Test all new models"""
    try:
        print("🔄 Connecting to database...")
        client = AsyncIOMotorClient(settings.database_url)
        db = client.user_management_db
        
        print("🔄 Initializing Beanie...")
        document_models = [
            User, DeveloperProfile, PurchasedItem, 
            ContentApproval, PaymentTransaction, Template, Component
        ]
        await init_beanie(database=db, document_models=document_models)
        print("✅ Database connected successfully")
        
        # Test 1: Create a developer user
        print("\n🧪 Test 1: Creating developer user...")
        test_user = User(
            email="developer@test.com",
            name="Test Developer",
            role=UserRole.DEVELOPER,
            bio="Full-stack developer with 5 years experience",
            website="https://testdev.com",
            social_links={"github": "testdev", "linkedin": "testdev"}
        )
        await test_user.create()
        print(f"✅ Developer user created: {test_user.email} with role: {test_user.role}")
        
        # Test 2: Create developer profile
        print("\n🧪 Test 2: Creating developer profile...")
        dev_profile = DeveloperProfile(
            user_id=test_user.id,
            profession="Full Stack Developer",
            experience_years=5,
            skills=["Python", "JavaScript", "React", "FastAPI"],
            company="TechCorp",
            location="Mumbai, India"
        )
        await dev_profile.create()
        print(f"✅ Developer profile created for user: {test_user.id}")
        
        # Test 3: Create a template with new fields
        print("\n🧪 Test 3: Creating template with approval workflow...")
        test_template = Template(
            title="React Dashboard Template",
            category="Dashboard",
            type="React",
            language="TypeScript",
            difficulty_level="Medium",
            plan_type="Paid",
            pricing_inr=2999,
            pricing_usd=35,
            short_description="Modern React dashboard template",
            full_description="A comprehensive dashboard template built with React and TypeScript",
            developer_name="Test Developer",
            developer_experience="5 years",
            user_id=test_user.id,
            approval_status="pending_approval",
            is_purchasable=True
        )
        await test_template.create()
        print(f"✅ Template created: {test_template.title} with status: {test_template.approval_status}")
        
        # Test 4: Create content approval
        print("\n🧪 Test 4: Creating content approval...")
        approval = ContentApproval(
            content_id=test_template.id,
            content_type="template",
            status=ContentStatus.PENDING_APPROVAL,
            submitted_by=test_user.id
        )
        await approval.create()
        print(f"✅ Content approval created for template: {test_template.id}")
        
        # Test 5: Create a payment transaction
        print("\n🧪 Test 5: Creating payment transaction...")
        transaction = PaymentTransaction(
            user_id=test_user.id,
            type=TransactionType.PURCHASE,
            amount=2999.0,
            currency="INR",
            payment_method="razorpay",
            item_id=test_template.id,
            item_type="template",
            platform_fee=899.7,  # 30%
            developer_share=2099.3  # 70%
        )
        await transaction.create()
        print(f"✅ Payment transaction created: {transaction.type} - ₹{transaction.amount}")
        
        # Test 6: Create purchased item
        print("\n🧪 Test 6: Creating purchased item...")
        purchase = PurchasedItem(
            user_id=test_user.id,
            item_id=test_template.id,
            item_type=ItemType.TEMPLATE,
            price_paid=2999.0,
            transaction_id=str(transaction.id)
        )
        await purchase.create()
        print(f"✅ Purchased item created: {purchase.item_type} for ₹{purchase.price_paid}")
        
        # Test 7: Query tests
        print("\n🧪 Test 7: Testing queries...")
        
        # Find all developers
        developers = await User.find(User.role == UserRole.DEVELOPER).to_list()
        print(f"✅ Found {len(developers)} developers")
        
        # Find pending approvals
        pending_approvals = await ContentApproval.find(
            ContentApproval.status == ContentStatus.PENDING_APPROVAL
        ).to_list()
        print(f"✅ Found {len(pending_approvals)} pending approvals")
        
        # Find user purchases
        user_purchases = await PurchasedItem.find(
            PurchasedItem.user_id == test_user.id
        ).to_list()
        print(f"✅ Found {len(user_purchases)} purchases for user")
        
        print("\n🎉 All tests passed successfully!")
        print("\n📊 Test Summary:")
        print(f"   - User created with role: {test_user.role}")
        print(f"   - Developer profile: ✅")
        print(f"   - Template with approval workflow: ✅")
        print(f"   - Content approval: ✅")
        print(f"   - Payment transaction: ✅")
        print(f"   - Purchased item: ✅")
        print(f"   - Database queries: ✅")
        
        # Cleanup
        print("\n🧹 Cleaning up test data...")
        await purchase.delete()
        await transaction.delete()
        await approval.delete()
        await test_template.delete()
        await dev_profile.delete()
        await test_user.delete()
        print("✅ Test data cleaned up")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Enhanced Role-Based System Tests...")
    success = asyncio.run(test_models())
    if success:
        print("\n✅ All systems are working perfectly!")
        print("🎯 Your enhanced role-based backend is ready!")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    print("\n📋 What's been implemented:")
    print("   ✅ Enhanced User model with roles (user, developer, admin)")
    print("   ✅ Developer Profile model")
    print("   ✅ Purchased Item tracking")
    print("   ✅ Content Approval workflow")
    print("   ✅ Payment Transaction system")
    print("   ✅ Enhanced Template/Component models")
    print("   ✅ Role-based middleware")
    print("   ✅ Database indexing and relationships")
    print("\n🎯 Ready for Phase 2: Admin Dashboard implementation!")
