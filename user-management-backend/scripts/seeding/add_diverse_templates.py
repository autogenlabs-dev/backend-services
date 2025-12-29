"""
Script to add diverse usable website templates - landing pages, dashboards, 
e-commerce, admin panels, blogs, agency sites, etc.
"""

import asyncio
from playwright.async_api import async_playwright
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path
from bson import ObjectId
from datetime import datetime, timezone

# Load .env file
load_dotenv()

# MongoDB connection
MONGODB_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017/user_management_db")

# Screenshot output directory
SCREENSHOTS_DIR = Path("/home/cis/Music/Autogenlabs-Web-App/public/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Diverse templates to add
DIVERSE_TEMPLATES = [
    # Landing Pages
    {
        "title": "Play - SaaS Startup Landing Page",
        "short_description": "Free open-source Tailwind CSS template for SaaS, startup, and business websites with modern design.",
        "category": "Landing Page",
        "type": "HTML/CSS",
        "live_demo_url": "https://play-tailwind.tailgrids.com",
        "git_repo_url": "https://github.com/tailgrids/play-tailwind",
        "technologies": ["Tailwind CSS", "HTML", "JavaScript"],
        "tags": ["landing page", "saas", "startup", "tailwind"],
        "featured": True,
    },
    {
        "title": "Simple Light - SaaS Landing Page",
        "short_description": "Clean React/Next.js landing page template for SaaS products with essential components and sections.",
        "category": "Landing Page",
        "type": "Next.js",
        "live_demo_url": "https://simple-light-nextjs.vercel.app",
        "git_repo_url": "https://github.com/cruip/tailwind-landing-page-template",
        "technologies": ["Next.js", "React", "Tailwind CSS"],
        "tags": ["landing page", "saas", "nextjs", "clean"],
        "featured": False,
    },
    {
        "title": "Open React Landing Template",
        "short_description": "Meticulously crafted Next.js landing page with Tailwind CSS for open-source projects and SaaS.",
        "category": "Landing Page",
        "type": "Next.js",
        "live_demo_url": "https://open-react-template.vercel.app",
        "git_repo_url": "https://github.com/cruip/open-react-template",
        "technologies": ["Next.js", "React", "Tailwind CSS", "Framer Motion"],
        "tags": ["landing page", "open source", "modern", "animations"],
        "featured": True,
    },
    # Admin Dashboards  
    {
        "title": "TailAdmin - Admin Dashboard",
        "short_description": "Free open-source admin dashboard built with Next.js and Tailwind CSS for backend and admin panels.",
        "category": "Dashboard",
        "type": "Next.js",
        "live_demo_url": "https://nextjs-demo.tailadmin.com",
        "git_repo_url": "https://github.com/TailAdmin/free-nextjs-admin-dashboard",
        "technologies": ["Next.js", "React", "Tailwind CSS", "TypeScript"],
        "tags": ["dashboard", "admin", "tailwind", "charts"],
        "featured": True,
    },
    {
        "title": "Shadcn Admin Dashboard",
        "short_description": "Modern admin dashboard with shadcn/ui, Vite, React and TypeScript. 10+ pre-built pages.",
        "category": "Dashboard",
        "type": "React",
        "live_demo_url": "https://shadcn-admin.netlify.app",
        "git_repo_url": "https://github.com/satnaing/shadcn-admin",
        "technologies": ["React", "Vite", "shadcn/ui", "TypeScript", "Tailwind CSS"],
        "tags": ["dashboard", "admin", "shadcn", "modern"],
        "featured": True,
    },
    # Agency & Business
    {
        "title": "Flavor - Agency Template",
        "short_description": "Creative digital agency template with smooth animations, dark theme, and modern sections.",
        "category": "Agency",
        "type": "Next.js",
        "live_demo_url": "https://flavor-demo.vercel.app",
        "git_repo_url": "https://github.com/themefisher/flavor-agency",
        "technologies": ["Next.js", "React", "Tailwind CSS", "GSAP"],
        "tags": ["agency", "creative", "dark theme", "animations"],
        "featured": False,
    },
    # Blog Templates
    {
        "title": "Starter Blog - MDX Blog Template",
        "short_description": "Next.js blog starter with MDX support, dark mode, and SEO-friendly design.",
        "category": "Blog",
        "type": "Next.js",
        "live_demo_url": "https://tailwind-nextjs-starter-blog.vercel.app",
        "git_repo_url": "https://github.com/timlrx/tailwind-nextjs-starter-blog",
        "technologies": ["Next.js", "MDX", "Tailwind CSS", "ContentLayer"],
        "tags": ["blog", "mdx", "seo", "dark mode"],
        "featured": False,
    },
    # E-commerce
    {
        "title": "Next.js Commerce",
        "short_description": "High-performance e-commerce starter with Next.js, Vercel, and Shopify integration.",
        "category": "E-commerce",
        "type": "Next.js",
        "live_demo_url": "https://demo.vercel.store",
        "git_repo_url": "https://github.com/vercel/commerce",
        "technologies": ["Next.js", "React", "Tailwind CSS", "Shopify"],
        "tags": ["ecommerce", "store", "shopify", "vercel"],
        "featured": True,
    },
    # SaaS Starters
    {
        "title": "Next.js SaaS Starter",
        "short_description": "Full-stack SaaS starter with authentication, Stripe payments, and dashboard. Official Vercel template.",
        "category": "SaaS",
        "type": "Next.js",
        "live_demo_url": "https://nextjs-saas-starter-ashen.vercel.app",
        "git_repo_url": "https://github.com/vercel/nextjs-saas-starter",
        "technologies": ["Next.js", "React", "Postgres", "Stripe", "shadcn/ui"],
        "tags": ["saas", "starter", "stripe", "auth"],
        "featured": True,
    },
    # Documentation
    {
        "title": "Nextra Docs Template",
        "short_description": "Beautiful documentation site generator with Next.js. Fast, SEO-friendly, and customizable.",
        "category": "Documentation",
        "type": "Next.js",
        "live_demo_url": "https://nextra.site",
        "git_repo_url": "https://github.com/shuding/nextra",
        "technologies": ["Next.js", "MDX", "React", "Tailwind CSS"],
        "tags": ["docs", "documentation", "mdx", "search"],
        "featured": False,
    },
]

async def capture_screenshot(page, url, filename):
    """Capture a screenshot of a website."""
    try:
        print(f"  📸 Capturing: {url}")
        await page.goto(url, wait_until='networkidle', timeout=45000)
        await asyncio.sleep(3)
        
        screenshot_path = SCREENSHOTS_DIR / filename
        await page.screenshot(path=str(screenshot_path), full_page=False)
        
        print(f"  ✅ Saved: {filename}")
        return f"/screenshots/{filename}"
    except Exception as e:
        print(f"  ❌ Failed: {url} - {str(e)[:60]}")
        return None

async def add_diverse_templates():
    """Add diverse website templates with screenshots."""
    
    print("🔌 Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_default_database()
    templates_collection = db.templates
    
    # Get a valid user_id
    sample = await templates_collection.find_one({'user_id': {'$exists': True}})
    user_id = sample.get('user_id') if sample else ObjectId("000000000000000000000001")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            device_scale_factor=1
        )
        page = await context.new_page()
        
        added_count = 0
        for template_data in DIVERSE_TEMPLATES:
            title = template_data["title"]
            url = template_data["live_demo_url"]
            
            # Check if already exists
            existing = await templates_collection.find_one({"live_demo_url": url})
            if existing:
                print(f"⏭️ Skipping (already exists): {title}")
                continue
            
            print(f"\n📦 Processing: {title}")
            
            # Create safe filename
            safe_name = "".join(c if c.isalnum() or c in '-_' else '_' for c in title[:40])
            template_id = ObjectId()
            filename = f"{template_id}_{safe_name}.png"
            
            # Capture screenshot
            screenshot_url = await capture_screenshot(page, url, filename)
            
            if screenshot_url:
                # Create template document with all required fields
                template_doc = {
                    "_id": template_id,
                    "title": template_data["title"],
                    "short_description": template_data["short_description"],
                    "description": template_data["short_description"],
                    "full_description": "",
                    "live_demo_url": template_data["live_demo_url"],
                    "git_repo_url": template_data["git_repo_url"],
                    "category": template_data["category"],
                    "type": template_data["type"],
                    "language": "JavaScript",
                    "difficulty_level": "Medium",
                    "technologies": template_data["technologies"],
                    "tags": template_data["tags"],
                    "featured": template_data.get("featured", False),
                    "popular": True,
                    "preview_images": [screenshot_url],
                    "rating": 4.7,
                    "total_ratings": 0,
                    "views": 0,
                    "downloads": 0,
                    "likes": 0,
                    "plan_type": "Free",
                    "is_active": True,
                    "developer_name": "Community",
                    "developer_experience": "5",
                    "is_available_for_dev": True,
                    "user_id": user_id,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
                
                await templates_collection.insert_one(template_doc)
                print(f"  ✅ Added to database: {title}")
                added_count += 1
            else:
                print(f"  ⚠️ Skipping (no screenshot): {title}")
        
        await browser.close()
    
    # Final count
    total = await templates_collection.count_documents({})
    print(f"\n📊 Added: {added_count} new templates")
    print(f"📊 Total templates: {total}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(add_diverse_templates())
    print("\n🎉 Done!")
