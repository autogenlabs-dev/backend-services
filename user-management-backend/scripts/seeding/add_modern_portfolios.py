"""
Script to add modern, smooth portfolio website templates similar to Giats Portfolio.
Includes capturing screenshots for each template.
"""

import asyncio
from playwright.async_api import async_playwright
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path
from bson import ObjectId
from datetime import datetime

# Load .env file
load_dotenv()

# MongoDB connection
MONGODB_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017/user_management_db")

# Screenshot output directory
SCREENSHOTS_DIR = Path("/home/cis/Music/Autogenlabs-Web-App/public/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Modern portfolio templates to add
MODERN_PORTFOLIOS = [
    {
        "title": "Brittany Chiang Portfolio v4",
        "short_description": "Award-winning Gatsby portfolio with slick dark theme, subtle hover effects, and smooth animations. Awwwards One Page Website Award 2019.",
        "description": "A beautifully crafted personal portfolio website built with Gatsby. Features a dark color scheme, smooth scroll animations, hover effects, and a clean, minimal design. Won the Awwwards One Page Website Award. Over 6,000+ GitHub stars.",
        "live_demo_url": "https://v4.brittanychiang.com",
        "git_repo_url": "https://github.com/bchiang7/v4",
        "category": "Portfolio",
        "type": "Gatsby",
        "language": "React",
        "difficulty_level": "Medium",
        "technologies": ["React", "Gatsby", "Styled Components", "GSAP"],
        "tags": ["portfolio", "dark theme", "awwwards", "gatsby", "animations"],
        "featured": True,
        "popular": True,
    },
    {
        "title": "Denis Snellenberg Portfolio",
        "short_description": "Award-winning freelance designer portfolio with smooth transitions, micro animations, and hidden menu interactions. Awwwards Site of the Day 2022.",
        "description": "A stunning portfolio website by freelance designer Denis Snellenberg. Features beautiful UI design, matched colors, animated hero section, hidden menu with smooth transitions, and exceptional micro-interactions.",
        "live_demo_url": "https://dennissnellenberg.com",
        "git_repo_url": "https://github.com/dennissnellenberg/dennissnellenberg-portfolio",
        "category": "Portfolio",
        "type": "Next.js",
        "language": "React",
        "difficulty_level": "Tough",
        "technologies": ["React", "Next.js", "GSAP", "Framer Motion"],
        "tags": ["portfolio", "awwwards", "animations", "designer", "premium"],
        "featured": True,
        "popular": True,
    },
    {
        "title": "Tamal Sen Developer Portfolio",
        "short_description": "Modern developer portfolio with IDE-inspired dark theme, code aesthetics, and clean project showcase.",
        "description": "A software engineer portfolio with strong developer aesthetic. Features dark theme reminiscent of an IDE, code-style backgrounds, and effective project screenshots display.",
        "live_demo_url": "https://tamalsen.dev",
        "git_repo_url": "https://github.com/tamal-sen/portfolio",
        "category": "Portfolio",
        "type": "React",
        "language": "JavaScript",
        "difficulty_level": "Medium",
        "technologies": ["React", "JavaScript", "CSS3"],
        "tags": ["portfolio", "developer", "dark theme", "minimal"],
        "featured": False,
        "popular": True,
    },
    {
        "title": "Adrian Hajdin 3D Portfolio",
        "short_description": "Visually captivating 3D portfolio with interactive hero section, Framer Motion animations, and React Three Fiber graphics.",
        "description": "Build a visually captivating 3D portfolio with React.js and Three.js. Features a customizable 3D hero section, interactive work sections with Framer Motion animations, a 3D skills section, and animated projects.",
        "live_demo_url": "https://jsmastery.pro",
        "git_repo_url": "https://github.com/adrianhajdin/3d-portfolio",
        "category": "Portfolio",
        "type": "React",
        "language": "JavaScript",
        "difficulty_level": "Tough",
        "technologies": ["React", "Three.js", "React Three Fiber", "Framer Motion", "Tailwind CSS"],
        "tags": ["portfolio", "3D", "threejs", "animations", "interactive"],
        "featured": True,
        "popular": True,
    },
    {
        "title": "Sanidhyy Modern 3D Portfolio",
        "short_description": "Modern 3D Portfolio using React, Three.js and TypeScript with immersive 3D graphics and smooth animations.",
        "description": "A contemporary 3D portfolio template built with React, Three.js and TypeScript. Features strong type-checking, immersive 3D elements, and a modern design approach.",
        "live_demo_url": "https://itsvaibhavcoder.vercel.app",
        "git_repo_url": "https://github.com/sanidhyy/3d-portfolio",
        "category": "Portfolio",
        "type": "React",
        "language": "TypeScript",
        "difficulty_level": "Medium",
        "technologies": ["React", "Three.js", "TypeScript", "React Three Fiber"],
        "tags": ["portfolio", "3D", "typescript", "modern"],
        "featured": False,
        "popular": True,
    },
    {
        "title": "3D Game-like Portfolio",
        "short_description": "Unique 3D game-like portfolio with character movements, interactive elements, and Blender 3D models.",
        "description": "An innovative 3D portfolio featuring game-like interactions with character movements and interactive elements. Built with Three.js, React, and Blender models using React-Three-Fiber.",
        "live_demo_url": "https://vinaymatta-portfolio.web.app",
        "git_repo_url": "https://github.com/VinayMatta63/threejs-portfolio",
        "category": "Portfolio",
        "type": "React",
        "language": "JavaScript",
        "difficulty_level": "Tough",
        "technologies": ["React", "Three.js", "React Three Fiber", "Blender", "Firebase"],
        "tags": ["portfolio", "3D", "game", "interactive", "blender"],
        "featured": True,
        "popular": True,
    },
    {
        "title": "Ladunjexa React 3D Portfolio",
        "short_description": "Black and purple themed portfolio with cool design elements, 3D modeling, and clearly divided structure.",
        "description": "A stylish React portfolio template with black and purple color scheme, cool design elements, 3D modeling sections, and a well-organized structure for showcasing projects and skills.",
        "live_demo_url": "https://ladunjexa-portfolio.vercel.app",
        "git_repo_url": "https://github.com/ladunjexa/reactjs18-3d-portfolio",
        "category": "Portfolio",
        "type": "React",
        "language": "JavaScript",
        "difficulty_level": "Medium",
        "technologies": ["React", "Three.js", "Tailwind CSS", "Framer Motion"],
        "tags": ["portfolio", "3D", "dark theme", "purple", "modern"],
        "featured": False,
        "popular": True,
    },
    {
        "title": "3D React Island Portfolio",
        "short_description": "Portfolio with dynamic 3D island in hero section, engaging animations, and modern design using React and Three.js.",
        "description": "A creative 3D portfolio website featuring a dynamic 3D island in the hero section. Built with React.js, Tailwind CSS, and Three.js for an engaging and interactive user experience.",
        "live_demo_url": "https://3d-react-portfolio-22.vercel.app",
        "git_repo_url": "https://github.com/GourangaDasSamrat/3d-react-portfolio-2",
        "category": "Portfolio",
        "type": "React",
        "language": "JavaScript",
        "difficulty_level": "Medium",
        "technologies": ["React", "Three.js", "Tailwind CSS", "Vite"],
        "tags": ["portfolio", "3D", "island", "animations", "interactive"],
        "featured": False,
        "popular": True,
    },
]

async def capture_screenshot(page, url, filename):
    """Capture a screenshot of a website."""
    try:
        print(f"  📸 Capturing: {url}")
        await page.goto(url, wait_until='networkidle', timeout=45000)
        await asyncio.sleep(3)  # Wait for animations
        
        screenshot_path = SCREENSHOTS_DIR / filename
        await page.screenshot(path=str(screenshot_path), full_page=False)
        
        print(f"  ✅ Saved: {filename}")
        return f"/screenshots/{filename}"
    except Exception as e:
        print(f"  ❌ Failed: {url} - {str(e)[:60]}")
        return None

async def add_modern_portfolios():
    """Add modern portfolio templates with screenshots."""
    
    print("🔌 Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_default_database()
    templates_collection = db.templates
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            device_scale_factor=1
        )
        page = await context.new_page()
        
        added_count = 0
        for template_data in MODERN_PORTFOLIOS:
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
                # Create template document
                template_doc = {
                    "_id": template_id,
                    "title": template_data["title"],
                    "short_description": template_data["short_description"],
                    "description": template_data["description"],
                    "live_demo_url": template_data["live_demo_url"],
                    "git_repo_url": template_data["git_repo_url"],
                    "category": template_data["category"],
                    "type": template_data["type"],
                    "language": template_data["language"],
                    "difficulty_level": template_data["difficulty_level"],
                    "technologies": template_data["technologies"],
                    "tags": template_data["tags"],
                    "featured": template_data["featured"],
                    "popular": template_data["popular"],
                    "preview_images": [screenshot_url],
                    "rating": 4.8,
                    "total_ratings": 0,
                    "views": 0,
                    "downloads": 0,
                    "likes": 0,
                    "plan_type": "Free",
                    "is_active": True,
                    "developer_name": "Community",
                    "developer_experience": 5,
                    "is_available_for_dev": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
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
    asyncio.run(add_modern_portfolios())
    print("\n🎉 Done!")
