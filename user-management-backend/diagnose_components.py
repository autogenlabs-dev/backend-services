"""
Diagnostic script to check components in the database
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.component import Component
from app.config import settings


async def diagnose():
    print("🔍 Connecting to database...")
    client = AsyncIOMotorClient(settings.database_url)
    database = client["user_management_db"]
    
    await init_beanie(database=database, document_models=[Component])
    print("✅ Connected\n")
    
    # Total components
    total = await Component.find().count()
    print(f"📊 Total components in collection: {total}")
    
    # Active components
    active = await Component.find({"is_active": True}).count()
    print(f"📊 Active components (is_active=True): {active}")
    
    # Inactive components
    inactive = await Component.find({"is_active": False}).count()
    print(f"📊 Inactive components (is_active=False): {inactive}")
    
    # Components with missing is_active field
    missing_active = await Component.find({"is_active": {"$exists": False}}).count()
    print(f"📊 Components without is_active field: {missing_active}")
    
    # Show first few components with details
    print("\n🔍 First 3 components in database:")
    components = await Component.find().limit(3).to_list()
    for i, comp in enumerate(components, 1):
        print(f"\n  Component {i}:")
        print(f"    ID: {comp.id}")
        print(f"    Title: {comp.title}")
        print(f"    Category: {comp.category}")
        print(f"    is_active: {comp.is_active}")
        print(f"    approval_status: {comp.approval_status}")
    
    # Test the exact query from the API
    print("\n🔍 Testing API query filter: {'is_active': True}")
    api_results = await Component.find({"is_active": True}).to_list()
    print(f"  Results: {len(api_results)} components")
    if api_results:
        print(f"  First result: {api_results[0].title}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(diagnose())
