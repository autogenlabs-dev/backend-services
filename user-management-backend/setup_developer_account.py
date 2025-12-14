"""
Create a test developer account and demonstrate template creation
"""

import asyncio
import httpx
from datetime import datetime
import json

BASE_URL = "http://localhost:8000"

async def create_developer_and_template():
    """Create developer account, upgrade role, and create template"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        print("\n🔧 Creating Developer Account...")
        
        # Step 1: Create a user account directly with MongoDB
        # For testing, we'll use the admin API to create a developer
        
        # First, create and login as regular user
        email = "testdev@example.com"
        register_data = {
            "email": email,
            "password": "DevPass123!",
            "username": "testdev"
        }
        
        print(f"📝 Registering: {email}")
        response = await client.post(f"{BASE_URL}/api/auth/register", json=register_data)
        
        if response.status_code == 200:
            print(f"✅ User registered")
        else:
            print(f"⚠️  User might exist: {response.status_code}")
        
        # Login
        login_data = {
            "username": email,
            "password": "DevPass123!"
        }
        
        print(f"🔐 Logging in...")
        response = await client.post(f"{BASE_URL}/api/auth/login", data=login_data)
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return
        
        auth_data = response.json()
        jwt_token = auth_data["access_token"]
        user_info = auth_data.get("user", {})
        user_id = user_info.get("id")
        
        print(f"✅ Logged in as: {email}")
        print(f"📋 User ID: {user_id}")
        print(f"👤 Current Role: {user_info.get('role', 'user')}")
        
        # For this demo, we need to manually update the user role in MongoDB
        # In production, this would be done via admin panel
        print(f"\n⚠️  Manual Step Required:")
        print(f"Run this command to upgrade user to developer:")
        print(f"\nPython:")
        print(f"```python")
        print(f"# upgrade_user_role.py")
        print(f"import asyncio")
        print(f"from motor.motor_asyncio import AsyncIOMotorClient")
        print(f"from bson import ObjectId")
        print(f"")
        print(f"async def upgrade_role():")
        print(f"    client = AsyncIOMotorClient('mongodb://localhost:27017')")
        print(f"    db = client['user_management']")
        print(f"    await db.users.update_one(")
        print(f"        {{'_id': ObjectId('{user_id}')}},")
        print(f"        {{'$set': {{'role': 'developer'}}}}")
        print(f"    )")
        print(f"    print('✅ User upgraded to developer')")
        print(f"    client.close()")
        print(f"")
        print(f"asyncio.run(upgrade_role())")
        print(f"```")
        print(f"\nOr MongoDB Shell:")
        print(f"```bash")
        print(f"mongo user_management")
        print(f"db.users.updateOne(")
        print(f"  {{ _id: ObjectId('{user_id}') }},")
        print(f"  {{ $set: {{ role: 'developer' }} }}")
        print(f")")
        print(f"```")
        
        # Create upgrade script file
        upgrade_script = f"""import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def upgrade_role():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['user_management']
    
    result = await db.users.update_one(
        {{'_id': ObjectId('{user_id}')}},
        {{'$set': {{'role': 'developer'}}}}
    )
    
    if result.modified_count > 0:
        print('✅ User upgraded to developer role')
    else:
        print('⚠️  User already has developer role or not found')
    
    # Verify
    user = await db.users.find_one({{'_id': ObjectId('{user_id}')}})
    print(f'Current role: {{user.get("role", "user")}}')
    
    client.close()

if __name__ == "__main__":
    asyncio.run(upgrade_role())
"""
        
        with open("upgrade_user_to_developer.py", "w") as f:
            f.write(upgrade_script)
        
        print(f"\n✅ Created: upgrade_user_to_developer.py")
        print(f"Run: python upgrade_user_to_developer.py")
        
        # Show template creation example
        print(f"\n📝 After upgrading to developer, use this code to create template:")
        print(f"\n```python")
        print(f"# create_template_example.py")
        print(f"import asyncio")
        print(f"import httpx")
        print(f"")
        print(f"async def create_template():")
        print(f"    async with httpx.AsyncClient() as client:")
        print(f"        # Login")
        print(f"        response = await client.post(")
        print(f"            '{BASE_URL}/api/auth/login',")
        print(f"            data={{'username': '{email}', 'password': 'DevPass123!'}}")
        print(f"        )")
        print(f"        token = response.json()['access_token']")
        print(f"        ")
        print(f"        # Create template")
        print(f"        headers = {{'Authorization': f'Bearer {{token}}'}}")
        print(f"        template = {{")
        print(f"            'title': 'Modern React Dashboard',")
        print(f"            'category': 'Dashboard',")
        print(f"            'type': 'React',")
        print(f"            'language': 'TypeScript',")
        print(f"            'difficulty_level': 'Medium',")
        print(f"            'plan_type': 'Free',")
        print(f"            'pricing_inr': 0,")
        print(f"            'pricing_usd': 0,")
        print(f"            'short_description': 'Professional React dashboard',")
        print(f"            'full_description': 'Complete dashboard with charts',")
        print(f"            'git_repo_url': 'https://github.com/example/dashboard',")
        print(f"            'live_demo_url': 'https://demo.example.com',")
        print(f"            'dependencies': ['react', 'typescript', 'tailwindcss'],")
        print(f"            'tags': ['dashboard', 'admin', 'charts'],")
        print(f"            'developer_name': 'Test Developer',")
        print(f"            'developer_experience': '5+ years',")
        print(f"        }}")
        print(f"        ")
        print(f"        response = await client.post(")
        print(f"            '{BASE_URL}/api/templates/',")
        print(f"            json=template,")
        print(f"            headers=headers")
        print(f"        )")
        print(f"        print(response.json())")
        print(f"")
        print(f"asyncio.run(create_template())")
        print(f"```")
        
        return user_id, jwt_token

if __name__ == "__main__":
    asyncio.run(create_developer_and_template())
