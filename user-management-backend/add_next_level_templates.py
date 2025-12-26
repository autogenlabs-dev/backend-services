"""
Add 15 "Next Level" modern templates to the database.
These are high-quality, open-source, cloneable applications.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from bson import ObjectId

DATABASE_URL = "mongodb://admin:password123@localhost:27017/user_management_db?authSource=admin"

NEXT_LEVEL_TEMPLATES = [
    {
        "title": "Precedent",
        "category": "Starter Kit",
        "type": "Next.js Template",
        "language": "TypeScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "rating": 5.0,
        "downloads": 50000,
        "views": 200000,
        "likes": 12000,
        "short_description": "Opinionated Next.js starter with Radix UI, Tailwind CSS, and Framer Motion",
        "full_description": """An opinionated collection of components, hooks, and utilities for your Next.js project.

## Features
- Next.js 14 App Router
- Radix UI Primitives
- Tailwind CSS styling
- Framer Motion animations
- Auth with NextAuth.js
- Database with Prisma
""",
        "git_repo_url": "https://github.com/steven-tey/precedent",
        "live_demo_url": "https://precedent.dev",
        "dependencies": ["next", "tailwindcss", "radix-ui", "framer-motion"],
        "tags": ["starter", "nextjs", "radix-ui", "modern"],
    },
    {
        "title": "RoomGPT",
        "category": "AI Application",
        "type": "Next.js Template",
        "language": "TypeScript",
        "difficulty_level": "Advanced",
        "plan_type": "Free",
        "rating": 5.0,
        "downloads": 45000,
        "views": 300000,
        "likes": 15000,
        "short_description": "Redesign your room in seconds using AI - 100% open source",
        "full_description": """Upload a photo of your room and let AI redesign it for you.

## Features
- AI Image Generation (ControlNet)
- Next.js 13 App Router
- UploadThing for storage
- Clerk for authentication
- Tailwind CSS
""",
        "git_repo_url": "https://github.com/Nutlope/roomGPT",
        "live_demo_url": "https://roomgpt.io",
        "dependencies": ["next", "ai", "tailwindcss", "clerk"],
        "tags": ["ai", "roomgpt", "design", "nextjs"],
    },
    {
        "title": "Skateshop",
        "category": "E-commerce",
        "type": "Next.js Template",
        "language": "TypeScript",
        "difficulty_level": "Advanced",
        "plan_type": "Free",
        "rating": 4.9,
        "downloads": 25000,
        "views": 80000,
        "likes": 5000,
        "short_description": "Open source e-commerce skateshop built with Next.js 14",
        "full_description": """A feature-rich e-commerce platform built with the latest Next.js tech stack.

## Features
- Next.js 14 Server Actions
- Stripe Connect integration
- Drizzle ORM + MySQL
- Tailwind CSS + shadcn/ui
- Clerk Authentication
""",
        "git_repo_url": "https://github.com/sadmann7/skateshop",
        "live_demo_url": "https://skateshop.sadmn.com",
        "dependencies": ["next", "stripe", "drizzle", "shadcn-ui"],
        "tags": ["ecommerce", "shop", "stripe", "nextjs"],
    },
    {
        "title": "ChadNext",
        "category": "Starter Kit",
        "type": "Next.js Template",
        "language": "TypeScript",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.8,
        "downloads": 15000,
        "views": 40000,
        "likes": 3000,
        "short_description": "Quick starter with Next.js 14, shadcn/ui, Lucia, and Prisma",
        "full_description": """The quickest way to start a Next.js project with the best tools.

## Features
- Next.js 14 App Router
- shadcn/ui components
- Lucia Auth
- Prisma ORM
- Stripe integration
""",
        "git_repo_url": "https://github.com/moinulmoin/chadnext",
        "live_demo_url": "https://chadnext.moinulmoin.com",
        "dependencies": ["next", "shadcn-ui", "lucia", "prisma"],
        "tags": ["starter", "shadcn", "lucia", "nextjs"],
    },
    {
        "title": "Mantis Dashboard",
        "category": "Dashboard",
        "type": "React Template",
        "language": "TypeScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "rating": 4.8,
        "downloads": 30000,
        "views": 90000,
        "likes": 4000,
        "short_description": "Modern React Material UI dashboard template",
        "full_description": """A professional admin dashboard built with MUI (Material-UI).

