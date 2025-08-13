#!/usr/bin/env python3
"""
Test script to verify the fixes for template status and admin dashboard issues.
"""

import asyncio
import json
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_fixes():
    """Test all the fixes we implemented"""
    print("🧪 Testing Template and Component Fixes")
    print("=" * 50)
    
    try:
        from app.models.template import Template, ContentStatus
        from app.models.component import Component
        from app.models.user import User
        from motor.motor_asyncio import AsyncIOMotorClient
        from beanie import init_beanie
        from app.config import settings
        
        # Initialize database connection
        print("🔄 Connecting to database...")
        client = AsyncIOMotorClient(settings.database_url)
        db = client.user_management_db
        
        # Initialize Beanie
        print("🔄 Initializing Beanie...")
        await init_beanie(database=db, document_models=[User, Template, Component])
        
        # Test 1: Check Template model status property
        print("\n1. Testing Template model status property...")
        try:
            # Find a template
            template = await Template.find_one()
            if template:
                print(f"   ✅ Template found: {template.title}")
                print(f"   ✅ approval_status: {template.approval_status}")
                print(f"   ✅ status property: {template.status}")
                print(f"   ✅ to_dict() contains status: {'status' in template.to_dict()}")
                # Check the actual values in to_dict
                template_dict = template.to_dict()
                print(f"   📄 to_dict status value: {template_dict.get('status')}")
                print(f"   📄 to_dict approval_status value: {template_dict.get('approval_status')}")
            else:
                print("   ⚠️  No templates found")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Check Component model status property
        print("\n2. Testing Component model status property...")
        try:
            # Find a component
            component = await Component.find_one()
            if component:
                print(f"   ✅ Component found: {component.title}")
                print(f"   ✅ approval_status: {component.approval_status}")
                print(f"   ✅ status property: {component.status}")
                print(f"   ✅ to_dict() contains status: {'status' in component.to_dict()}")
                # Check the actual values in to_dict
                component_dict = component.to_dict()
                print(f"   📄 to_dict status value: {component_dict.get('status')}")
                print(f"   📄 to_dict approval_status value: {component_dict.get('approval_status')}")
            else:
                print("   ⚠️  No components found")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Count content by status
        print("\n3. Testing content counts by status...")
        try:
            # Count templates by status
            total_templates = await Template.find().count()
            pending_templates = await Template.find(Template.approval_status == ContentStatus.PENDING_APPROVAL).count()
            approved_templates = await Template.find(Template.approval_status == ContentStatus.APPROVED).count()
            
            print(f"   📊 Total Templates: {total_templates}")
            print(f"   📊 Pending Templates: {pending_templates}")
            print(f"   📊 Approved Templates: {approved_templates}")
            
            # Count components by status
            total_components = await Component.find().count()
            pending_components = await Component.find(Component.approval_status == ContentStatus.PENDING_APPROVAL).count()
            approved_components = await Component.find(Component.approval_status == ContentStatus.APPROVED).count()
            
            print(f"   📊 Total Components: {total_components}")
            print(f"   📊 Pending Components: {pending_components}")
            print(f"   📊 Approved Components: {approved_components}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the backend directory with proper environment setup")
    
    print("\n" + "=" * 50)
    print("🎉 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_fixes())
