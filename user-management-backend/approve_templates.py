#!/usr/bin/env python3
"""
Approve all templates
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def approve_templates():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.user_management_db
    
    # Update all templates to be approved
    result = await db.templates.update_many(
        {},  # Empty filter matches all documents
        {"$set": {"status": "approved"}}
    )
    
    print(f"Updated {result.modified_count} templates to approved status")
    
    # Verify
    templates = await db.templates.find({}).to_list(None)
    print(f"Found {len(templates)} templates after update:")
    for t in templates:
        title = t.get('title', 'Unknown')
        status = t.get('status', 'None')
        active = t.get('is_active', 'None')
        print(f"- {title} - Status: {status} - Active: {active}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(approve_templates())