## Features
- Material UI v5
- React Hooks
- Redux Toolkit
- Light/Dark Mode
- Fully Responsive
""",
        "git_repo_url": "https://github.com/codedthemes/mantis-free-react-admin-template",
        "live_demo_url": "https://mantisdashboard.io/free",
        "dependencies": ["react", "mui", "redux"],
        "tags": ["dashboard", "admin", "mui", "react"],
    },
    {
        "title": "Horizon UI",
        "category": "Dashboard",
        "type": "React Template",
        "language": "TypeScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "rating": 4.8,
        "downloads": 20000,
        "views": 60000,
        "likes": 3500,
        "short_description": "Trendy admin dashboard for Chakra UI and React",
        "full_description": """The most trendy admin dashboard for Chakra UI.

## Features
- Chakra UI
- React.js
- 70+ Components
- Dark/Light Mode
- RTL Support
""",
        "git_repo_url": "https://github.com/horizon-ui/horizon-ui-chakra",
        "live_demo_url": "https://horizon-ui.com/chakra",
        "dependencies": ["react", "chakra-ui"],
        "tags": ["dashboard", "chakra-ui", "admin", "react"],
    },
    {
        "title": "Typebot",
        "category": "SaaS",
        "type": "Full Stack",
        "language": "TypeScript",
        "difficulty_level": "Advanced",
        "plan_type": "Free",
        "rating": 4.9,
        "downloads": 40000,
        "views": 150000,
        "likes": 8000,
        "short_description": "Conversational form builder - Open source Typeform alternative",
        "full_description": """Build beautiful conversational forms and embed them anywhere.

## Features
- Visual Flow Builder
- Real-time Analytics
- Integrations (Google Sheets, Webhooks)
- Embed anywhere
- Next.js + Prisma + Tailwind
""",
        "git_repo_url": "https://github.com/baptisteArno/typebot.io",
        "live_demo_url": "https://typebot.io",
        "dependencies": ["next", "prisma", "tailwindcss"],
        "tags": ["form", "builder", "saas", "typebot"],
    },
    {
        "title": "Formbricks",
        "category": "SaaS",
        "type": "Full Stack",
        "language": "TypeScript",
        "difficulty_level": "Advanced",
        "plan_type": "Free",
        "rating": 4.9,
        "downloads": 35000,
        "views": 120000,
        "likes": 7000,
        "short_description": "Open source survey platform - Qualtrics alternative",
        "full_description": """The open source survey platform for product teams.

## Features
- In-app Surveys
- Link Surveys
- No-code Editor
- Data Analysis
- Next.js + Tailwind
""",
        "git_repo_url": "https://github.com/formbricks/formbricks",
        "live_demo_url": "https://formbricks.com",
        "dependencies": ["next", "tailwindcss", "prisma"],
        "tags": ["survey", "saas", "formbricks", "analytics"],
    },
    {
        "title": "Twenty",
        "category": "CRM",
        "type": "Full Stack",
        "language": "TypeScript",
        "difficulty_level": "Advanced",
        "plan_type": "Free",
        "rating": 5.0,
        "downloads": 20000,
        "views": 100000,
        "likes": 10000,
        "short_description": "Modern open-source CRM - Salesforce alternative",
        "full_description": """The open-source CRM built for the modern web.

## Features
- Custom Objects
- Kanban & List Views
- API-first
- Self-hostable
- React + NestJS
""",
        "git_repo_url": "https://github.com/twentyhq/twenty",
        "live_demo_url": "https://twenty.com",
        "dependencies": ["react", "nestjs", "postgresql"],
        "tags": ["crm", "saas", "business", "modern"],
    },
    {
        "title": "Plane",
        "category": "Project Management",
        "type": "Full Stack",
        "language": "TypeScript",
        "difficulty_level": "Advanced",
        "plan_type": "Free",
        "rating": 5.0,
        "downloads": 60000,
        "views": 250000,
        "likes": 20000,
        "short_description": "Open source project management tool - JIRA alternative",
        "full_description": """Simple, extensible, open-source project management tool.

## Features
- Issue Tracking
- Cycles & Modules
- Pages & Docs
- Analytics
- Next.js + Django
""",
        "git_repo_url": "https://github.com/makeplane/plane",
        "live_demo_url": "https://plane.so",
        "dependencies": ["next", "django", "python"],
        "tags": ["project-management", "jira", "saas", "productivity"],
    },
    {
        "title": "Infisical",
        "category": "DevTools",
        "type": "Full Stack",
        "language": "TypeScript",
        "difficulty_level": "Advanced",
        "plan_type": "Free",
        "rating": 4.9,
        "downloads": 25000,
        "views": 90000,
        "likes": 9000,
        "short_description": "Open source secret management platform",
        "full_description": """Manage secrets and configs across your team and infrastructure.

