"""
Upload website templates with proper preview images.
Uses Microlink API for live website screenshots.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from bson import ObjectId

# MongoDB connection - Docker local
DATABASE_URL = "mongodb://admin:password123@localhost:27017/user_management_db?authSource=admin"

def get_screenshot_url(url: str) -> str:
    """Generate screenshot URL using Thum.io (free, no API key needed).
    Returns a direct image URL that can be used in <img> tags.
    Format: https://image.thum.io/get/width/800/URL
    """
    # Thum.io provides free website screenshots
    # The URL returns an actual image, not JSON
    return f"https://image.thum.io/get/width/600/{url}"

# Templates with real live demo URLs for screenshot generation
TEMPLATES = [
    {
        "title": "Tailwind Starter Kit",
        "category": "Landing Page",
        "type": "React Component",
        "language": "JavaScript",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.8,
        "downloads": 5420,
        "views": 15000,
        "likes": 890,
        "short_description": "Free and open source Tailwind CSS starter kit with a modern design",
        "full_description": """A beautiful free starter kit for Tailwind CSS. This kit features a landing page with hero section, features grid, testimonials, and pricing table.

## Features
- Responsive design
- Dark mode support
- Animations with Framer Motion
- SEO optimized""",
        "git_repo_url": "https://github.com/creativetimofficial/tailwind-starter-kit",
        "live_demo_url": "https://www.creative-tim.com/learning-lab/tailwind-starter-kit/presentation",
        "dependencies": ["react", "tailwindcss", "framer-motion"],
        "tags": ["tailwind", "landing", "starter", "react", "responsive"],
        "developer_name": "Creative Tim",
        "developer_experience": "8 years",
        "featured": True,
        "popular": True
    },
    {
        "title": "Next.js Commerce",
        "category": "E-commerce",
        "type": "Full Stack",
        "language": "TypeScript",
        "difficulty_level": "Advanced",
        "plan_type": "Free",
        "rating": 4.9,
        "downloads": 8200,
        "views": 25000,
        "likes": 1250,
        "short_description": "High-performance e-commerce storefront by Vercel",
        "full_description": """A production-ready e-commerce template built with Next.js. Features product catalog, shopping cart, and checkout flow.

## Features
- Next.js 14 App Router
- Shopify integration
- Fast checkout
- Product search""",
        "git_repo_url": "https://github.com/vercel/commerce",
        "live_demo_url": "https://demo.vercel.store",
        "dependencies": ["next", "typescript", "tailwindcss"],
        "tags": ["ecommerce", "nextjs", "shopify", "store"],
        "developer_name": "Vercel",
        "developer_experience": "10 years",
        "featured": True,
        "popular": True
    },
    {
        "title": "Astro Blog Theme",
        "category": "Blog",
        "type": "Static Site",
        "language": "TypeScript",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.7,
        "downloads": 6500,
        "views": 18000,
        "likes": 920,
        "short_description": "Beautiful blog template built with Astro framework",
        "full_description": """A modern blog template with excellent performance scores. Built with Astro for fast page loads.

## Features
- 100 Lighthouse score
- Markdown support
- Dark mode
- RSS feed""",
        "git_repo_url": "https://github.com/withastro/astro",
        "live_demo_url": "https://astro.build",
        "dependencies": ["astro", "typescript"],
        "tags": ["blog", "astro", "fast", "markdown"],
        "developer_name": "Astro",
        "developer_experience": "5 years",
        "featured": True,
        "popular": True
    },
    {
        "title": "Shadcn Dashboard",
        "category": "Dashboard",
        "type": "React Component",
        "language": "TypeScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "rating": 4.9,
        "downloads": 12000,
        "views": 35000,
        "likes": 2100,
        "short_description": "Beautiful dashboard built with Shadcn UI components",
        "full_description": """A stunning admin dashboard using Shadcn UI. Features charts, tables, and authentication.

