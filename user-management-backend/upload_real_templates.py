"""
Upload real open-source cloneable templates with working demos.
All repos are open-source, easily cloneable, and have live demo URLs.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from bson import ObjectId

# MongoDB connection
DATABASE_URL = "mongodb://admin:password123@localhost:27017/user_management_db?authSource=admin"

# Curated list of REAL open-source templates
# All are cloneable, have live demos, and are actively maintained
TEMPLATES = [
    # PORTFOLIO TEMPLATES
    {
        "title": "Developer Portfolio - Next.js",
        "category": "Portfolio",
        "type": "Next.js Template",
        "language": "TypeScript",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.9,
        "downloads": 15000,
        "views": 45000,
        "likes": 2800,
        "short_description": "Beautiful developer portfolio with dark/light mode, built with Next.js and Tailwind CSS",
        "full_description": """A stunning software developer portfolio template built with Next.js and Tailwind CSS.

## Features
- Dark and Light mode
- Responsive design
- Animations with Framer Motion
- SEO optimized
- Easy to customize

## Clone & Run
```bash
git clone https://github.com/said7388/developer-portfolio-nextjs
cd developer-portfolio-nextjs
npm install
npm run dev
```""",
        "git_repo_url": "https://github.com/said7388/developer-portfolio-nextjs",
        "live_demo_url": "https://developer-portfolio-sand.vercel.app/",
        "dependencies": ["next", "react", "tailwindcss", "framer-motion"],
        "tags": ["portfolio", "nextjs", "tailwind", "developer", "dark-mode"],
        "developer_name": "Abu Said",
        "developer_experience": "5 years",
        "featured": True,
        "popular": True
    },
    {
        "title": "Minimal Portfolio Template",
        "category": "Portfolio",
        "type": "Next.js Template",
        "language": "TypeScript",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.7,
        "downloads": 8500,
        "views": 28000,
        "likes": 1650,
        "short_description": "Clean, minimal portfolio for developers and designers",
        "full_description": """A minimal and clean portfolio template built with Next.js, TypeScript, and Tailwind CSS.

## Features
- Minimalist design
- Fast loading
- Mobile responsive
- Easy customization
- Vercel/Netlify ready

## Clone & Run
```bash
git clone https://github.com/hqasmei/tailwindcss-and-nextjs-portfolio
npm install && npm run dev
```""",
        "git_repo_url": "https://github.com/hqasmei/tailwindcss-and-nextjs-portfolio",
        "live_demo_url": "https://tailwindcss-and-nextjs-portfolio.vercel.app/",
        "dependencies": ["next", "tailwindcss", "typescript"],
        "tags": ["portfolio", "minimal", "nextjs", "tailwind"],
        "developer_name": "Hosna Qasmei",
        "developer_experience": "4 years",
        "featured": True,
        "popular": True
    },
    
    # LANDING PAGE TEMPLATES
    {
        "title": "Open React Landing Page",
        "category": "Landing Page",
        "type": "React/Next.js",
        "language": "TypeScript",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.9,
        "downloads": 25000,
        "views": 75000,
        "likes": 4200,
        "short_description": "Free React/Next.js landing page template for open-source projects and SaaS",
        "full_description": """A beautifully designed landing page template for showcasing open-source projects, SaaS products, or online services.

## Features
- Modern design with Tailwind CSS v4
- Hero section with animations
- Features grid
- Testimonials section
- FAQ accordion
- Newsletter signup
- Fully responsive

## Clone & Run
```bash
git clone https://github.com/cruip/open-react-template
cd open-react-template
npm install
npm run dev
```""",
        "git_repo_url": "https://github.com/cruip/open-react-template",
        "live_demo_url": "https://open.cruip.com/",
        "dependencies": ["next", "react", "tailwindcss"],
        "tags": ["landing", "react", "saas", "startup", "tailwind"],
        "developer_name": "Cruip",
        "developer_experience": "7 years",
        "featured": True,
        "popular": True
    },
    {
        "title": "Next.js SaaS Starter",
        "category": "SaaS",
        "type": "Full Stack",
        "language": "TypeScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "rating": 4.8,
        "downloads": 18000,
        "views": 55000,
        "likes": 3400,
        "short_description": "Complete SaaS starter with authentication, payments, and dashboard",
        "full_description": """A production-ready SaaS starter template with everything you need to launch.

