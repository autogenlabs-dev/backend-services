#!/usr/bin/env python3
"""
Check Templates in Database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def check_templates():
    """Check what templates are in the database"""
    client = AsyncIOMotorClient(settings.database_url)
    db = client.user_management_db
    templates_collection = db.templates
    
    # Get all templates
    templates = await templates_collection.find({}).to_list(None)
    
    print(f'📊 Total templates in database: {len(templates)}')
    
    for i, template in enumerate(templates, 1):
        print(f'\n🔍 Template {i}:')
        print(f'   Title: {template.get("title", "N/A")}')
        print(f'   Live Demo URL: {template.get("live_demo_url", "N/A")}')
        print(f'   Category: {template.get("category", "N/A")}')
        print(f'   ID: {template.get("_id", "N/A")}')
        print(f'   Plan Type: {template.get("plan_type", "N/A")}')
        print(f'   Developer: {template.get("developer_name", "N/A")}')
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(check_templates())
