"""
Upload curated website templates from GitHub to MongoDB.
These are real, high-quality templates with proper details.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from bson import ObjectId

# MongoDB connection - Docker local
DATABASE_URL = "mongodb://admin:password123@localhost:27017/user_management_db?authSource=admin"

# Curated list of real GitHub templates
GITHUB_TEMPLATES = [
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
        "full_description": """A beautiful free starter kit for Tailwind CSS. This kit features a landing page with hero section, features grid, testimonials, and pricing table. Perfect for SaaS products and startups.

## Features
- Responsive design
- Dark mode support
- Animations with Framer Motion
- SEO optimized
- Fast performance

## Tech Stack
- React 18
- Tailwind CSS 3
- Framer Motion""",
        "preview_images": ["https://raw.githubusercontent.com/creativetimofficial/tailwind-starter-kit/main/images/landing.jpg"],
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
        "title": "Next.js SaaS Starter",
        "category": "SaaS",
        "type": "Full Stack",
        "language": "TypeScript",
        "difficulty_level": "Advanced",
        "plan_type": "Free",
        "rating": 4.9,
        "downloads": 3200,
        "views": 12000,
        "likes": 750,
        "short_description": "Production-ready SaaS template with authentication, payments, and dashboard",
        "full_description": """A complete SaaS starter template built with Next.js 14, featuring authentication with NextAuth, payments with Stripe, and a beautiful dashboard.

## Features
- Next.js 14 App Router
- Prisma ORM with PostgreSQL
- Stripe integration
- NextAuth.js authentication
- Admin dashboard
- User management
- Email templates

## Perfect for
- SaaS applications
- Subscription-based products
- B2B platforms""",
        "preview_images": [],
        "git_repo_url": "https://github.com/vercel/nextjs-subscription-payments",
        "live_demo_url": "https://subscription-payments.vercel.app/",
        "dependencies": ["next", "typescript", "prisma", "stripe", "next-auth"],
        "tags": ["saas", "nextjs", "stripe", "authentication", "dashboard"],
        "developer_name": "Vercel",
        "developer_experience": "10 years",
        "featured": True,
        "popular": True
    },
    {
        "title": "Developer Portfolio",
        "category": "Portfolio",
        "type": "Static Site",
        "language": "JavaScript",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.7,
        "downloads": 8500,
        "views": 25000,
        "likes": 1200,
        "short_description": "Clean and modern portfolio template for developers",
        "full_description": """A sleek, minimalist portfolio template designed specifically for developers and designers. Features project showcase, skills section, and contact form.

## Features
- Clean, modern design
- Project gallery with filtering
- Skills section with progress bars
- Contact form integration
- Blog support
- Responsive design

## Customization
Easy to customize colors, fonts, and content through simple configuration.""",
        "preview_images": [],
        "git_repo_url": "https://github.com/ashutosh1919/masterPortfolio",
        "live_demo_url": "https://ashutosh1919.github.io/masterPortfolio/",
        "dependencies": ["react", "sass", "lottie-web"],
        "tags": ["portfolio", "developer", "personal", "showcase", "minimal"],
        "developer_name": "Ashutosh Hathidara",
        "developer_experience": "5 years",
        "featured": True,
        "popular": False
    },
    {
        "title": "Admin Dashboard Pro",
        "category": "Dashboard",
        "type": "React Component",
        "language": "TypeScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "rating": 4.8,
        "downloads": 6700,
        "views": 18000,
        "likes": 980,
        "short_description": "Modern React admin dashboard with charts, tables, and dark mode",
        "full_description": """A feature-rich admin dashboard template built with React and TypeScript. Includes data visualization, tables, forms, and multiple page layouts.

## Features
- 50+ UI components
- 10+ page templates
- Chart.js integration
- Data tables with sorting/filtering
- Dark/light mode
- RTL support
- Responsive sidebar

