"""
Simple: Create developer account and template using existing API
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def main():
    print("\n" + "="*70)
    print("  TEMPLATE CREATION DEMO")
    print("="*70 + "\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Step 1: Register developer
        print("Step 1: Creating developer account...")
        email = "dev@example.com"
        password = "Pass123!"
        
        response = await client.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": password,
            "username": "developer"
        })
        
        if response.status_code == 200:
            print(f"   Created: {email}")
        else:
            print(f"   Already exists (continuing...)")
        
        # Step 2: Login
        print("\nStep 2: Logging in...")
        response = await client.post(f"{BASE_URL}/api/auth/login", data={
            "username": email,
            "password": password
        })
        
        if response.status_code != 200:
            print(f"   ERROR: {response.text}")
            return
        
        token = response.json()["access_token"]
        print(f"   Logged in")
        
        # Step 3: Try creating template (will fail - need developer role)
        print("\nStep 3: Testing template creation...")
        headers = {"Authorization": f"Bearer {token}"}
        
        template = {
            "title": "React Dashboard Pro",
            "category": "Dashboard",
            "type": "React",
            "language": "TypeScript",
            "difficulty_level": "Medium",
            "plan_type": "Free",
            "pricing_inr": 0,
            "pricing_usd": 0,
            "short_description": "Professional React dashboard",
            "full_description": "Complete dashboard solution",
            "developer_name": "Dev User",
            "developer_experience": "5+ years"
        }
        
        response = await client.post(
            f"{BASE_URL}/api/templates/",
            json=template,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 403:
            print("\n" + "="*70)
            print("  TO CREATE TEMPLATES:")
            print("="*70)
            print("\n1. User needs 'developer' role")
            print("\n2. Upgrade user role in MongoDB:")
            print(f"\n   MongoDB Shell:")
            print(f"   ```")
            print(f"   use user_management")
            print(f"   db.users.updateOne(")
            print(f"     {{ email: '{email}' }},")
            print(f"     {{ $set: {{ role: 'developer' }} }}")
            print(f"   )")
            print(f"   ```")
            print(f"\n3. Or using Python:")
            print(f"   ```python")
            print(f"   from motor.motor_asyncio import AsyncIOMotorClient")
            print(f"   client = AsyncIOMotorClient('mongodb://localhost:27017')")
            print(f"   db = client['user_management']")
            print(f"   await db.users.update_one(")
            print(f"       {{'email': '{email}'}},")
            print(f"       {{'$set': {{'role': 'developer'}}}}")
            print(f"   )")
            print(f"   ```")
            print(f"\n4. Then login again and create template")
            print("\n" + "="*70)
            
            # Create upgrade script
            script = f"""# Run this to upgrade user to developer
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def upgrade():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['user_management']
    result = await db.users.update_one(
        {{'email': '{email}'}},
        {{'$set': {{'role': 'developer'}}}}
    )
    print(f'Updated {{result.modified_count}} user(s)')
    user = await db.users.find_one({{'email': '{email}'}})
    print(f'Role is now: {{user.get("role", "user")}}')
    client.close()

asyncio.run(upgrade())
"""
            with open("upgrade_to_developer.py", "w", encoding="utf-8") as f:
                f.write(script)
            
            print(f"\nCreated: upgrade_to_developer.py")
            print(f"Run: python upgrade_to_developer.py")

if __name__ == "__main__":
    asyncio.run(main())