## Features
- Radix UI primitives
- Tailwind CSS
- Dark mode
- Responsive design""",
        "git_repo_url": "https://github.com/shadcn-ui/ui",
        "live_demo_url": "https://ui.shadcn.com",
        "dependencies": ["react", "tailwindcss", "radix-ui"],
        "tags": ["dashboard", "shadcn", "admin", "charts"],
        "developer_name": "Shadcn",
        "developer_experience": "6 years",
        "featured": True,
        "popular": True
    },
    {
        "title": "Docusaurus Docs",
        "category": "Documentation",
        "type": "Static Site",
        "language": "JavaScript",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.8,
        "downloads": 9500,
        "views": 28000,
        "likes": 1650,
        "short_description": "Documentation website generator by Meta",
        "full_description": """Build beautiful documentation websites with Docusaurus. Used by major open source projects.

## Features
- MDX support
- Versioning
- Search integration
- i18n support""",
        "git_repo_url": "https://github.com/facebook/docusaurus",
        "live_demo_url": "https://docusaurus.io",
        "dependencies": ["react", "mdx"],
        "tags": ["docs", "documentation", "meta", "mdx"],
        "developer_name": "Meta",
        "developer_experience": "15 years",
        "featured": True,
        "popular": True
    },
    {
        "title": "Notion Clone",
        "category": "SaaS",
        "type": "Full Stack",
        "language": "TypeScript",
        "difficulty_level": "Advanced",
        "plan_type": "Free",
        "rating": 4.6,
        "downloads": 4200,
        "views": 15000,
        "likes": 780,
        "short_description": "Open source Notion alternative with real-time collaboration",
        "full_description": """A Notion-like workspace with real-time editing. Features rich text editor and nested pages.

## Features
- Block-based editor
- Real-time sync
- File uploads
- Dark mode""",
        "git_repo_url": "https://github.com/toeverything/AFFiNE",
        "live_demo_url": "https://affine.pro",
        "dependencies": ["react", "typescript", "yjs"],
        "tags": ["notion", "workspace", "editor", "collaboration"],
        "developer_name": "AFFiNE",
        "developer_experience": "4 years",
        "featured": False,
        "popular": True
    },
    {
        "title": "Cal.com Booking",
        "category": "SaaS",
        "type": "Full Stack",
        "language": "TypeScript",
        "difficulty_level": "Advanced",
        "plan_type": "Free",
        "rating": 4.8,
        "downloads": 7800,
        "views": 22000,
        "likes": 1420,
        "short_description": "Open source scheduling platform like Calendly",
        "full_description": """A beautiful scheduling tool for appointments and meetings. Self-hostable alternative to Calendly.

## Features
- Calendar integrations
- Video conferencing
- Payment integration
- Custom branding""",
        "git_repo_url": "https://github.com/calcom/cal.com",
        "live_demo_url": "https://cal.com",
        "dependencies": ["next", "prisma", "trpc"],
        "tags": ["scheduling", "calendar", "booking", "meetings"],
        "developer_name": "Cal.com",
        "developer_experience": "5 years",
        "featured": True,
        "popular": True
    },
    {
        "title": "Portfolio Starter",
        "category": "Portfolio",
        "type": "Static Site",
        "language": "JavaScript",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.5,
        "downloads": 5600,
        "views": 16000,
        "likes": 890,
        "short_description": "Minimal developer portfolio with project showcase",
        "full_description": """A clean portfolio template for developers. Show off your projects and skills.

## Features
- Project gallery
- Skills section
- Contact form
- Blog support""",
        "git_repo_url": "https://github.com/craftzdog/craftzdog-homepage",
        "live_demo_url": "https://www.craftz.dog",
        "dependencies": ["next", "chakra-ui", "framer-motion"],
        "tags": ["portfolio", "developer", "minimal", "projects"],
        "developer_name": "Takuya Matsuyama",
        "developer_experience": "10 years",
        "featured": False,
        "popular": True
    },
    {
        "title": "Stripe Landing",
        "category": "Landing Page",
        "type": "Static Site",
        "language": "JavaScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "rating": 4.7,
        "downloads": 4800,
        "views": 14000,
        "likes": 720,
        "short_description": "Stripe-inspired landing page with animations",
        "full_description": """A beautiful landing page inspired by Stripe's design. Features smooth animations and gradients.