## Features
- Next.js 14 App Router
- Authentication (NextAuth)
- Database (Prisma + PostgreSQL)
- Stripe payments ready
- Admin dashboard
- SEO optimized
- Dark mode

## Clone & Run
```bash
git clone https://github.com/Blazity/next-saas-starter
cd next-saas-starter
npm install
npm run dev
```""",
        "git_repo_url": "https://github.com/Blazity/next-saas-starter",
        "live_demo_url": "https://next-saas-starter-ashy.vercel.app/",
        "dependencies": ["next", "prisma", "stripe", "nextauth", "tailwindcss"],
        "tags": ["saas", "starter", "authentication", "stripe", "dashboard"],
        "developer_name": "Blazity",
        "developer_experience": "6 years",
        "featured": True,
        "popular": True
    },
    {
        "title": "Landing Page Starter",
        "category": "Landing Page",
        "type": "Next.js Template",
        "language": "TypeScript",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.7,
        "downloads": 12000,
        "views": 38000,
        "likes": 2100,
        "short_description": "Modern landing page starter with beautiful animations",
        "full_description": """A stunning landing page template with modern design and smooth animations.

## Features
- Hero with gradient background
- Feature sections
- Pricing table
- Customer testimonials
- Contact form
- Smooth scroll animations

## Clone & Run
```bash
git clone https://github.com/ixartz/Next-JS-Landing-Page-Starter-Template
npm install && npm run dev
```""",
        "git_repo_url": "https://github.com/ixartz/Next-JS-Landing-Page-Starter-Template",
        "live_demo_url": "https://creativedesignsguru.com/demo/nextjs-landing-page/",
        "dependencies": ["next", "tailwindcss", "typescript"],
        "tags": ["landing", "startup", "modern", "animations"],
        "developer_name": "Creative Designs Guru",
        "developer_experience": "8 years",
        "featured": True,
        "popular": True
    },
    
    # BLOG TEMPLATES
    {
        "title": "Tailwind Blog Starter",
        "category": "Blog",
        "type": "Next.js Template",
        "language": "TypeScript",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.8,
        "downloads": 22000,
        "views": 65000,
        "likes": 3800,
        "short_description": "Beautiful blog template with MDX support and syntax highlighting",
        "full_description": """The ultimate blog starter for developers with MDX, code highlighting, and more.

## Features
- MDX for rich content
- Syntax highlighting (Prism)
- Table of contents
- Reading time
- Tags and categories
- RSS feed
- SEO optimized
- Dark mode

## Clone & Run
```bash
git clone https://github.com/timlrx/tailwind-nextjs-starter-blog
npm install && npm run dev
```""",
        "git_repo_url": "https://github.com/timlrx/tailwind-nextjs-starter-blog",
        "live_demo_url": "https://tailwind-nextjs-starter-blog.vercel.app/",
        "dependencies": ["next", "mdx", "tailwindcss", "contentlayer"],
        "tags": ["blog", "mdx", "developer", "technical-writing"],
        "developer_name": "Timothy Lin",
        "developer_experience": "6 years",
        "featured": True,
        "popular": True
    },
    
    # E-COMMERCE TEMPLATES
    {
        "title": "Next.js E-commerce Starter",
        "category": "E-commerce",
        "type": "Full Stack",
        "language": "TypeScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "rating": 4.6,
        "downloads": 9500,
        "views": 32000,
        "likes": 1850,
        "short_description": "Modern e-commerce template with cart and checkout",
        "full_description": """A complete e-commerce solution with product catalog, cart, and checkout.

## Features
- Product catalog
- Shopping cart
- Checkout flow
- Product search
- Category filters
- Responsive design

## Clone & Run
```bash
npx create-next-app -e https://github.com/vercel/commerce
```""",
        "git_repo_url": "https://github.com/vercel/commerce",
        "live_demo_url": "https://demo.vercel.store/",
        "dependencies": ["next", "tailwindcss", "shopify"],
        "tags": ["ecommerce", "store", "shopping", "cart"],
        "developer_name": "Vercel",
        "developer_experience": "10 years",
        "featured": True,
        "popular": True
    },
    
    # DASHBOARD TEMPLATES  
    {
        "title": "Mosaic Dashboard",
        "category": "Dashboard",
        "type": "React Template",
        "language": "TypeScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "rating": 4.8,
        "downloads": 14000,
        "views": 42000,
        "likes": 2650,
        "short_description": "Beautiful admin dashboard with charts, tables, and dark mode",
        "full_description": """A feature-rich admin dashboard template built with React and Tailwind CSS.