## Use Cases
- Admin panels
- CRM systems
- Analytics dashboards
- E-commerce backends""",
        "preview_images": [],
        "git_repo_url": "https://github.com/cruip/tailwind-dashboard-template",
        "live_demo_url": "https://mosaic.cruip.com/",
        "dependencies": ["react", "typescript", "tailwindcss", "chart.js"],
        "tags": ["dashboard", "admin", "charts", "tables", "dark-mode"],
        "developer_name": "Cruip",
        "developer_experience": "7 years",
        "featured": True,
        "popular": True
    },
    {
        "title": "E-commerce Store Template",
        "category": "E-commerce",
        "type": "Next.js Template",
        "language": "TypeScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "rating": 4.6,
        "downloads": 4500,
        "views": 14000,
        "likes": 650,
        "short_description": "Complete e-commerce storefront with cart, checkout, and product pages",
        "full_description": """A modern e-commerce template built with Next.js and headless CMS. Features product listings, cart functionality, and checkout flow.

## Features
- Product catalog with categories
- Shopping cart
- Checkout process
- User accounts
- Order history
- Search functionality
- Wishlist

## Integrations
- Stripe payments
- Contentful CMS
- SendGrid emails""",
        "preview_images": [],
        "git_repo_url": "https://github.com/vercel/commerce",
        "live_demo_url": "https://demo.vercel.store/",
        "dependencies": ["next", "typescript", "tailwindcss", "stripe"],
        "tags": ["ecommerce", "store", "shop", "cart", "checkout"],
        "developer_name": "Vercel",
        "developer_experience": "10 years",
        "featured": False,
        "popular": True
    },
    {
        "title": "Blog Platform",
        "category": "Blog",
        "type": "Next.js Template",
        "language": "TypeScript",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.7,
        "downloads": 7200,
        "views": 20000,
        "likes": 890,
        "short_description": "Modern blog template with MDX support and syntax highlighting",
        "full_description": """A beautiful blog template with MDX support, perfect for technical blogs and documentation sites. Features syntax highlighting, dark mode, and SEO optimization.

## Features
- MDX support
- Code syntax highlighting
- Table of contents
- Reading time
- Categories and tags
- RSS feed
- SEO optimized
- Dark mode

## Perfect for
- Technical blogs
- Documentation
- Personal blogs""",
        "preview_images": [],
        "git_repo_url": "https://github.com/timlrx/tailwind-nextjs-starter-blog",
        "live_demo_url": "https://tailwind-nextjs-starter-blog.vercel.app/",
        "dependencies": ["next", "mdx", "tailwindcss", "contentlayer"],
        "tags": ["blog", "mdx", "technical", "documentation", "seo"],
        "developer_name": "Timothy Lin",
        "developer_experience": "6 years",
        "featured": False,
        "popular": True
    },
    {
        "title": "Startup Landing Page",
        "category": "Landing Page",
        "type": "Static Site",
        "language": "JavaScript",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.5,
        "downloads": 9800,
        "views": 28000,
        "likes": 1450,
        "short_description": "Beautiful startup landing page with animations and modern design",
        "full_description": """A stunning landing page template designed for startups and SaaS products. Features smooth animations, pricing section, and testimonials.

## Sections
- Hero with CTA
- Features grid
- How it works
- Testimonials
- Pricing table
- FAQ accordion
- Newsletter signup
- Footer

## Design
- Modern gradients
- Smooth scroll
- Animated elements
- Mobile responsive""",
        "preview_images": [],
        "git_repo_url": "https://github.com/cruip/open-react-template",
        "live_demo_url": "https://open.cruip.com/",
        "dependencies": ["react", "tailwindcss", "aos"],
        "tags": ["startup", "landing", "saas", "animations", "modern"],
        "developer_name": "Cruip",
        "developer_experience": "7 years",
        "featured": True,
        "popular": True
    },
    {
        "title": "Medical Clinic Website",
        "category": "Business",
        "type": "HTML Template",
        "language": "HTML/CSS",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.4,
        "downloads": 3400,
        "views": 9500,
        "likes": 420,
        "short_description": "Professional medical and healthcare website template",
        "full_description": """A professional website template designed for medical clinics, hospitals, and healthcare providers. Clean design with appointment booking section.