## Features
- Animated hero
- Gradient effects
- Responsive design
- Modern typography""",
        "git_repo_url": "https://github.com/stripe/stripe.com",
        "live_demo_url": "https://stripe.com",
        "dependencies": ["react", "gsap"],
        "tags": ["landing", "stripe", "animations", "gradients"],
        "developer_name": "Stripe",
        "developer_experience": "12 years",
        "featured": True,
        "popular": True
    },
    {
        "title": "Linear Clone",
        "category": "SaaS",
        "type": "Full Stack",
        "language": "TypeScript",
        "difficulty_level": "Advanced",
        "plan_type": "Free",
        "rating": 4.8,
        "downloads": 3500,
        "views": 11000,
        "likes": 650,
        "short_description": "Project management tool inspired by Linear",
        "full_description": """A beautiful project tracking app like Linear. Keyboard-first design with smooth animations.

## Features
- Issue tracking
- Roadmap view
- Keyboard shortcuts
- Dark mode""",
        "git_repo_url": "https://github.com/calcom/cal.com",
        "live_demo_url": "https://linear.app",
        "dependencies": ["react", "typescript", "framer-motion"],
        "tags": ["linear", "project", "issues", "tracking"],
        "developer_name": "Linear",
        "developer_experience": "6 years",
        "featured": True,
        "popular": True
    }
]

async def upload_templates():
    print("=" * 60)
    print("📦 UPLOADING TEMPLATES WITH PREVIEW IMAGES")
    print("=" * 60 + "\n")
    
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client.user_management_db
    
    # Get a default user_id
    user = await db.users.find_one({})
    user_id = user["_id"] if user else None
    
    if not user_id:
        print("⚠️  No users found. Templates will be created without user_id.")
    else:
        print(f"✅ Using user: {user.get('email', 'unknown')}")
    
    # Prepare templates
    templates_to_insert = []
    for tpl in TEMPLATES:
        # Generate preview image from live_demo_url using Thum.io
        preview_url = get_screenshot_url(tpl["live_demo_url"])
        
        template_doc = {
            "_id": ObjectId(),
            "title": tpl["title"],
            "category": tpl["category"],
            "type": tpl["type"],
            "language": tpl["language"],
            "difficulty_level": tpl["difficulty_level"],
            "plan_type": tpl["plan_type"],
            "rating": tpl["rating"],
            "downloads": tpl["downloads"],
            "views": tpl["views"],
            "likes": tpl["likes"],
            "short_description": tpl["short_description"],
            "full_description": tpl["full_description"],
            "preview_images": [preview_url],  # Microlink screenshot URL
            "git_repo_url": tpl["git_repo_url"],
            "live_demo_url": tpl["live_demo_url"],
            "dependencies": tpl["dependencies"],
            "tags": tpl["tags"],
            "developer_name": tpl["developer_name"],
            "developer_experience": tpl["developer_experience"],
            "is_available_for_dev": True,
            "featured": tpl["featured"],
            "popular": tpl["popular"],
            "user_id": user_id,
            "approval_status": "approved",
            "approved_at": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "is_active": True,
            "is_purchasable": True,
            "purchase_count": 0,
            "average_rating": tpl["rating"],
            "total_ratings": 0,
            "comments_count": 0
        }
        templates_to_insert.append(template_doc)
        print(f"✅ Prepared: {tpl['title']} - Preview: {preview_url[:60]}...")
    
    # Insert templates
    print(f"\n🔄 Inserting {len(templates_to_insert)} templates...")
    
    result = await db.templates.insert_many(templates_to_insert)
    print(f"✅ Inserted {len(result.inserted_ids)} templates successfully!")
    
    # Count by category
    print("\n📊 Templates by Category:")
    pipeline = [{"$group": {"_id": "$category", "count": {"$sum": 1}}}]
    cursor = db.templates.aggregate(pipeline)
    async for doc in cursor:
        print(f"  - {doc['_id']}: {doc['count']}")
    
    total = await db.templates.count_documents({})
    print(f"\n📊 Total templates in database: {total}")
    
    client.close()
    print("\n✅ Template upload complete!")
    print("\n💡 Thum.io generates direct image URLs from any website URL.")
    print("   Preview images work directly in <img> tags without any parsing.")

if __name__ == "__main__":
    asyncio.run(upload_templates())