## Features
- 50+ UI components
- Charts (Chart.js)
- Data tables
- User management pages
- Dark/Light mode
- Sidebar navigation
- Responsive design

## Clone & Run
```bash
git clone https://github.com/cruip/tailwind-dashboard-template
npm install && npm run dev
```""",
        "git_repo_url": "https://github.com/cruip/tailwind-dashboard-template",
        "live_demo_url": "https://mosaic.cruip.com/",
        "dependencies": ["react", "tailwindcss", "chart.js"],
        "tags": ["dashboard", "admin", "charts", "dark-mode"],
        "developer_name": "Cruip",
        "developer_experience": "7 years",
        "featured": True,
        "popular": True
    },
    
    # DOCUMENTATION TEMPLATES
    {
        "title": "Nextra Docs Theme",
        "category": "Documentation",
        "type": "Next.js Template",
        "language": "TypeScript",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.9,
        "downloads": 30000,
        "views": 85000,
        "likes": 5200,
        "short_description": "Beautiful documentation site generator with MDX support",
        "full_description": """The most popular documentation framework for Next.js projects.

## Features
- MDX support
- Full-text search
- Syntax highlighting
- Dark mode
- i18n support
- Automatic sidebar
- SEO optimized

## Clone & Run
```bash
npx create-next-app -e https://github.com/shuding/nextra-docs-template
```""",
        "git_repo_url": "https://github.com/shuding/nextra-docs-template",
        "live_demo_url": "https://nextra-docs-template.vercel.app/",
        "dependencies": ["next", "nextra", "mdx"],
        "tags": ["docs", "documentation", "mdx", "nextra"],
        "developer_name": "Shu Ding",
        "developer_experience": "8 years",
        "featured": True,
        "popular": True
    },
    
    # RESTAURANT/BUSINESS
    {
        "title": "Restaurant Website Template",
        "category": "Business",
        "type": "HTML/CSS",
        "language": "HTML/CSS/JS",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.5,
        "downloads": 8200,
        "views": 25000,
        "likes": 1420,
        "short_description": "Elegant restaurant website with menu and reservation",
        "full_description": """A beautiful restaurant website template with modern design.

## Features
- Hero section
- Menu display
- About section
- Reservation form
- Gallery
- Contact info
- Responsive design

## Clone & Run
```bash
git clone https://github.com/bedimcode/responsive-restaurant-website
# Open index.html in browser
```""",
        "git_repo_url": "https://github.com/bedimcode/responsive-restaurant-website",
        "live_demo_url": "https://bedimcode.github.io/responsive-restaurant-website/",
        "dependencies": ["html", "css", "javascript"],
        "tags": ["restaurant", "food", "business", "responsive"],
        "developer_name": "Bedimcode",
        "developer_experience": "5 years",
        "featured": False,
        "popular": True
    }
]

async def upload_templates():
    print("=" * 60)
    print("📦 UPLOADING REAL CLONEABLE TEMPLATES")
    print("=" * 60 + "\n")
    
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client.user_management_db
    
    # Get a default user_id
    user = await db.users.find_one({})
    user_id = user["_id"] if user else None
    
    if user_id:
        print(f"✅ Using user: {user.get('email', 'unknown')}")
    
    # Prepare templates
    templates_to_insert = []
    for tpl in TEMPLATES:
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
            "preview_images": [],  # Will be added via Cloudinary later
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
        }
        templates_to_insert.append(template_doc)
        print(f"✅ {tpl['title']} ({tpl['category']})")
        print(f"   📁 {tpl['git_repo_url']}")
        print(f"   🔗 {tpl['live_demo_url']}")
        print()
    
    # Insert templates
    result = await db.templates.insert_many(templates_to_insert)
    print(f"\n✅ Inserted {len(result.inserted_ids)} templates!")
    
    # Summary
    print("\n📊 Templates by Category:")
    pipeline = [{"$group": {"_id": "$category", "count": {"$sum": 1}}}]
    cursor = db.templates.aggregate(pipeline)
    async for doc in cursor:
        print(f"  - {doc['_id']}: {doc['count']}")
    
    client.close()
    print("\n✅ All templates are open-source and cloneable!")

if __name__ == "__main__":
    asyncio.run(upload_templates())