## Pages
- Home page
- About us
- Services
- Doctors/Team
- Appointment booking
- Contact

## Features
- Appointment form
- Doctor profiles
- Service listings
- Testimonials
- Google Maps integration""",
        "preview_images": [],
        "git_repo_url": "https://github.com/themefisher/flavor-starter",
        "live_demo_url": "https://demo.themefisher.com/flavor/",
        "dependencies": ["bootstrap", "jquery"],
        "tags": ["medical", "healthcare", "clinic", "business", "professional"],
        "developer_name": "Themefisher",
        "developer_experience": "9 years",
        "featured": False,
        "popular": False
    },
    {
        "title": "Restaurant Website",
        "category": "Business",
        "type": "HTML Template",
        "language": "HTML/CSS",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.6,
        "downloads": 5600,
        "views": 16000,
        "likes": 780,
        "short_description": "Elegant restaurant template with menu and reservation features",
        "full_description": """An elegant and appetizing restaurant website template. Features beautiful food photography layouts, menu sections, and reservation system.

## Features
- Menu display with categories
- Reservation form
- Gallery/Photos
- Chef profiles
- Customer reviews
- Location map
- Opening hours
- Social media integration""",
        "preview_images": [],
        "git_repo_url": "https://github.com/bedimcode/responsive-restaurant-website",
        "live_demo_url": "https://bedimcode.github.io/responsive-restaurant-website/",
        "dependencies": ["scrollreveal", "swiper"],
        "tags": ["restaurant", "food", "menu", "reservation", "elegant"],
        "developer_name": "Bedimcode",
        "developer_experience": "5 years",
        "featured": False,
        "popular": True
    },
    {
        "title": "Agency Portfolio",
        "category": "Portfolio",
        "type": "React Component",
        "language": "JavaScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "rating": 4.7,
        "downloads": 4100,
        "views": 11500,
        "likes": 560,
        "short_description": "Creative agency portfolio with case studies and team section",
        "full_description": """A creative portfolio template for digital agencies and creative studios. Showcase your work, team, and services with style.

## Sections
- Hero with video background
- Services overview
- Case studies/Portfolio
- Team members
- Client logos
- Testimonials
- Contact form

## Animations
- Parallax scrolling
- Fade-in effects
- Hover interactions
- Page transitions""",
        "preview_images": [],
        "git_repo_url": "https://github.com/issaafalkattan/developer-portfolio",
        "live_demo_url": "https://developer-portfolio-1hzq.vercel.app/",
        "dependencies": ["react", "framer-motion", "tailwindcss"],
        "tags": ["agency", "portfolio", "creative", "case-study", "animations"],
        "developer_name": "Issaaf Kattan",
        "developer_experience": "6 years",
        "featured": False,
        "popular": False
    }
]

async def upload_templates():
    print("=" * 60)
    print("📦 UPLOADING GITHUB TEMPLATES TO DATABASE")
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
    for tpl in GITHUB_TEMPLATES:
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
            "preview_images": tpl.get("preview_images", []),
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
    
    # Insert templates
    print(f"\n🔄 Inserting {len(templates_to_insert)} templates...")
    
    result = await db.templates.insert_many(templates_to_insert)
    print(f"✅ Inserted {len(result.inserted_ids)} templates successfully!")
    
    # Show summary
    print("\n📋 Uploaded Templates:")
    for tpl in GITHUB_TEMPLATES:
        featured = "⭐" if tpl["featured"] else ""
        print(f"  {featured} {tpl['title']} ({tpl['category']})")
    
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

if __name__ == "__main__":
    asyncio.run(upload_templates())
