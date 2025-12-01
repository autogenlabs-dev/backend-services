"""
Clear all templates and components from the database

Usage:
    python clear_database.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.template import Template
from app.models.component import Component
from app.models.user import User
from app.config import settings


async def clear_all():
    """Clear all templates and components from database"""
    
    print("🗑️  Starting database clear...")
    print(f"📦 Database: {settings.database_url.split('@')[-1]}")
    
    # Connect to database
    client = AsyncIOMotorClient(settings.database_url)
    database = client["user_management_db"]
    
    # Initialize Beanie
    await init_beanie(database=database, document_models=[Template, Component, User])
    print("✅ Database connected\n")
    
    # Confirm before deleting
    print("⚠️  WARNING: This will delete ALL templates and components!")
    response = input("Type 'yes' to confirm: ")
    
    if response.lower() != 'yes':
        print("❌ Cancelled")
        client.close()
        return
    
    print("\n🗑️  Deleting...")
    
    # Delete all templates
    template_result = await Template.find({}).delete()
    print(f"✅ Deleted {template_result.deleted_count} templates")
    
    # Delete all components
    component_result = await Component.find({}).delete()
    print(f"✅ Deleted {component_result.deleted_count} components")
    
    # Verify
    template_count = await Template.find({}).count()
    component_count = await Component.find({}).count()
    
    print("\n📊 Database is now empty:")
    print(f"  - Templates: {template_count}")
    print(f"  - Components: {component_count}")
    
    client.close()
    print("\n✅ Database cleared successfully!")
    print("\n💡 You can now create your own templates and components via:")
    print("   - Web UI: http://localhost:3000/templates/create")
    print("   - Web UI: http://localhost:3000/components/create")


if __name__ == "__main__":
    asyncio.run(clear_all())
