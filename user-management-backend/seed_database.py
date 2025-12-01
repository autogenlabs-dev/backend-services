"""
All-in-One Database Seed Script
Seeds both templates and components with realistic data

Usage:
    python seed_database.py
    python seed_database.py --clear  # Clear existing data first
"""

import asyncio
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone
from bson import ObjectId

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.template import Template, ContentStatus as TemplateStatus
from app.models.component import Component, ContentStatus as ComponentStatus
from app.models.user import User
from app.config import settings


async def seed_all(clear_existing=False):
    """Seed the database with templates and components"""
    
    print("🚀 Starting database seed...")
    print(f"📦 Database: {settings.database_url.split('@')[-1]}")
    
    # Connect to database
    client = AsyncIOMotorClient(settings.database_url)
    database = client["user_management_db"]
    
    # Initialize Beanie
    await init_beanie(database=database, document_models=[Template, Component, User])
    print("✅ Database connected\n")
    
    # Get or create default user
    default_user = await User.find_one({})
    if default_user:
        user_id = default_user.id
        print(f"👤 Using user: {default_user.email}")
    else:
        print("⚠️  No users found - creating without user_id")
        user_id = None
    
    # ========== TEMPLATES ==========
    print("\n" + "="*50)
    print("📄 SEEDING TEMPLATES")
    print("="*50)
    
    if clear_existing:
        deleted = await Template.find({}).delete()
        print(f"🗑️  Cleared {deleted.deleted_count} existing templates")
    
    templates_data = [
        {
            "title": "Modern SaaS Landing Page",
            "category": "Landing Page",
            "type": "Next.js",
            "language": "TypeScript",
            "difficulty_level": "Intermediate",
            "plan_type": "Free",
            "short_description": "Beautiful, conversion-optimized landing page for SaaS products",
            "full_description": "Complete landing page template with hero section, features, pricing tables, testimonials, and newsletter signup. Includes animations, dark mode, and mobile-responsive design. Perfect for B2B or B2C SaaS products.",
            "git_repo_url": "https://github.com/codemurf/saas-landing",
            "live_demo_url": "https://codemurf.com/demos/saas-landing",
            "dependencies": ["next", "typescript", "tailwindcss", "framer-motion"],
            "tags": ["landing-page", "saas", "marketing", "conversion", "responsive"],
            "developer_name": "CodeMurf Team",
            "developer_experience": "6 years",
            "featured": True,
            "popular": True,
            "rating": 4.8,
            "downloads": 2340,
            "views": 8920,
            "likes": 567,
        },
        {
            "title": "E-Commerce Store Template",
            "category": "E-Commerce",
            "type": "Next.js",
            "language": "TypeScript",
            "difficulty_level": "Advanced",
            "plan_type": "Paid",
            "short_description": "Full-featured e-commerce store with Stripe integration",
            "full_description": "Production-ready e-commerce template with product catalog, shopping cart, checkout, order management, and admin dashboard. Includes Stripe payment processing, inventory management, and customer accounts.",
            "git_repo_url": "https://github.com/codemurf/ecommerce-pro",
            "live_demo_url": "https://codemurf.com/demos/ecommerce",
            "dependencies": ["next", "typescript", "stripe", "prisma", "tailwindcss"],
            "tags": ["ecommerce", "stripe", "shopping-cart", "payments", "store"],
            "developer_name": "CodeMurf Team",
            "developer_experience": "8 years",
            "featured": True,
            "popular": True,
            "rating": 4.9,
            "downloads": 1780,
            "views": 6540,
            "likes": 432,
        },
        {
            "title": "Admin Dashboard Pro",
            "category": "Dashboard",
            "type": "React",
            "language": "TypeScript",
            "difficulty_level": "Advanced",
            "plan_type": "Paid",
            "short_description": "Enterprise-grade admin dashboard with charts and analytics",
            "full_description": "Comprehensive admin dashboard with real-time analytics, user management, data tables, charts, reports, and role-based access control. Built with React, TypeScript, and modern best practices.",
            "git_repo_url": "https://github.com/codemurf/admin-pro",
            "live_demo_url": "https://codemurf.com/demos/admin-dashboard",
            "dependencies": ["react", "typescript", "recharts", "react-table", "tailwindcss"],
            "tags": ["dashboard", "admin", "analytics", "charts", "enterprise"],
            "developer_name": "CodeMurf Team",
            "developer_experience": "7 years",
            "featured": True,
            "popular": False,
            "rating": 4.7,
            "downloads": 1450,
            "views": 5230,
            "likes": 389,
        },
        {
            "title": "Portfolio Website",
            "category": "Portfolio",
            "type": "Static Site",
            "language": "JavaScript",
            "difficulty_level": "Beginner",
            "plan_type": "Free",
            "short_description": "Clean, modern portfolio for developers and designers",
            "full_description": "Minimalist portfolio template perfect for showcasing your work. Includes project gallery, about section, skills, contact form, and blog. Fully responsive with smooth animations.",
            "git_repo_url": "https://github.com/codemurf/portfolio",
            "live_demo_url": "https://codemurf.com/demos/portfolio",
            "dependencies": ["html", "css", "javascript", "gsap"],
            "tags": ["portfolio", "personal", "showcase", "minimal", "animation"],
            "developer_name": "CodeMurf Team",
            "developer_experience": "4 years",
            "featured": False,
            "popular": True,
            "rating": 4.6,
            "downloads": 3200,
            "views": 12400,
            "likes": 789,
        },
        {
            "title": "Blog Platform",
            "category": "Blog",
            "type": "Next.js",
            "language": "TypeScript",
            "difficulty_level": "Intermediate",
            "plan_type": "Free",
            "short_description": "Modern blog platform with MDX and dark mode",
            "full_description": "Full-featured blog template with MDX support, syntax highlighting, reading time, tags, categories, search, and RSS feed. Includes SEO optimization and social sharing.",
            "git_repo_url": "https://github.com/codemurf/blog-platform",
            "live_demo_url": "https://codemurf.com/demos/blog",
            "dependencies": ["next", "mdx", "typescript", "tailwindcss"],
            "tags": ["blog", "mdx", "content", "seo", "writing"],
            "developer_name": "CodeMurf Team",
            "developer_experience": "5 years",
            "featured": False,
            "popular": True,
            "rating": 4.5,
            "downloads": 2100,
            "views": 7800,
            "likes": 521,
        },
    ]
    
    template_count = 0
    for tpl_data in templates_data:
        tpl_data.update({
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "is_active": True,
            "approval_status": TemplateStatus.APPROVED,
            "approved_at": datetime.now(timezone.utc),
            "is_available_for_dev": True,
            "is_purchasable": True,
        })
        
        template = Template(**tpl_data)
        await template.insert()
        template_count += 1
        print(f"✅ {tpl_data['title']} ({tpl_data['category']})")
    
    print(f"\n📊 Created {template_count} templates")
    
    # ========== COMPONENTS ==========
    print("\n" + "="*50)
    print("🧩 SEEDING COMPONENTS")
    print("="*50)
    
    if clear_existing:
        deleted = await Component.find({}).delete()
        print(f"🗑️  Cleared {deleted.deleted_count} existing components")
    
    components_data = [
        {
            "title": "Modern Button Set",
            "category": "Buttons",
            "type": "React",
            "language": "TypeScript",
            "difficulty_level": "Beginner",
            "plan_type": "Free",
            "short_description": "Collection of modern, accessible button components",
            "full_description": "Comprehensive button component library with multiple variants (primary, secondary, outline, ghost), sizes, loading states, and icon support. Fully accessible and keyboard navigable.",
            "git_repo_url": "https://github.com/codemurf/button-set",
            "live_demo_url": "https://codemurf.com/demos/buttons",
            "dependencies": ["react", "typescript", "tailwindcss"],
            "tags": ["button", "ui", "accessible", "react", "component"],
            "developer_name": "CodeMurf UI Team",
            "developer_experience": "5 years",
            "featured": True,
            "rating": 4.9,
            "downloads": 4500,
            "views": 15200,
            "likes": 892,
        },
        {
            "title": "Advanced Data Table",
            "category": "Tables",
            "type": "React",
            "language": "TypeScript",
            "difficulty_level": "Advanced",
            "plan_type": "Paid",
            "short_description": "Feature-rich data table with sorting, filtering, and pagination",
            "full_description": "Enterprise-grade data table component with sorting, filtering, pagination, row selection, export to CSV/Excel, column resizing, and virtual scrolling for large datasets.",
            "git_repo_url": "https://github.com/codemurf/data-table-pro",
            "live_demo_url": "https://codemurf.com/demos/table",
            "dependencies": ["react", "typescript", "tanstack-table", "date-fns"],
            "tags": ["table", "data-grid", "sorting", "filtering", "enterprise"],
            "developer_name": "CodeMurf Data Team",
            "developer_experience": "8 years",
            "featured": True,
            "rating": 4.8,
            "downloads": 2100,
            "views": 7800,
            "likes": 567,
        },
        {
            "title": "Modal Dialog System",
            "category": "Modals",
            "type": "React",
            "language": "TypeScript",
            "difficulty_level": "Intermediate",
            "plan_type": "Free",
            "short_description": "Customizable modal with animations and focus management",
            "full_description": "Fully accessible modal dialog component with smooth animations, backdrop control, keyboard navigation (ESC to close), focus trap, and portal rendering.",
            "git_repo_url": "https://github.com/codemurf/modal-system",
            "live_demo_url": "https://codemurf.com/demos/modal",
            "dependencies": ["react", "framer-motion", "focus-trap-react"],
            "tags": ["modal", "dialog", "overlay", "accessible", "animation"],
            "developer_name": "CodeMurf UX Team",
            "developer_experience": "6 years",
            "featured": False,
            "rating": 4.7,
            "downloads": 3200,
            "views": 11000,
            "likes": 678,
        },
        {
            "title": "Form Components Kit",
            "category": "Forms",
            "type": "React",
            "language": "TypeScript",
            "difficulty_level": "Intermediate",
            "plan_type": "Paid",
            "short_description": "Complete form component library with validation",
            "full_description": "Comprehensive form components including inputs, selects, checkboxes, radios, date pickers, and file uploads. Built-in validation, error handling, and accessibility features.",
            "git_repo_url": "https://github.com/codemurf/form-kit",
            "live_demo_url": "https://codemurf.com/demos/forms",
            "dependencies": ["react", "react-hook-form", "yup", "date-fns"],
            "tags": ["form", "validation", "input", "accessible", "hooks"],
            "developer_name": "CodeMurf Forms Team",
            "developer_experience": "7 years",
            "featured": True,
            "rating": 4.8,
            "downloads": 2800,
            "views": 9600,
            "likes": 734,
        },
        {
            "title": "Chart Library Pro",
            "category": "Charts",
            "type": "React",
            "language": "TypeScript",
            "difficulty_level": "Advanced",
            "plan_type": "Paid",
            "short_description": "Interactive charts and graphs for data visualization",
            "full_description": "Comprehensive charting library with line, bar, pie, area, scatter, and candlestick charts. Features include tooltips, zoom, pan, real-time updates, and export to PNG/SVG.",
            "git_repo_url": "https://github.com/codemurf/chart-pro",
            "live_demo_url": "https://codemurf.com/demos/charts",
            "dependencies": ["react", "recharts", "d3", "typescript"],
            "tags": ["chart", "graph", "visualization", "analytics", "data"],
            "developer_name": "CodeMurf Data Viz",
            "developer_experience": "9 years",
            "featured": True,
            "rating": 4.9,
            "downloads": 1900,
            "views": 6700,
            "likes": 512,
        },
    ]
    
    component_count = 0
    for comp_data in components_data:
        comp_data.update({
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "is_active": True,
            "approval_status": ComponentStatus.APPROVED,
            "approved_at": datetime.now(timezone.utc),
            "is_available_for_dev": True,
            "is_purchasable": True,
        })
        
        component = Component(**comp_data)
        await component.insert()
        component_count += 1
        print(f"✅ {comp_data['title']} ({comp_data['category']})")
    
    print(f"\n📊 Created {component_count} components")
    
    # ========== SUMMARY ==========
    print("\n" + "="*50)
    print("📊 DATABASE SUMMARY")
    print("="*50)
    
    total_templates = await Template.find({}).count()
    total_components = await Component.find({}).count()
    
    print(f"📄 Total Templates: {total_templates}")
    print(f"🧩 Total Components: {total_components}")
    print(f"📦 Total Items: {total_templates + total_components}")
    
    print("\n📋 Templates by category:")
    template_categories = await Template.distinct("category")
    for cat in template_categories:
        count = await Template.find({"category": cat}).count()
        print(f"  - {cat}: {count}")
    
    print("\n📋 Components by category:")
    component_categories = await Component.distinct("category")
    for cat in component_categories:
        count = await Component.find({"category": cat}).count()
        print(f"  - {cat}: {count}")
    
    client.close()
    print("\n✅ Seed completed successfully!\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed database with templates and components")
    parser.add_argument("--clear", action="store_true", help="Clear existing data before seeding")
    args = parser.parse_args()
    
    asyncio.run(seed_all(clear_existing=args.clear))
