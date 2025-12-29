import asyncio
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os

# Database configuration
MONGO_URL = "mongodb://mongo:27017" # Assuming standard docker networking or localhost if exposed
# Since we are running from host, we might need localhost if ports are mapped.
# The backend uses 'mongodb' hostname. From host, it's likely localhost:27017.
MONGO_URL_HOST = "mongodb://localhost:27017"
DB_NAME = "user_management_db"

async def verify():
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGO_URL_HOST)
    db = client[DB_NAME]
    
    # 1. Verify Component Fix
    print("\n--- Verifying Component Fix ---")
    component_id = ObjectId()
    component_data = {
        "_id": component_id,
        "title": "Verification Component",
        "description": "Created to verify backend fix",
        "code": "<div>Test</div>",
        "user_id": ObjectId(),
        "is_active": True,
        "settings": {},
        "category": "Buttons",
        "type": "React",
        "framework": "React",
        "styling": "Tailwind",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }
    
    await db.components.insert_one(component_data)
    print(f"Inserted test component with ID: {component_id}")
    
    async with httpx.AsyncClient() as http:
        try:
            response = await http.get(f"http://localhost:8000/api/components/{str(component_id)}")
            if response.status_code == 200:
                data = response.json()
                returned_id = data.get("id") or data.get("_id")
                print(f"API Response Status: {response.status_code}")
                print(f"API Returned ID: {returned_id}")
                
                if str(returned_id) == str(component_id):
                    print("✅ Component API Success: Returned correct component.")
                else:
                    print(f"❌ Component API Failed: ID Mismatch! Expected {component_id}, got {returned_id}")
            else:
                print(f"❌ Component API Failed: Status {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Component API Request Error: {e}")
            
    # Cleanup component
    await db.components.delete_one({"_id": component_id})

    # 2. Verify Template Fix
    print("\n--- Verifying Template Fix ---")
    template_id = ObjectId()
    template_data = {
        "_id": template_id,
        "title": "Verification Template",
        "short_description": "Created to verify backend fix",
        "user_id": ObjectId(),
        "is_active": True,
        "category": "Dashboard",
        "type": "Admin",
        "plan_type": "Free",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }
    
    await db.templates.insert_one(template_data)
    print(f"Inserted test template with ID: {template_id}")
    
    async with httpx.AsyncClient() as http:
        try:
            response = await http.get(f"http://localhost:8000/api/templates/{str(template_id)}")
            if response.status_code == 200:
                data = response.json()
                # Check if it's the old hardcoded response
                if "git_repo_url" in data and "test_field" in data and "template" not in data:
                     print("❌ Template API Failed: Returned hardcoded test response!")
                else:
                    # New response structure has "template" key
                    template_info = data.get("template", data)
                    returned_id = template_info.get("id") or template_info.get("_id")
                    print(f"API Response Status: {response.status_code}")
                    print(f"API Returned ID: {returned_id}")
                    
                    if str(returned_id) == str(template_id):
                        print("✅ Template API Success: Returned correct template.")
                    else:
                         print(f"❌ Template API Failed: ID Mismatch! Expected {template_id}, got {returned_id}")
            else:
                print(f"❌ Template API Failed: Status {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Template API Request Error: {e}")

    # Cleanup template
    await db.templates.delete_one({"_id": template_id})

if __name__ == "__main__":
    asyncio.run(verify())
