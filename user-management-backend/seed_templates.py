"""
Seed templates into MongoDB for testing
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId

# MongoDB connection
DATABASE_URL = "mongodb+srv://autogencodebuilder:DataOnline@autogen.jf0j0.mongodb.net/user_management_db?retryWrites=true&w=majority&connectTimeoutMS=60000&socketTimeoutMS=60000"

async def seed_templates():
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client.user_management_db
    
    # Sample templates
    templates = [
        {
            "_id": ObjectId(),
            "title": "Modern Dashboard Template",
            "category": "Dashboard",
            "type": "React Component",
            "language": "JavaScript",
            "difficulty_level": "Intermediate",
            "plan_type": "Free",
            "short_description": "A modern, responsive dashboard with charts and analytics",
            "full_description": "Complete dashboard template with data visualization, user management, and real-time updates. Built with React, Tailwind CSS, and Chart.js.",
            "preview_images": [],
            "git_repo_url": "https://github.com/example/dashboard",
            "live_demo_url": "https://example.com/dashboard-demo",
            "dependencies": ["react", "tailwindcss", "chart.js", "framer-motion"],
            "tags": ["dashboard", "analytics", "charts", "admin"],
            "developer_name": "AutogenLabs",
            "developer_experience": "5 years",
            "is_available_for_dev": True,
            "featured": True,
            "user_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "status": "published",
            "approval_status": "approved",
            "approved_at": datetime.utcnow(),
            "rating": 4.8,
            "downloads": 1250,
            "views": 5420,
            "likes": 342
        },
        {
            "_id": ObjectId(),
            "title": "E-commerce Landing Page",
            "category": "Landing Page",
            "type": "Next.js Template",
            "language": "TypeScript",
            "difficulty_level": "Beginner",
            "plan_type": "Free",
            "short_description": "Beautiful e-commerce landing page with product showcase",
            "full_description": "Fully responsive e-commerce landing page template with hero section, product grid, testimonials, and newsletter signup. Optimized for conversions.",
            "preview_images": [],
            "git_repo_url": "https://github.com/example/ecommerce-landing",
            "live_demo_url": "https://example.com/ecommerce-demo",
            "dependencies": ["next", "typescript", "tailwindcss"],
            "tags": ["ecommerce", "landing", "shop", "products"],
            "developer_name": "AutogenLabs",
            "developer_experience": "4 years",
            "is_available_for_dev": True,
            "featured": True,
            "user_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "status": "published",
            "approval_status": "approved",
            "approved_at": datetime.utcnow(),
            "rating": 4.6,
            "downloads": 890,
            "views": 3200,
            "likes": 215
        },
        {
            "_id": ObjectId(),
            "title": "SaaS Application Template",
            "category": "SaaS",
            "type": "Full Stack",
            "language": "TypeScript",
            "difficulty_level": "Advanced",
            "plan_type": "Paid",
            "short_description": "Complete SaaS application with authentication and billing",
            "full_description": "Production-ready SaaS template with user authentication, subscription billing, admin dashboard, and API integration. Includes Stripe integration.",
            "preview_images": [],
            "git_repo_url": "https://github.com/example/saas-template",
            "live_demo_url": "https://example.com/saas-demo",
            "dependencies": ["next", "typescript", "prisma", "stripe", "clerk"],
            "tags": ["saas", "authentication", "billing", "stripe"],
            "developer_name": "AutogenLabs",
            "developer_experience": "7 years",
            "is_available_for_dev": True,
            "featured": True,
            "user_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "status": "published",
            "approval_status": "approved",
            "approved_at": datetime.utcnow(),
            "rating": 4.9,
            "downloads": 567,
            "views": 2100,
            "likes": 189
        },
        {
            "_id": ObjectId(),
            "title": "Portfolio Website Template",
            "category": "Portfolio",
            "type": "Static Site",
            "language": "JavaScript",
            "difficulty_level": "Beginner",
            "plan_type": "Free",
            "short_description": "Clean and modern portfolio template for developers",
            "full_description": "Minimalist portfolio template perfect for showcasing your projects and skills. Includes project gallery, about section, and contact form.",
            "preview_images": [],
            "git_repo_url": "https://github.com/example/portfolio",
            "live_demo_url": "https://example.com/portfolio-demo",
            "dependencies": ["react", "tailwindcss", "framer-motion"],
            "tags": ["portfolio", "personal", "showcase", "developer"],
            "developer_name": "AutogenLabs",
            "developer_experience": "3 years",
            "is_available_for_dev": True,
            "featured": False,
            "user_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "status": "published",
            "approval_status": "approved",
            "approved_at": datetime.utcnow(),
            "rating": 4.5,
            "downloads": 1100,
            "views": 4200,
            "likes": 298
        },
        {
            "_id": ObjectId(),
            "title": "Blog Platform Template",
            "category": "Blog",
            "type": "Next.js Template",
            "language": "TypeScript",
            "difficulty_level": "Intermediate",
            "plan_type": "Free",
            "short_description": "Full-featured blog platform with MDX support",
            "full_description": "Modern blog template with MDX support, syntax highlighting, dark mode, and SEO optimization. Perfect for technical blogs and documentation.",
            "preview_images": [],
            "git_repo_url": "https://github.com/example/blog-platform",
            "live_demo_url": "https://example.com/blog-demo",
            "dependencies": ["next", "mdx", "typescript", "tailwindcss"],
            "tags": ["blog", "mdx", "content", "seo"],
            "developer_name": "AutogenLabs",
            "developer_experience": "5 years",
            "is_available_for_dev": True,
            "featured": False,
            "user_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "status": "published",
            "approval_status": "approved",
            "approved_at": datetime.utcnow(),
            "rating": 4.7,
            "downloads": 745,
            "views": 2800,
            "likes": 167
        }
    ]
    
    # Clear existing templates
    result = await db.templates.delete_many({})
    print(f"🗑️  Deleted {result.deleted_count} existing templates")
    
    # Insert new templates
    result = await db.templates.insert_many(templates)
    print(f"✅ Inserted {len(result.inserted_ids)} templates")
    
    # Verify
    count = await db.templates.count_documents({})
    print(f"📊 Total templates in DB: {count}")
    
    # Show templates
    cursor = db.templates.find({}, {"title": 1, "category": 1, "plan_type": 1})
    print("\n📋 Templates:")
    async for template in cursor:
        print(f"  - {template['title']} ({template['category']}, {template['plan_type']})")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_templates())
