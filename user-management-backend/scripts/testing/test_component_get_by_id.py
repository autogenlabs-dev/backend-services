#!/usr/bin/env python3
"""
Test script to verify the Component.get() method is correctly querying by ID.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from beanie import init_beanie, PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.component import Component
from app.config import settings

async def test_component_query():
    """Test if Component.get() correctly queries by ID"""
    
    # Initialize database connection
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.DATABASE_NAME]
    
    # Initialize Beanie
    await init_beanie(database=database, document_models=[Component])
    
    # Test ID from user's report
    test_id = "69244197cc1af6f2acdbbbd4"
    
    print(f"Testing component query with ID: {test_id}")
    print("="*80)
    
    # Validate ID
    if not PydanticObjectId.is_valid(test_id):
        print(f"❌ Invalid ID format: {test_id}")
        return
    
    print(f"✅ ID format is valid")
    
    # Convert to ObjectId
    object_id = PydanticObjectId(test_id)
    print(f"📝 Converted to ObjectId: {object_id}")
    
    # Method 1: Using Component.get() (what the API uses)
    print("\n" + "="*80)
    print("METHOD 1: Component.get()")
    print("="*80)
    component1 = await Component.get(object_id)
    
    if component1:
        print(f"✅ Found component:")
        print(f"   ID: {component1.id}")
        print(f"   Title: {component1.title}")
        print(f"   Category: {component1.category}")
        print(f"   Type: {component1.type}")
        print(f"   Language: {component1.language}")
    else:
        print(f"❌ Component not found with Component.get()")
    
    # Method 2: Using direct MongoDB query to verify
    print("\n" + "="*80)
    print("METHOD 2: Direct MongoDB find_one()")
    print("="*80)
    raw_doc = await database.components.find_one({"_id": object_id})
    
    if raw_doc:
        print(f"✅ Found document in MongoDB:")
        print(f"   _id: {raw_doc.get('_id')}")
        print(f"   Title: {raw_doc.get('title')}")
        print(f"   Category: {raw_doc.get('category')}")
        print(f"   Type: {raw_doc.get('type')}")
        print(f"   Language: {raw_doc.get('language')}")
    else:
        print(f"❌ Document not found in MongoDB")
    
    # Method 3: Check if ID exists at all
    print("\n" + "="*80)
    print("METHOD 3: List all components to verify ID exists")
    print("="*80)
    all_components = await Component.find_all().to_list()
    print(f"Total components in database: {len(all_components)}")
    
    found_match = False
    for comp in all_components:
        if str(comp.id) == test_id:
            found_match = True
            print(f"\n✅ FOUND MATCH in component list:")
            print(f"   ID: {comp.id}")
            print(f"   Title: {comp.title}")
            print(f"   Category: {comp.category}")
            print(f"   Type: {comp.type}")
            break
    
    if not found_match:
        print(f"\n❌ ID {test_id} does not exist in database")
        print("\nFirst 5 component IDs in database:")
        for i, comp in enumerate(all_components[:5]):
            print(f"   {i+1}. {comp.id} - {comp.title}")
    
    # Method 4: Check what Component.get() returns if we query wrong ID
    print("\n" + "="*80)
    print("METHOD 4: Testing if Component.get() has any caching issues")
    print("="*80)
    
    # Query twice to see if results are consistent
    comp_query1 = await Component.get(object_id)
    comp_query2 = await Component.get(object_id)
    
    if comp_query1 and comp_query2:
        if comp_query1.id == comp_query2.id:
            print(f"✅ Queries are consistent")
        else:
            print(f"❌ INCONSISTENT QUERIES!")
            print(f"   First query: {comp_query1.id} - {comp_query1.title}")
            print(f"   Second query: {comp_query2.id} - {comp_query2.title}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_component_query())
