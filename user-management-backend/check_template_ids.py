#!/usr/bin/env python3
"""
Check template IDs
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_template_ids():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.user_management_db
    templates = await db.templates.find({}).to_list(None)
    print(f"Found {len(templates)} templates:")
    for t in templates:
        _id = str(t.get('_id'))
        title = t.get('title')
        print(f"ID: {_id}, Title: {title}")
    client.close()

if __name__ == "__main__":
    asyncio.run(check_template_ids())
