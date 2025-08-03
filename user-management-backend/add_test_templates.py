#!/usr/bin/env python3
"""
Add Test Templates to Database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId

# Database connection
DATABASE_URL = "mongodb://localhost:27017"

async def add_test_templates():
    """Add test templates with live URLs"""
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client.user_management_db
    templates_collection = db.templates
    
    # Clear existing templates first
    await templates_collection.delete_many({})
    print("🗑️ Cleared existing templates")
    
    # Sample templates with real live URLs
    test_templates = [
        {
            "_id": ObjectId(),
            "title": "NextJS Official Website",
            "category": "Navigation",
            "type": "React",
            "language": "TypeScript",
            "difficulty_level": "Easy",
            "plan_type": "Free",
            "pricing_inr": 0,
            "pricing_usd": 0,
            "rating": 4.8,
            "downloads": 1250,
            "views": 3400,
            "likes": 89,
            "short_description": "Official NextJS website with modern navigation",
            "full_description": "This is the official NextJS website showcasing modern navigation patterns and design.",
            "live_demo_url": "https://nextjs.org",
            "git_repo_url": "https://github.com/vercel/next.js",
            "dependencies": ["react", "next"],
            "tags": ["nextjs", "react", "website"],
            "developer_name": "Vercel Team",
            "developer_experience": "10+ years",
            "is_available_for_dev": True,
            "featured": True,
            "popular": True,
            "user_id": ObjectId("507f1f77bcf86cd799439011"),
            "code": "// NextJS Sample Code",
            "readme_content": "# NextJS Official Website",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "title": "TailwindCSS Documentation",
            "category": "Layout",
            "type": "HTML/CSS",
            "language": "CSS",
            "difficulty_level": "Medium",
            "plan_type": "Free",
            "pricing_inr": 0,
            "pricing_usd": 0,
            "rating": 4.9,
            "downloads": 890,
            "views": 2100,
            "likes": 156,
            "short_description": "TailwindCSS official documentation site",
            "full_description": "The official TailwindCSS documentation showcasing modern CSS framework design patterns.",
            "live_demo_url": "https://tailwindcss.com",
            "git_repo_url": "https://github.com/tailwindlabs/tailwindcss",
            "dependencies": ["tailwindcss"],
            "tags": ["css", "tailwind", "documentation"],
            "developer_name": "Tailwind Labs",
            "developer_experience": "8+ years",
            "is_available_for_dev": True,
            "featured": True,
            "popular": False,
            "user_id": ObjectId("507f1f77bcf86cd799439011"),
            "code": "/* TailwindCSS Sample */",
            "readme_content": "# TailwindCSS Documentation",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "title": "React Official Documentation",
            "category": "User Interface",
            "type": "React",
            "language": "JavaScript",
            "difficulty_level": "Easy",
            "plan_type": "Free",
            "pricing_inr": 0,
            "pricing_usd": 0,
            "rating": 4.7,
            "downloads": 2100,
            "views": 5600,
            "likes": 203,
            "short_description": "React official documentation and examples",
            "full_description": "The official React documentation site with comprehensive examples and tutorials.",
            "live_demo_url": "https://react.dev",
            "git_repo_url": "https://github.com/facebook/react",
            "dependencies": ["react"],
            "tags": ["react", "javascript", "documentation"],
            "developer_name": "Meta Team",
            "developer_experience": "10+ years",
            "is_available_for_dev": True,
            "featured": False,
            "popular": True,
            "user_id": ObjectId("507f1f77bcf86cd799439011"),
            "code": "// React Sample Code",
            "readme_content": "# React Documentation",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insert test templates
    result = await templates_collection.insert_many(test_templates)
    print(f"✅ Added {len(result.inserted_ids)} test templates to database")
    
    # Verify templates were added
    count = await templates_collection.count_documents({})
    print(f"📊 Total templates in database: {count}")
    
    # List all templates with their live URLs
    templates = await templates_collection.find({}).to_list(None)
    for i, template in enumerate(templates, 1):
        print(f"\n🔍 Template {i}:")
        print(f"   Title: {template.get('title')}")
        print(f"   Live URL: {template.get('live_demo_url')}")
        print(f"   Category: {template.get('category')}")
    
    await client.close()
    print("\n🎉 Test templates added successfully!")

if __name__ == "__main__":
    asyncio.run(add_test_templates())