## Features
- End-to-end Encryption
- Secret Versioning
- Integrations (Vercel, AWS, etc.)
- Self-hostable
- Next.js + Node.js
""",
        "git_repo_url": "https://github.com/Infisical/infisical",
        "live_demo_url": "https://infisical.com",
        "dependencies": ["next", "nodejs", "encryption"],
        "tags": ["security", "secrets", "devtools", "saas"],
    },
    {
        "title": "Dub.co",
        "category": "SaaS",
        "type": "Full Stack",
        "language": "TypeScript",
        "difficulty_level": "Advanced",
        "plan_type": "Free",
        "rating": 4.9,
        "downloads": 30000,
        "views": 110000,
        "likes": 11000,
        "short_description": "Open source link management infrastructure",
        "full_description": """Modern link management for marketing teams.

## Features
- Advanced Analytics
- Custom Domains
- QR Codes
- API-first
- Next.js + Vercel Edge Functions
""",
        "git_repo_url": "https://github.com/dubinc/dub",
        "live_demo_url": "https://dub.co",
        "dependencies": ["next", "tinybird", "upstash"],
        "tags": ["links", "analytics", "saas", "marketing"],
    },
    {
        "title": "Flowise",
        "category": "AI Application",
        "type": "Full Stack",
        "language": "TypeScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "rating": 4.9,
        "downloads": 40000,
        "views": 130000,
        "likes": 13000,
        "short_description": "Drag & drop UI to build your customized LLM flow",
        "full_description": """Build LLM apps easily with a visual drag & drop interface.

## Features
- LangChain Integration
- Visual Flow Builder
- Chat Interface
- API Access
- React + Node.js
""",
        "git_repo_url": "https://github.com/FlowiseAI/Flowise",
        "live_demo_url": "https://flowiseai.com",
        "dependencies": ["react", "langchain", "nodejs"],
        "tags": ["ai", "llm", "langchain", "visual"],
    },
    {
        "title": "Novel",
        "category": "Component",
        "type": "React Template",
        "language": "TypeScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "rating": 4.8,
        "downloads": 20000,
        "views": 70000,
        "likes": 6000,
        "short_description": "Notion-style WYSIWYG editor with AI-powered autocompletions",
        "full_description": """A Notion-style WYSIWYG editor with AI-powered autocompletions.

## Features
- Tiptap Editor
- AI Autocomplete
- Slash Commands
- Markdown Support
- Next.js + Tailwind
""",
        "git_repo_url": "https://github.com/steven-tey/novel",
        "live_demo_url": "https://novel.sh",
        "dependencies": ["next", "tiptap", "ai"],
        "tags": ["editor", "notion", "ai", "component"],
    },
    {
        "title": "Vercel Commerce",
        "category": "E-commerce",
        "type": "Next.js Template",
        "language": "TypeScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "rating": 4.9,
        "downloads": 100000,
        "views": 500000,
        "likes": 10000,
        "short_description": "The all-in-one starter kit for high-performance e-commerce sites",
        "full_description": """The standard for high-performance e-commerce sites.

## Features
- Next.js App Router
- Optimized for Performance
- Shopify / BigCommerce / etc. Integration
- Tailwind CSS
- Edge Middleware
""",
        "git_repo_url": "https://github.com/vercel/commerce",
        "live_demo_url": "https://demo.vercel.store",
        "dependencies": ["next", "ecommerce", "tailwindcss"],
        "tags": ["ecommerce", "store", "vercel", "performance"],
    }
]

async def add_next_level_templates():
    print("=" * 60)
    print("🚀 ADDING 15 NEXT-LEVEL MODERN TEMPLATES")
    print("=" * 60 + "\n")
    
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client.user_management_db
    
    user = await db.users.find_one({})
    user_id = user["_id"] if user else None
    
    for tpl in NEXT_LEVEL_TEMPLATES:
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
            "preview_images": [],  # Will add screenshots next
            "git_repo_url": tpl["git_repo_url"],
            "live_demo_url": tpl["live_demo_url"],
            "dependencies": tpl["dependencies"],
            "tags": tpl["tags"],
            "developer_name": "Open Source Community",
            "developer_experience": "Various",
            "is_available_for_dev": True,
            "featured": True,
            "popular": True,
            "user_id": user_id,
            "approval_status": "approved",
            "approved_at": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "is_active": True,
            "is_purchasable": True,
        }
        
        # Upsert based on title to avoid duplicates
        await db.templates.update_one(
            {"title": tpl["title"]},
            {"$set": template_doc},
            upsert=True
        )
        print(f"✅ {tpl['title']}")
        print(f"   🔗 {tpl['live_demo_url']}")
        print()
    
    total = await db.templates.count_documents({})
    print(f"\n📊 Total templates: {total}")
    
    client.close()
    print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(add_next_level_templates())
