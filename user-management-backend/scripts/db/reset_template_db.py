#!/usr/bin/env python3
"""
Reset Template Database Collections
This script drops all template-related collections to resolve index conflicts.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def reset_template_collections():
    """Drop all template-related collections"""
    client = AsyncIOMotorClient(settings.database_url)
    db = client.user_management_db
    
    collections_to_drop = [
        "templates",
        "template_likes",
        "template_downloads", 
        "template_views",
        "template_comments",
        "template_categories"
    ]
    
    print("Dropping template collections...")
    for collection_name in collections_to_drop:
        try:
            await db.drop_collection(collection_name)
            print(f"✓ Dropped {collection_name}")
        except Exception as e:
            print(f"! Failed to drop {collection_name}: {e}")
    
    print("Template collections reset complete!")
    await client.close()

if __name__ == "__main__":
    asyncio.run(reset_template_collections())
