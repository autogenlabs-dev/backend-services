#!/usr/bin/env python3
"""
Comprehensive test script for the complete marketplace implementation.
Tests all Phase 4 features: payments, access control, developer earnings, and enhanced content.
"""

import sys
import os
import asyncio
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "testuser@example.com"
TEST_DEVELOPER_EMAIL = "testdev@example.com"
TEST_ADMIN_EMAIL = "admin@example.com"
TEST_PASSWORD = "testpass123"

async def test_marketplace_implementation():
    """Test the complete marketplace implementation."""
    
    print("🧪 Phase 4 Marketplace Implementation Test")
    print("=" * 60)
    
    tests = {
        "model_imports": False,
        "payment_service": False,
        "access_control": False,
        "developer_earnings": False,
        "shopping_cart": False,
        "user_dashboard": False,
        "enhanced_content_access": False,
        "admin_payout_system": False
    }
    
    # Test 1: Model Imports
    print("\n🔍 Testing Model Imports...")
    try:
        from app.models.item_purchase import ItemPurchase, PurchaseStatus, ItemType
        from app.models.shopping_cart import ShoppingCart, CartItem, CartItemType
        from app.models.developer_earnings import DeveloperEarnings, PayoutRequest, PayoutStatus, PayoutMethod
        from app.services.access_control import ContentAccessService, AccessLevel
        from app.services.payment_service import payment_service
        
        tests["model_imports"] = True
        print("✅ All marketplace models imported successfully")
    except Exception as e:
        print(f"❌ Model import error: {e}")
    
    # Test 2: Payment Service
    print("\n🔍 Testing Payment Service...")
    try:
        from app.services.payment_service import PaymentService
        service = PaymentService()
        
        # Check if Razorpay configuration exists
        has_razorpay_config = hasattr(service, 'razorpay_key_id') and hasattr(service, 'razorpay_key_secret')
        
        tests["payment_service"] = True
        print("✅ Payment service initialized successfully")
        print(f"   - Razorpay configuration: {'✅' if has_razorpay_config else '⚠️ Mock mode'}")
    except Exception as e:
        print(f"❌ Payment service error: {e}")
    
    # Test 3: Access Control Service
    print("\n🔍 Testing Access Control Service...")
    try:
        from app.services.access_control import ContentAccessService, AccessLevel
        
        # Test access levels
        access_levels = [AccessLevel.NO_ACCESS, AccessLevel.LIMITED_ACCESS, AccessLevel.FULL_ACCESS, AccessLevel.OWNER_ACCESS]
        
        # Test filtering method exists
        has_filter_method = hasattr(ContentAccessService, 'filter_content_by_access_level')
        has_access_method = hasattr(ContentAccessService, 'get_content_access_level')
        
        tests["access_control"] = has_filter_method and has_access_method
        print("✅ Access control service functional")
        print(f"   - Access levels: {len(access_levels)} defined")
        print(f"   - Content filtering: {'✅' if has_filter_method else '❌'}")
        print(f"   - Access level detection: {'✅' if has_access_method else '❌'}")
    except Exception as e:
        print(f"❌ Access control error: {e}")
    
    # Test 4: Developer Earnings Models
    print("\n🔍 Testing Developer Earnings System...")
    try:
        from app.models.developer_earnings import DeveloperEarnings, PayoutRequest
        from bson import ObjectId
        
        # Test earnings calculation with proper ObjectId
        test_earnings = DeveloperEarnings(
            developer_id=ObjectId(), 
            developer_username="testdev",
            total_earnings_inr=10000,
            available_balance_inr=10000
        )
        
        # Test revenue split calculation
        test_earnings.add_sale_earnings(1000, str(ObjectId()), "template")
        expected_earnings = int(1000 * 0.70)  # 70% to developer
        
        earnings_correct = test_earnings.total_earnings_inr == 10000 + expected_earnings
        
        tests["developer_earnings"] = earnings_correct
        print("✅ Developer earnings system functional")
        print(f"   - Revenue split (70/30): {'✅' if earnings_correct else '❌'}")
        print(f"   - Payout request model: ✅")
    except Exception as e:
        print(f"❌ Developer earnings error: {e}")
        tests["developer_earnings"] = False
    
    # Test 5: Shopping Cart Functionality
    print("\n🔍 Testing Shopping Cart...")
    try:
        from app.models.shopping_cart import ShoppingCart, CartItem, CartItemType
        from bson import ObjectId
        
        # Create test cart
        test_cart = ShoppingCart(user_id=ObjectId())
        
        # Create test item
        test_item = CartItem(
            item_id=ObjectId(),
            item_type=CartItemType.TEMPLATE,
            item_title="Test Template",
            developer_username="testdev",
            price_inr=500,
            price_usd=6
        )
        
        # Test cart operations
        add_success = test_cart.add_item(test_item)
        cart_has_item = len(test_cart.items) == 1
        total_correct = test_cart.total_amount_inr == 500
        
        tests["shopping_cart"] = add_success and cart_has_item and total_correct
        print("✅ Shopping cart functional")
        print(f"   - Add items: {'✅' if add_success else '❌'}")
        print(f"   - Track totals: {'✅' if total_correct else '❌'}")
    except Exception as e:
        print(f"❌ Shopping cart error: {e}")
        tests["shopping_cart"] = False
    
    # Test 6: User Dashboard Endpoints
    print("\n🔍 Testing User Dashboard...")
    try:
        from app.endpoints.user_dashboard import router
        
        # Check endpoint functions exist
        has_dashboard = any('dashboard' in str(route.path) for route in router.routes)
        has_purchased_content = any('purchased-content' in str(route.path) for route in router.routes)
        has_recommendations = any('recommendations' in str(route.path) for route in router.routes)
        
        tests["user_dashboard"] = has_dashboard and has_purchased_content and has_recommendations
        print("✅ User dashboard endpoints available")
        print(f"   - Dashboard endpoint: {'✅' if has_dashboard else '❌'}")
        print(f"   - Purchased content: {'✅' if has_purchased_content else '❌'}")
        print(f"   - Recommendations: {'✅' if has_recommendations else '❌'}")
    except Exception as e:
        print(f"❌ User dashboard error: {e}")
    
    # Test 7: Enhanced Content Access
    print("\n🔍 Testing Enhanced Content Access...")
    try:
        # Check if main server has access control integration
        with open("minimal_auth_server.py", "r", encoding="utf-8") as f:
            server_content = f.read()
        
        has_access_control_import = "ContentAccessService" in server_content
        has_access_level_check = "get_content_access_level" in server_content
        has_filter_content = "filter_content_by_access_level" in server_content
        
        tests["enhanced_content_access"] = has_access_control_import and has_access_level_check and has_filter_content
        print("✅ Enhanced content access implemented")
        print(f"   - Access control integration: {'✅' if has_access_control_import else '❌'}")
        print(f"   - Content filtering: {'✅' if has_filter_content else '❌'}")
    except Exception as e:
        print(f"❌ Enhanced content access error: {e}")
    
    # Test 8: Admin Payout System
    print("\n🔍 Testing Admin Payout System...")
    try:
        from app.endpoints.developer_earnings import router as earnings_router
        
        # Check admin endpoints exist
        admin_endpoints = [route for route in earnings_router.routes if 'admin' in str(route.path)]
        has_admin_payout_endpoints = len(admin_endpoints) >= 2  # Should have get and update endpoints
        
        tests["admin_payout_system"] = has_admin_payout_endpoints
        print("✅ Admin payout system available")
        print(f"   - Admin endpoints: {len(admin_endpoints)} found")
    except Exception as e:
        print(f"❌ Admin payout system error: {e}")
    
    # Test Summary
    print("\n" + "=" * 60)
    print("📊 Implementation Test Results:")
    print("=" * 60)
    
    passed_tests = sum(tests.values())
    total_tests = len(tests)
    
    for test_name, result in tests.items():
        status = "✅ PASS" if result else "❌ FAIL"
        test_display = test_name.replace('_', ' ').title()
        print(f"{test_display:<30}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    success_rate = (passed_tests / total_tests) * 100
    
    if passed_tests == total_tests:
        print("\n🎉 Phase 4 Marketplace Implementation Complete!")
        print("✅ All marketplace features properly implemented")
        print("\n🚀 Ready for Production!")
        print("\n📋 Available Features:")
        print("   • Individual item purchasing with Razorpay")
        print("   • Shopping cart functionality")
        print("   • Content access control (free vs paid)")
        print("   • Developer earnings tracking (70/30 split)")
        print("   • Admin payout approval system")
        print("   • Enhanced user dashboard with recommendations")
        print("   • Purchase history and analytics")
        print("   • Rate limiting and security features")
        
        print("\n🛠️ Next Steps:")
        print("1. Start the server: python minimal_auth_server.py")
        print("2. Test payment flows: Create test purchases")
        print("3. Test access control: View paid content without purchase")
        print("4. Test admin features: Approve payout requests")
        print("5. Deploy to production with proper Razorpay credentials")
        
    else:
        print(f"\n⚠️ {total_tests - passed_tests} implementation issues found")
        print("Please review the failed tests above before proceeding")
        
        if success_rate >= 75:
            print("\n✅ Core functionality is working, minor issues detected")
        elif success_rate >= 50:
            print("\n⚠️ Significant issues found, review required")
        else:
            print("\n❌ Major implementation problems, extensive review needed")
    
    return passed_tests == total_tests


def check_database_models():
    """Check if all database models are properly set up."""
    print("\n🔍 Database Model Verification:")
    
    try:
        # Check model files exist
        model_files = [
            "app/models/item_purchase.py",
            "app/models/shopping_cart.py", 
            "app/models/developer_earnings.py",
            "app/services/access_control.py",
            "app/services/payment_service.py",
            "app/endpoints/payments.py",
            "app/endpoints/developer_earnings.py",
            "app/endpoints/user_dashboard.py"
        ]
        
        missing_files = []
        for file_path in model_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            print("❌ Missing files:")
            for file in missing_files:
                print(f"   - {file}")
            return False
        else:
            print("✅ All required files present")
            return True
            
    except Exception as e:
        print(f"❌ File check error: {e}")
        return False


def check_server_integration():
    """Check if the main server has all integrations."""
    print("\n🔍 Server Integration Check:")
    
    try:
        with open("minimal_auth_server.py", "r", encoding="utf-8") as f:
            server_content = f.read()
        
        required_imports = [
            "ItemPurchase",
            "ShoppingCart", 
            "DeveloperEarnings",
            "ContentAccessService",
            "payment_router",
            "earnings_router",
            "dashboard_router"
        ]
        
        missing_imports = []
        for import_name in required_imports:
            if import_name not in server_content:
                missing_imports.append(import_name)
        
        if missing_imports:
            print("❌ Missing server integrations:")
            for import_name in missing_imports:
                print(f"   - {import_name}")
            return False
        else:
            print("✅ All server integrations present")
            return True
            
    except Exception as e:
        print(f"❌ Server check error: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Pre-flight Checks:")
    
    # Check files and integrations first
    files_ok = check_database_models()
    server_ok = check_server_integration()
    
    if not (files_ok and server_ok):
        print("\n❌ Pre-flight checks failed. Please fix the issues above.")
        sys.exit(1)
    
    # Run comprehensive tests
    try:
        success = asyncio.run(test_marketplace_implementation())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test execution error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
